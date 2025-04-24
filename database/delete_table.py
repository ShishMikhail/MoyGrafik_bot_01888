from sqlalchemy import create_engine, text
from database.db import engine 

def drop_specified_tables(connection, tables):
    """
    Удаление указанных таблиц с зависимыми объектами.

    :param connection: Текущее соединение с базой данных.
    :param tables: Список таблиц для удаления.
    """
    for table in tables:
        # Удаление таблицы с каскадированием
        connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
        print(f"Table {table} deleted.")

# Список таблиц для удаления
tables_to_delete = [
    'employees',
    'placements',
    'positions',
    'presence_report',
    'subdivisions'
]

# Исполнение функции
with engine.begin() as connection:
    drop_specified_tables(connection, tables_to_delete)