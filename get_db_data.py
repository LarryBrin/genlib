import sqlite3
import pprint
import json

LANGUAGES = ['python', 'php', 'javascript', 'java', 'ruby']
conn = sqlite3.connect('genlib.db')

conn.row_factory = sqlite3.Row

cur = conn.cursor()

total_language_info = {}
data = cur.fetchall()
with open('total_language_info.json', 'w+') as js:
    for language in LANGUAGES:
        print(language)
        cur.execute('SELECT * FROM Book_infos WHERE programing_lang=%s', language)
        total_language_info[language] = {}
        for datum in data:
            i = total_language_info[language]
            id = datum['ID']
            # programing_lang = datum['programing_lang']
            title = datum['title']
            url = datum['url']
            publisher = datum['publisher']
            year = datum['year']
            book_language = datum['language']
            # i['ID'] = id
            # i['programing_lang'] = programing_lang
            i['title'] = title
            i['publisher'] = publisher
            i['url'] = url
            i['year'] = year
            i['book_language'] = book_language
            js.write(i)
    print(total_language_info)

print(php)
