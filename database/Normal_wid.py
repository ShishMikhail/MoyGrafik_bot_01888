from datetime import datetime
from pathlib import Path
import pandas as pd
import ast


def clean_and_normalize_data(file_path, table_structure):
    df = pd.read_csv(file_path)
    df = df.where(pd.notnull(df), None)

    print(f"До нормализации данных в {file_path.name}:")
    print(df.head(3))  # Вывод первых 3 строк до нормализации

    def clean_and_convert(value, expected_type=None):
        if value is None or value == '':
            return None
        if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return None
        if expected_type == datetime:
            try:
                return pd.to_datetime(value)
            except (ValueError, TypeError):
                return None
        try:
            if expected_type:
                return expected_type(value)
        except (ValueError, TypeError):
            return None
        return value

    for column, expected_type in table_structure.items():
        if column in df.columns:
            df[column] = df[column].apply(lambda x: clean_and_convert(x, expected_type))

    print(f"После нормализации данных в {file_path.name}:")
    print(df.head(3))  # Вывод первых 3 строк после нормализации

    df.to_csv(file_path, index=False)
    print(f"Данные в {file_path.name} были успешно нормализованы.\n")


def main():
    data_path = Path("C:\\Users\\shish.me\\PycharmProjects\\MoyGrafik_bot\\database")

    csv_files = {
        'employees.csv': {
            'id': int,
            'user_id': int,
            'company_id': int,
            'timezone_id': int,
            'first_name': str,
            'last_name': str,
            'snils': str,
            'clid': str,
            'telegram_id': int,
            'presence_close_rule': int,
            'email': str,
            'phone': str,
            'avatar': str,
            'avatar_big': str,
            'placements': list,
            'sites': list,
            'subdivisions': list,
            'positions': list,
            'identification_photos': str,
            'identification_photos_count': int,
            'preferred_photo': str
        },
        'placements.csv': {
            'id': int,
            'company_id': int,
            'timezone_id': int,
            'name': str,
            'clid': str,
            'color': str,
            'color_id': int,
            'status': int,
            'terminal_monitoring_enabled': bool,
            'location_control': float,
            'liveness_enabled': bool,
            'ips': list,
            'mac_addresses': list,
            'managers': list
        },
        'subdivisions.csv': {
            'id': int,
            'company_id': int,
            'name': str,
            'clid': str,
            'color': str,
            'color_id': int,
            'status': int,
            'managers': list,
            'placements': list
        },
        'positions.csv': {
            'id': int,
            'company_id': int,
            'name': str,
            'clid': str,
            'color': str,
            'color_id': int,
            'status': int,
            'managers': list,
            'subdivisions': list
        },
        'presence_report.csv': {
            'date': datetime,
            'start_time': datetime,
            'end_time': datetime,
            'is_night_shift': bool,
            'original_estimate': int,
            'real_estimate': int,
            'is_red': bool,
            'employee_id': int,
            'first_name': str,
            'last_name': str,
            'email': str
        }
    }

    for file_name, table_structure in csv_files.items():
        file_path = data_path / file_name
        if file_path.exists():
            clean_and_normalize_data(file_path, table_structure)
        else:
            print(f"Файл {file_name} не найден.")


if __name__ == "__main__":
    main()