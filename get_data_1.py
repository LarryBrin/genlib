import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select


engine = create_engine('sqlite:///genlib.db')
conn = engine.connect()
metadate = MetaData(engine)
metadate.reflect()
table = metadate.tables['Book_infos']
LANGUAGES = ['python', 'php', 'javascript', 'java', 'ruby']
# if not use encoding, the write() method will be failed.
with open('total_language_info.json', 'w+', encoding='utf-8') as f:
    # f.write()
    info = {}
    final_list = {}
    for language in LANGUAGES:
        final_list[language] = []
        info[language] = {}
        s = table.select().where(table.c.programing_lang == language)
        # str(s)
        rp = conn.execute(s)
        key = rp.keys()
        # print(key)
        results = rp.fetchall()
        for item in results:
            # print(item.title)
            # book_name = item.title
            # print(type(book_name))
            # book_name = book_name.lower()
            info[language][item.ID] = {}
            book = info[language][item.ID]
            # book = info[language]
            book[key[2]] = item.title.lower().strip()
            book[key[3]] = item.url.strip()
            book[key[4]] = item.publisher.lower().strip()
            book[key[5]] = item.year.strip()
            book[key[6]] = item.language.lower().strip()
            # print(book)
            # print(type(item))
            # for i in item:
                # print(type(i))
                # f. write(str(i)+'\n')
    # final_list = {}
    # for language in LANGUAGES:
        # final_list[language] = []
    # final_list[language] = []
        for item in info[language].values():
            final_list[language].append((item['title'], item['year'],))
        # print(python_tuple)
        # len_list = len(python_tuple)
        # len_set = len(set(python_tuple))
        # print(len_set, '+', len_list)
        len_list = len(final_list[language])
        print('len_list: ', len_list)
        language_set = set(final_list[language])
        len_set = len(language_set)
        print('len_set: ', len_set)
        # print(language_set)
        final_list[language].sort(key=lambda x: x[0])
        # print(final_list[language])
        new_list = list(language_set)
        new_list.sort(key=lambda x: x[0])
        # print(new_list)
        processed_list = []
        for item in new_list:
            if language not in item[0]:
                continue
            elif len(item[1]) < 4:
                continue
            if ':' in item[0]:
                title = item[0][:item[0].index(':')].strip()
                year = item[1]
                item = (title, year,)
                # print(item)
            if '+' in item[0]:
                title = item[0][:item[0].index('+')].strip()
                year = item[1]
                item = (title, year,)
                # print(item)
            if ',' in item[0]:
                title = item[0][:item[0].index(',')].strip()
                year = item[1]
                item = (title, year,)
            if ' - ' in item[0]:
                title = item[0][:item[0].index(' - ')].strip()
                year = item[1]
                item = (title, year,)
            if '(' in item[0]:
                title = item[0][:item[0].index('(')].strip()
                year = item[1]
                item = (title, year,)
            # print(item[1])
            if len(item[1]) > 4:
                title = item[0]
                year = item[1][item[1].rindex(',')+1:].strip()
                item = (title, year,)
            print(item[1])
            processed_list.append(item)
            processed_set = set(processed_list)
            processed_list = list(processed_set)
            processed_list.sort(key=lambda x: x[0])
        for item in processed_list:
            f.writelines(json.dumps(item) + '\n')
