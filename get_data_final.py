import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select

LANGUAGES = ['python', 'php', 'javascript', 'java', 'ruby']

engine = create_engine('sqlite:///genlib.db')
connection = engine.connect()
metadata = MetaData(engine, reflect=True)
book_infos_table = metadata.tables['Book_infos']


def get_data_from_db(language):
    selection = book_infos_table.select().where(
            book_infos_table.c.programing_lang == language)
    result_proxy = connection.execute(selection)
    infos = result_proxy.fetchall()
    column_name = result_proxy.keys()
    return infos, column_name
    # column_name = result_proxy.keys()


def get_all_book_infos(LANGUAGES):
    book_infos = {}
    for language in LANGUAGES:
        book_infos[language] = {}
        results = get_data_from_db(language)
        infos = results[0]
        column_name = results[1]
        for item in infos:
            if len(item.year) < 4 or len(item.language) == 0:
                continue
            # print(item)
            book_infos[language][item.ID] = {}
            book = book_infos[language][item.ID]
            book[column_name[2]] = item.title.lower().strip()
            book[column_name[5]] = item.year.strip()
            book[column_name[6]] = \
                    item.language.lower().strip()
    return book_infos


def preprocess_data(data):
    processed_data = {}
    year_count = {}
    for language in LANGUAGES:
        # get all books in one language
        processed_data[language] = set()
        year_count[language] = {}
        year_count_medimum = year_count[language]
        medimum = processed_data[language]
        books_in_one_language = data[language]
        for item in books_in_one_language:
            item = books_in_one_language[item]
            # print(item)
            if ':' in item['title']:
                item['title'] = item['title'][:item['title'].index(':')].strip()
            if '+' in item['title']:
                item['title'] = item['title'][:item['title'].index('+')].strip()
            if ',' in item['title']:
                item['title'] = item['title'][:item['title'].index(',')].strip()
            if ' - ' in item['title']:
                item['title'] = item['title'][:item['title'].index(' - ')].strip()
            if '(' in item['title']:
                item['title'] = item['title'][:item['title'].index('(')].strip()
            if len(item['year']) > 4:
                item['year'] = item['year'].split(' ')[-1][:4]
            book_info = (item['year'], item['title'],
                        item['language'],)
            # print(book_info)
            medimum.add(book_info)
        # medimum_list = list(medimum)
        # medimum_list.sort(key=lambda x: x[0])
        # year_count = {}
        for item in medimum:
            if item[0] not in year_count_medimum:
                year_count_medimum[item[0]] = 0
            if item[0] in item:
                year_count_medimum[item[0]] += 1
    # print(year_count)
    return processed_data, year_count


def generate_books_json_file(data):
    with open('data.json', 'w+', encoding='utf-8') as f:
        for items in data[0].items():
            for item in items:
                if len(item) < 10:
                    f.writelines(json.dumps(item) + '\n')
                else:
                    for i in item:
                        f.writelines(json.dumps(i) + '\n')


def generate_year_count_json_file(data):
    with open('year_count.json', 'w+', encoding='utf-8') as f:
        data = data[1]
        year_count_dict = {}
        for language in data:
            year_count = data[language].items()
            year_count = list(year_count)
            year_count.sort(key=lambda x: x[0])
            year_count_dict[language] = year_count
        f.write(json.dumps(year_count_dict) + '\n')


if __name__ == '__main__':
    data = get_all_book_infos(LANGUAGES)
    data = preprocess_data(data)
    generate_books_json_file(data)
    generate_year_count_json_file(data)
