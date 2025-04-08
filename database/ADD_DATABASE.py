import pandas as pd
import ast
from sqlalchemy import create_engine, text

# Установите соединение с базой данных
engine = create_engine('postgresql://postgres:WE010203ws@localhost:5432/postgres')

def evaluate_lists(col):
    """Convert string representations of lists to actual lists"""
    if pd.notnull(col) and isinstance(col, str) and col.startswith('[') and col.endswith(']'):
        try:
            return ast.literal_eval(col)
        except (SyntaxError, ValueError):
            pass
    return col

def prepare_sql_array(lst):
    """Convert a list to a PostgreSQL-compatible array string"""
    if isinstance(lst, list):
        return '{' + ','.join(map(str, lst)) + '}'
    return None if lst is None else lst

def load_csv_to_temp_table(file_path, temp_table_name):
    """Load CSV data into a temporary table"""
    df = pd.read_csv(file_path)

    # Convert string representations of lists to SQL array strings
    list_columns = {
        'employees': ['placements', 'sites', 'subdivisions', 'positions', 'identification_photos'],
        'placements': ['ips', 'mac_addresses', 'managers'],
        'positions': ['managers', 'subdivisions'],
        'subdivisions': ['managers', 'placements']
    }

    table_name = temp_table_name.replace('_temp', '')
    if table_name in list_columns:
        for col in list_columns[table_name]:
            if col in df.columns:
                df[col] = df[col].apply(evaluate_lists)
                df[col] = df[col].apply(prepare_sql_array)

    df = df.where(pd.notnull(df), None)
    df.to_sql(temp_table_name, engine, if_exists='replace', index=False)
    print(f"Data loaded into temporary table {temp_table_name}.")

def drop_and_replace_table(connection, table_name):
    """Delete and replace the table with fresh data"""
    connection.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
    print(f"Table {table_name} dropped.")
    connection.execute(text(f"ALTER TABLE {table_name}_temp RENAME TO {table_name};"))
    print(f"Table {table_name}_temp renamed to {table_name}.")

def process_table(file_path, table_name, conflict_columns, update_columns):
    """Process each table"""
    temp_table_name = f"{table_name}_temp"

    # Load data into temporary table
    load_csv_to_temp_table(file_path, temp_table_name)

    with engine.begin() as connection:
        drop_and_replace_table(connection, table_name)

# Paths to your CSV files
data_path = "C:\\Users\\shish.me\\PycharmProjects\\MoyGrafik_bot\\database"

# Settings for each table
tables_info = [
    {
        'file_path': f"{data_path}\\employees.csv",
        'table_name': 'employees',
        'conflict_columns': ['id'],
        'update_columns': [
            'id', 'user_id', 'company_id', 'timezone_id', 'first_name', 'last_name', 'snils', 'clid',
            'telegram_id', 'presence_close_rule', 'email', 'phone', 'avatar', 'avatar_big', 'placements',
            'sites', 'subdivisions', 'positions', 'identification_photos', 'identification_photos_count',
            'preferred_photo'
        ]
    },
    {
        'file_path': f"{data_path}\\placements.csv",
        'table_name': 'placements',
        'conflict_columns': ['id'],
        'update_columns': [
            'id', 'company_id', 'timezone_id', 'name', 'clid', 'color', 'color_id', 'status',
            'terminal_monitoring_enabled', 'location_control', 'liveness_enabled', 'ips',
            'mac_addresses', 'managers'
        ]
    },
    {
        'file_path': f"{data_path}\\positions.csv",
        'table_name': 'positions',
        'conflict_columns': ['id'],
        'update_columns': [
            'id', 'company_id', 'name', 'clid', 'color', 'color_id', 'status', 'managers', 'subdivisions'
        ]
    },
    {
        'file_path': f"{data_path}\\presence_report.csv",
        'table_name': 'presence_report',
        'conflict_columns': ['employee_id', 'date'],
        'update_columns': [
            'employee_id', 'date', 'start_time', 'end_time', 'is_night_shift', 'original_estimate', 'real_estimate',
            'is_red', 'first_name', 'last_name', 'email'
        ]
    },
    {
        'file_path': f"{data_path}\\subdivisions.csv",
        'table_name': 'subdivisions',
        'conflict_columns': ['id'],
        'update_columns': [
            'id', 'company_id', 'name', 'clid', 'color', 'color_id', 'status', 'managers', 'placements'
        ]
    },
]

# Process all tables
for info in tables_info:
    process_table(info['file_path'], info['table_name'], info['conflict_columns'], info['update_columns'])