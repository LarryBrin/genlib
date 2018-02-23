import os
import os.path
import sqlite3
from time import sleep
from urllib.parse import urljoin

from lxml.html import fromstring
from requests import Session
from selenium import webdriver

LANGUAGES = ['php', 'python', 'java', 'javascript', 'ruby']
HOST = 'http://gen.lib.rus.ec/'
RAW_URL = 'http://gen.lib.rus.ec/search.php?req={lang}&open=0&res=100&view=simple&phrase=0&column=title'
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU iPhone OS 11_0 like Mac OS X) \
           AppleWebKit/604.1.38 (KHTML, like Gecko) \
           Version/11.0 Mobile/15A372 Safari/604.1'}


def get_first_page_source(url, language):
    """Because the page iterable urls can't get by requests, it may be
    generated by Ajax or javascript, so selenium is the right chioce."""
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    driver.implicitly_wait(2.0)
    source = driver.page_source
    with open('./{}/1.html'.format(language), 'w') as f:
        f.writelines(source)
    driver.quit()
    return source


def get_raw_iter_url(root):
    raw_iter_url = root.xpath('//div/table//tr[1]//a[1]/@href')[0]
    raw_iter_url = urljoin(HOST, raw_iter_url)
    # print('raw_iter_url: ', raw_iter_url)
    return raw_iter_url


def iter_crawler(raw_iter_url, language):
    # print('\niter_crawler-langage: {}\n'.format(language))
    global one_language_competed
    page_number = 2
    i = 1
    while True:
        if one_language_competed:
            one_language_competed = False
            break
        else:
            iter_url = raw_iter_url[:-1] + str(page_number)
            print('\n{:<6}iter_url: {}\n'.format(i, iter_url))
            response = get_rest_pages(iter_url)
            with open('./{}/{}.html'.format(language, page_number), 'w') as f:
                f.writelines(response.text)
            root = fromstring(response.text)
            get_book_items(root, language)
            page_number += 1
            i += 1
            print('-----------------------sleep 1.2s----------------------')
            sleep(1.2)


def get_rest_pages(iter_url):
    session = Session()
    response = session.get(iter_url, headers=HEADERS)
    return response


def get_book_items(root, language):
    global one_language_competed, HOST
    one_language_competed = False
    book_items = []
    items = root.xpath('//table[3]//tr[position()>1]')
    i = 1
    for item in items:
        if item.xpath('./td[3]/a/text()[1]'):
            title = item.xpath('./td[3]/a/text()[1]')[0]
        else:
            title = 'Unknown title'
        if item.xpath('./td[3]/a/@href')[0]:
            title_link = item.xpath('./td[3]/a/@href')[0]
            title_link = urljoin(HOST, title_link)
        else:
            title_link = 'Something error'
        if item.xpath('./td[4]/text()'):
            publisher = item.xpath('./td[4]/text()')[0]
        else:
            publisher = ''
        if item.xpath('./td[5]/text()'):
            year = item.xpath('./td[5]/text()')[0]
        else:
            year = ''
        if item.xpath('./td[7]/text()'):
            book_language = item.xpath('./td[7]/text()')[0]
        else:
            book_language = 'Unkown language'

        # print('%d: ' % i, title, title_link, publisher, year, book_language)
        # i += 1
        book_item = language, title, title_link, publisher, year, book_language

        book_items.append(book_item)
    book_items = tuple(book_items)
    print('length: {}'.format(len(book_items)))
    if len(book_items) < 100:
        one_language_competed = True
        return
    elif get_last_stored_book_info():
        last_stored_book_info = get_last_stored_book_info()
        try:
            print('\nbook_items[-1]:{}'.format(book_items[-1]))
            print('last_stored_book_info: {}\n'.format(last_stored_book_info))
            if book_items[-1] == last_stored_book_info:
                one_language_competed = True
                return
        except IndexError:
            # one_language_competed = True
            print('IndexError')
    if not one_language_competed:
        store_book_infos(book_items, language)


def store_book_infos(book_items, language):
    conn = sqlite3.connect('genlib.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Book_infos (
                ID INTEGER PRIMARY KEY AUTOINCREMENT, programing_lang TEXT,
                title TEXT, url TEXT, publisher TEXT, year TEXT, language TEXT)''')
    cur.executemany('''INSERT INTO Book_infos (programing_lang, title, url, publisher,
                    year, language) VALUES (?, ?, ?, ?, ?, ?)''', book_items)
    conn.commit()


def get_last_stored_book_info():
    conn = sqlite3.connect('genlib.db')
    cur = conn.cursor()
    # lastid = cur.lastrowid
    try:
        cur.execute('''SELECT * FROM Book_infos WHERE ID=(SELECT MAX(ID)
                    FROM Book_infos)''')
        last_stored_book_info = cur.fetchone()[1:]
        return last_stored_book_info
    except Exception:
        None


def judge_language_not_stored(language):
    languages = ('php', 'python', 'java', 'javascript', 'ruby')
    conn = sqlite3.connect('genlib.db')
    cur = conn.cursor()
    try:
        cur.execute('''SELECT programing_lang FROM Book_infos''')
        raw_stored_language = set(cur.fetchall())
        stored_language = []
        for item in raw_stored_language:
            stored_language.append(item[0])
        # print('stored_language: {}'.format(stored_language))
        print('stored_language: {}'.format(stored_language))
        if language not in stored_language:
            return language
    except Exception:
        return languages[0]


if __name__ == '__main__':
    for language in LANGUAGES:
        if judge_language_not_stored(language):
            language = judge_language_not_stored(language)
            dirname = os.path.join(os.getcwd(), language + '/')
            if not os.path.exists(dirname):
                os.makedirs(language)
            url = RAW_URL.format(lang=language)
            first_page_source = get_first_page_source(url, language)
            root = fromstring(first_page_source)
            get_book_items(root, language)
            raw_iter_url = get_raw_iter_url(root)
            iter_crawler(raw_iter_url, language)