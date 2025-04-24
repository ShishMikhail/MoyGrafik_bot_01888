import pandas as pd
from sqlalchemy import create_engine, text
from database.db import engine 
def load_and_update_table(csv_file, table_name, key_columns):
    """
    Загрузка данных из CSV и обновление таблицы в БД.
    :param csv_file: Путь к файлу CSV.
    :param table_name: Название таблицы в БД.
    :param key_columns: Список названий ключевых (уникальных) столбцов для обновления.
    """
    # Загрузка данных из CSV в DataFrame
    df = pd.read_csv(csv_file)

    # Подключение к БД
    with engine.connect() as connection:
        # Проверка наличия таблицы
        result = connection.execute(text(
            f"SELECT * FROM information_schema.tables WHERE table_schema = 'main' AND table_name = '{table_name}';"))
        if not result.rowcount:
            print(f"Таблица {table_name} не найдена в схеме main.")
            return

        # Временная таблица
        temp_table_name = f"{table_name}_temp"
        df.to_sql(temp_table_name, connection, schema='main', if_exists='replace', index=False)

        # Составляем SQL для добавления и обновления данных
        update_set = ', '.join([f"{col} = excluded.{col}" for col in df.columns if col not in key_columns])
        conflict_target = ', '.join(key_columns)

        insert_query = f"""
        INSERT INTO main.{table_name} ({', '.join(df.columns)}) 
        SELECT {', '.join(df.columns)} FROM main.{temp_table_name}
        ON CONFLICT ({conflict_target}) DO UPDATE SET {update_set};
        """
        connection.execute(text(insert_query))

        # Удаляем временную таблицу
        connection.execute(text(f"DROP TABLE IF EXISTS main.{temp_table_name};"))
        print(f"Данные из {csv_file} обновлены в таблице {table_name}.")


# Пути к файлам CSV и настройки таблиц
tables_info = [
    {'csv_file': 'employees.csv', 'table_name': 'employees', 'key_columns': ['id']},
    {'csv_file': 'placements.csv', 'table_name': 'placements', 'key_columns': ['id']},
    {'csv_file': 'positions.csv', 'table_name': 'positions', 'key_columns': ['id']},
    {'csv_file': 'presence_report.csv', 'table_name': 'presence_report', 'key_columns': ['employee_id', 'date']},
    {'csv_file': 'subdivisions.csv', 'table_name': 'subdivisions', 'key_columns': ['id']}
]

# Загрузка и обновление данных для каждой таблицы
for info in tables_info:
    load_and_update_table(info['csv_file'], info['table_name'], info['key_columns'])