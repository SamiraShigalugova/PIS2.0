import json
from Clients import Client

class ClientRepJson:
    def __init__(self, filename="clients.json"):
        self.filename = filename

    def read_all(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                clients = [Client(data=json.dumps(item)) for item in data]
                return clients
        except FileNotFoundError:
            print(f"Файл {self.filename} не найден")
            return []
        except json.JSONDecodeError:
            print(f"Ошибка чтения JSON из файла {self.filename}")
            return []

    def write_all(self, clients):
        try:
            data = []
            for client in clients:
                client_data = {
                    "client_id": client.client_id,
                    "last_name": client.last_name,
                    "first_name": client.first_name,
                    "otch": client.otch,
                    "address": client.address,
                    "phone": client.phone
                }
                data.append(client_data)

            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            print(f"Данные успешно записаны в файл {self.filename}")
            return True

        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")
            return False




repo = ClientRepJson("clients.json")
clients = repo.read_all()
new_client = Client(
    client_id=100,
    last_name="Петров",
    first_name="Петр",
    otch="Петрович",
    address="Москва",
    phone="+79161234567"
)
clients.append(new_client)
repo.write_all(clients)
updated_clients = repo.read_all()
for client in updated_clients:
    print(client.get_long_info())



