from sqlalchemy import create_engine, MetaData, Table, Column, BigInteger, Integer, String, Boolean, Double, Text, ForeignKey, PrimaryKeyConstraint
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env
load_dotenv()
DATABASE_URL = os.getenv("DB_URL")

# Создание подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание объекта MetaData
metadata = MetaData()

# database/db.py
employees = Table(
    'employees', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('user_id', Double),
    Column('company_id', BigInteger),
    Column('timezone_id', BigInteger),
    Column('telegram_id', Double),
    Column('presence_close_rule', Double),
    Column('phone', Double),
    Column('identification_photos', Text),  # Изменено с Double на Text
    Column('identification_photos_count', Double),
    Column('preferred_photo', Double),
    Column('email', Text),
    Column('positions', Text),
    Column('avatar', Text),
    Column('avatar_big', Text),
    Column('placements', Text),
    Column('first_name', Text),
    Column('last_name', Text),
    Column('snils', Text),
    Column('clid', Text),
    Column('sites', Text),
    Column('subdivisions', Text)
)

# Определение таблицы placements
placements = Table(
    'placements', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('company_id', BigInteger),
    Column('timezone_id', BigInteger),
    Column('color_id', BigInteger),
    Column('status', BigInteger),
    Column('terminal_monitoring_enabled', Boolean),
    Column('location_control', Double),
    Column('liveness_enabled', Boolean),
    Column('clid', Double),
    Column('name', Text),
    Column('ips', Text),
    Column('color', Text),
    Column('mac_addresses', Text),
    Column('managers', Text)
)

# Определение таблицы positions
positions = Table(
    'positions', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('company_id', BigInteger),
    Column('name', Text),
    Column('clid', Double),
    Column('color', Text),
    Column('color_id', BigInteger),
    Column('status', BigInteger),
    Column('managers', Text),
    Column('subdivisions', Text)
)

# database/db.py
presence_report = Table(
    'presence_report', metadata,
    Column('employee_id', BigInteger, ForeignKey('employees.id')),
    Column('date', Text),
    Column('start_time', Text),
    Column('end_time', Text),
    Column('is_night_shift', Boolean),
    Column('original_estimate', BigInteger),
    Column('real_estimate', BigInteger),
    Column('is_red', Boolean),
    Column('first_name', Text),
    Column('last_name', Text),
    Column('email', Text),
    PrimaryKeyConstraint('employee_id', 'date')
)

# Определение таблицы subdivisions
subdivisions = Table(
    'subdivisions', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('company_id', BigInteger),
    Column('name', Text),
    Column('clid', Double),
    Column('color', Text),
    Column('color_id', BigInteger),
    Column('status', BigInteger),
    Column('managers', Text),
    Column('placements', Text)
)

# Определение таблицы user_settings
user_settings = Table(
    'user_settings', metadata,
    Column('telegram_id', BigInteger, primary_key=True),
    Column('employee_id', BigInteger, ForeignKey('employees.id')),
    Column('subscribed', Boolean, default=True),
    Column('vacation_start', Text, nullable=True),
    Column('vacation_end', Text, nullable=True),
    Column('notification_times', Text, default='[]')  # Список времен оповещений в формате JSON
)

# Определение таблицы notifications
notifications = Table(
    'notifications', metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('telegram_id', BigInteger, ForeignKey('user_settings.telegram_id')),
    Column('message', Text),
    Column('sent_at', Text),
    Column('status', Text, default='pending')  # pending, sent, failed
)


timezones = Table(
    'timezones', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, unique=True)  # Например, 'Asia/Vladivostok'
)

# Создание всех таблиц
metadata.create_all(engine)
print("Все таблицы были успешно созданы с указанными типами данных и связями.")