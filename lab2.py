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



repo = ClientRepJson("clients.json")
clients = repo.read_all()
for client in clients:
    print("\nВывод из файла: ", client.get_long_info())