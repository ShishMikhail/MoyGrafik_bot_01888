from api.moygrafik_api import MoyGrafikAPI
import pandas as pd

def test_api_methods():
    api = MoyGrafikAPI()
    company_id = 1525
    mac_address = 'D0:5A:FD:DA:55:BB'
    start_date = '01-01-2025'
    end_date = '26-03-2025'
    positions = '36392'

    try:
        # Тестирование получения сотрудников
        employees = api.get_employees(company_id)
        print("Сотрудники:")
        df_employees = pd.DataFrame(employees)
        print(df_employees)
    except Exception as e:
        print("Ошибка при получении сотрудников:", e)

    try:
        # Тестирование получения размещений
        placements = api.get_placements(company_id)
        print("Размещения:")
        df_placements = pd.DataFrame(placements)
        print(df_placements)
    except Exception as e:
        print("Ошибка при получении размещений:", e)

    try:
        # Тестирование получения подразделений
        subdivisions = api.get_subdivisions(company_id)
        print("Подразделения:")
        df_subdivisions = pd.DataFrame(subdivisions)
        print(df_subdivisions)
    except Exception as e:
        print("Ошибка при получении подразделений:", e)

    try:
        # Тестирование получения позиций
        positions_list = api.get_positions(company_id)
        print("Позиции:")
        df_positions = pd.DataFrame(positions_list)
        print(df_positions)
    except Exception as e:
        print("Ошибка при получении позиций:", e)

    try:
        # Тестирование идентификации
        identification = api.test_identification(company_id, mac_address)
        print("Идентификация:", identification)
    except Exception as e:
        print("Ошибка при идентификации:", e)

    try:
        # Тестирование получения отчета о присутствии
        presence_report = api.get_presence_report(company_id, start_date, end_date, positions)
        print("Отчет о присутствии:")
        df_presence = pd.DataFrame(presence_report)
        print(df_presence)
    except Exception as e:
        print("Ошибка при получении отчета о присутствии:", e)


# Вызов функции для тестирования
if __name__ == '__main__':
    test_api_methods()