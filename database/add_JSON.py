import requests
import json
import os


class MoyGrafikAPI:
    def __init__(self):
        self.token = 'Bearer NmY3OTIxMTE3N2M2ZDE2NTVjN2I5NmQwMTBmNjlkZDcxNTE3MjQwODdlYzI5NmJjMWNkZWUzMjVhY2FmODc0Yw'
        self.base_url = 'https://api.moygrafik.ru/api/external/v1'
        self.base_url_v1_1 = 'https://api.moygrafik.ru/api/external/v1.1'
        self.headers = {'Authorization': self.token}

    def get_employees(self, company_id):
        url = f"{self.base_url}/companies/{company_id}/employees"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        employees_dict = response.json()

        # Convert the dictionary to a list of employee dictionaries
        if isinstance(employees_dict, dict):
            employees = list(employees_dict.values())
        else:
            raise ValueError("Unexpected data structure for employees")

        return employees

    def get_placements(self, company_id):
        url = f"{self.base_url}/companies/{company_id}/placements"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        placements_dict = response.json()

        # Convert the dictionary to a list of placement dictionaries
        if isinstance(placements_dict, dict):
            placements = list(placements_dict.values())
        else:
            raise ValueError("Unexpected data structure for placements")

        return placements

    def get_subdivisions(self, company_id):
        url = f"{self.base_url}/companies/{company_id}/subdivisions"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        subdivisions_dict = response.json()

        # Convert the dictionary to a list of subdivision dictionaries
        if isinstance(subdivisions_dict, dict):
            subdivisions = list(subdivisions_dict.values())
        else:
            raise ValueError("Unexpected data structure for subdivisions")

        return subdivisions

    def get_positions(self, company_id):
        url = f"{self.base_url}/companies/{company_id}/positions"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        positions_dict = response.json()

        # Convert the dictionary to a list of position dictionaries
        if isinstance(positions_dict, dict):
            positions = list(positions_dict.values())
        else:
            raise ValueError("Unexpected data structure for positions")

        return positions

    def test_identification(self, company_id, mac_address):
        url = f"{self.base_url_v1_1}/identification/companies/{company_id}/test?mac={mac_address}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        identification_result = response.json()

        # Handle identification result as needed
        if not isinstance(identification_result, dict):
            raise ValueError("Expected a dictionary for identification result")

        return identification_result

    def get_presence_report(self, company_id, start_date, end_date, positions):
        url = f"{self.base_url}/reports/presence/{company_id}"
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'positions': positions
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        presence_report_dict = response.json()

        # Convert the dictionary to a list of dictionaries if necessary
        if isinstance(presence_report_dict, dict):
            presence_report = list(presence_report_dict.values())
        else:
            raise ValueError("Unexpected data structure for presence report")

        return presence_report


def load_json_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_json_to_file(data, filename):
    current_data = load_json_from_file(filename)
    existing_ids = {item['id'] for item in current_data} if current_data else set()
    new_data = [item for item in data if item['id'] not in existing_ids]

    current_data.extend(new_data)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=4)

    print(f"Data saved to {filename}, {len(new_data)} new records added.")


def main():
    company_id = 1525
    api = MoyGrafikAPI()

    try:
        # Получение сотрудников
        employees = api.get_employees(company_id)
        save_json_to_file(employees, 'employees.json')

        # Получение размещений
        placements = api.get_placements(company_id)
        save_json_to_file(placements, 'placements.json')

        # Получение подразделений
        subdivisions = api.get_subdivisions(company_id)
        save_json_to_file(subdivisions, 'subdivisions.json')

        # Получение позиций
        positions = api.get_positions(company_id)
        save_json_to_file(positions, 'positions.json')

        # Пример теста идентификации (параметр mac_address требует конкретного значения)
        mac_address = '00:00:00:00:00:00'  # замените на актуальный MAC-адрес
        identification_result = api.test_identification(company_id, mac_address)
        save_json_to_file([identification_result], 'identification_result.json')

        # Пример получения отчета о присутствии (требует указания дат и позиций)
        start_date = '2023-01-01'
        end_date = '2023-01-31'
        positions = [1, 2, 3]  # примеры ID позиций
        presence_report = api.get_presence_report(company_id, start_date, end_date, positions)
        save_json_to_file(presence_report, 'presence_report.json')

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()