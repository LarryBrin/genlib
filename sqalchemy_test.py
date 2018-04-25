from datetime import datetime

from sqlalchemy import (MetaData, Table, Column, Integer, Numeric, String,
                        DateTime, ForeignKey, Boolean, create_engine,
                        CheckConstraint)

metadata = MetaData()

cookies = Table('cookies', metadata,
                Column('cookie_id', Integer(), primary_key=True),
                Column('cookie_name', String(50), index=True),
                Column('cookie_recipe_url', String(255)),
                Column('cookie_sku', String(55)),
                Column('quantity', Integer()),
                Column('unit_cost', Numeric(12, 2)),
                CheckConstraint('quantity > 0', name='quantity_positive'))

users = Table('users', metadata,
            Column('user_id', Integer(), primary_key=True),
            Column('username', String(15), nullable=False, unique=True),
            Column('email_address', String(255), nullable=False),
            Column('phone', String(20), nullable=False),
            Column('password', String(20), nullable=False),
            Column('create_on', DateTime(), default=datetime.now),
            Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now))

orders = Table('orders', metadata,
            Column('order_id', Integer()),
            Column('user_id', ForeignKey('users.user_id')),
            Column('shipped', Boolean(), default=False))

line_items = Table('line_items', metadata,
            Column('line_items_id', Integer(), primary_key=True),
            Column('order_id', ForeignKey('orders.order_id')),
            Column('cookie_id', ForeignKey('cookies.cookie_id')),
            Column('quantity', Integer()),
            Column('extended_cost', Numeric(12, 2)))

engine = create_engine('sqlite:///:memory:')
metadata.create_all(engine)
connection = engine.connect()

from sqlalchemy import select, insert
s = select([users.c.username])
connection.execute(s).fetchall()

ins = insert(users).values(
        username='cookiemon',
        email_address='damon@cookie.com',
        phone='111-111-1111',
        password='password')
result = connection.execute(ins)

s = select([users.c.username])
results = connection.execute(s)
for result in results:
    print(result.username)
    # print(result.password)

s = select([users.c.username])
connection.execute(s).fetchall()

from sqlalchemy.exc import IntegrityError
ins = insert(users).values(
        username='cookiemon',
        email_address='damon@cookie.com',
        phone='111-111-1111',
        password='password')

try:
    result = connection.execute(ins)
except IntegrityError as error:
    print(error.orig.message)
