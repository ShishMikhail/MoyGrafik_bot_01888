from sqlalchemy import create_engine, text
from database.db import engine 

def drop_all_tables(connection):
    """
    Удалить все таблицы, игнорируя связи между ними.
    """
    # Отключаем проверки целостности
    connection.execute(text("SET CONSTRAINTS ALL DEFERRED;"))

    # Получаем список всех таблиц
    result = connection.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    ))

    # Удаляем каждую таблицу
    for row in result:
        table_name = row[0]
        connection.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
        print(f"Table {table_name} deleted.")

# Исполнение функции
with engine.begin() as connection:
    drop_all_tables(connection)
