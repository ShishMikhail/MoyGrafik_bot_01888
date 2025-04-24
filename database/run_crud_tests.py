from database.crud import create_record, read_all, update_record, delete_record
from database.Create_db import employees

# --- CREATE ---
create_record(employees, {
    "id": 999999,
    "user_id": 100001,
    "company_id": 1525,
    "timezone_id": 516,
    "first_name": "Тест",
    "last_name": "Пользователь",
    "email": "test@example.com"
})

# --- READ ---
read_all(employees)

# --- UPDATE ---
update_record(employees, 999999, {"first_name": "Обновлённый"})

# --- DELETE ---
delete_record(employees, 999999)
