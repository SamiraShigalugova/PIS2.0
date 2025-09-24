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

    def get_by_id(self, client_id):
        clients = self.read_all()
        for client in clients:
            if client.client_id == client_id:
                return client
        return None



    def get_k_n_short_list(self, k, n):
        clients = self.read_all()
        start_index = (n - 1) * k
        end_index = start_index + k
        if start_index >= len(clients):
            return []
        short_clients = []
        for client in clients[start_index:end_index]:
            short_clients.append(client.short())
        return short_clients


    def sort_by_field(self, field="last_name", reverse=False):
        clients = self.read_all()
        valid_fields = ["last_name", "first_name", "client_id", "phone"]
        if field not in valid_fields:
            raise ValueError(f"Недопустимое поле для сортировки")
        sort_list = []
        for client in clients:
            if field == "client_id":
                key = client.client_id
            elif field == "last_name":
                key = client.last_name or ""
            elif field == "first_name":
                key = client.first_name or ""
            elif field == "phone":
                key = client.phone or ""
            sort_list.append((key, client))

        sort_list.sort(reverse=reverse)
        return [client for key, client in sort_list]




repo = ClientRepJson("clients.json")
clients = repo.read_all()

new_client = Client(
    client_id=12,
    last_name="Кролик",
    first_name="Дмитрий",
    otch="Львович",
    address="Москва",
    phone="+79161234567"
)
print("\n" + "*"*50)
clients.append(new_client)
repo.write_all(clients)

updated_clients = repo.read_all()
for client in updated_clients:
    print(client.get_long_info())
print("\n" + "*"*50)
client = repo.get_by_id(50)
if client:
    print("Клиент с таким ID найден:")
    print(client.get_long_info())
else:
    print("Клиент с таким ID не найден")

print("\n" + "*"*50)
print("Выборка клиентов:")
first_page = repo.get_k_n_short_list(k=2, n=2)
for short_client in first_page:
    print(short_client.get_info())

print("\n" + "*"*50)
print("Сортировка по фамилии:")
sorted_clients = repo.sort_by_field("last_name")
for client in sorted_clients:
    print(f"{client.last_name} {client.first_name}")





