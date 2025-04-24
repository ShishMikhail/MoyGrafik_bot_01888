import subprocess

def run_command(cmd, description):
    print(f"\n🚀 {description}...")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Ошибка при выполнении: {description}")
        exit(result.returncode)
    print(f"✅ Завершено: {description}")

# 1. Обновление CSV из API
run_command("python3 database/Update_CSV.py", "Обновление CSV из API")

# 2. Создание базы данных и таблиц
run_command("python3 database/Create_db.py", "Создание структуры БД")

# 3. Преобразование данных (нормализация)
run_command("python3 -m database.Normal_wid", "Нормализация данных")

# 4. Запись в БД из нормализованных CSV
run_command("python3 -m database.UPDATE_DATABASE", "Запись данных в БД")
