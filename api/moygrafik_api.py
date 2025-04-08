import requests

class MoyGrafikAPI:
    def __init__(self):

        self.token = 'Bearer NmY3OTIxMTE3N2M2ZDE2NTVjN2I5NmQwMTBmNjlkZDcxNTE3MjQwODdlYzI5NmJjMWNkZWUzMjVhY2FmODc0Yw'
        self.base_url = 'https://api.moygrafik.ru/api/external/v1'
        self.base_url_v1_1 = 'https://api.moygrafik.ru/api/external/v1.1'
        self.headers = {'Authorization': self.token}

    def get_employees(self, company_id):
        # Получить список сотрудников
        url = f"{self.base_url}/companies/{company_id}/employees"
        response = requests.get(url, headers=self.headers)
        # Проверить на успешность запроса
        response.raise_for_status()
        return response.json()

    def get_placements(self, company_id):
        # Получить информацию о размещениях
        url = f"{self.base_url}/companies/{company_id}/placements"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_subdivisions(self, company_id):
        # Получить информацию о подразделениях
        url = f"{self.base_url}/companies/{company_id}/subdivisions"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_positions(self, company_id):
        # Получить информацию о позициях
        url = f"{self.base_url}/companies/{company_id}/positions"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def test_identification(self, company_id, mac_address):
        # Тест идентификации по MAC-адресу
        url = f"{self.base_url_v1_1}/identification/companies/{company_id}/test?mac={mac_address}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_presence_report(self, company_id, start_date, end_date, positions):
        # Получить отчет о присутствии
        url = f"{self.base_url}/reports/presence/{company_id}"
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'positions': positions
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

# Пример использования
api = MoyGrafikAPI()
employees = api.get_employees(company_id=1525)
#print(employees)