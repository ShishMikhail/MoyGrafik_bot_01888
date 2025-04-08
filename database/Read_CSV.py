import os
import pandas as pd
from pathlib import Path

def list_csv_columns_and_rows(data_directory):
    # Проверяем, существует ли директория
    data_dir = Path(data_directory)
    if not data_dir.exists():
        print(f"Каталог {data_directory} не существует.")
        return

    # Перебираем все файлы в директории
    for file_name in os.listdir(data_dir):
        # Проверяем, является ли файл CSV
        if file_name.endswith('.csv'):
            file_path = data_dir / file_name
            try:
                # Загрузка CSV-файла
                df = pd.read_csv(file_path)
                # Вывод названия файла и имен столбцов
                print(f"Файл: {file_name}")
                print("Столбцы:", list(df.columns))
                print("Первые две строки:")
                print(df.head(2))  # Вывод первых двух строк
                print()
            except Exception as e:
                print(f"Ошибка при чтении файла {file_name}: {e}")

# Заданный путь к каталогу
data_path = "C:\\Users\\shish.me\\PycharmProjects\\MoyGrafik_bot\\database"

# Вызов функции
list_csv_columns_and_rows(data_path)