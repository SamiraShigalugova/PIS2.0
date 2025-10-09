import json
import yaml
from clients import Client

class ClientRep:
    def __init__(self, filename):
        self.filename = filename

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
            short_obj = client.short()
            short_clients.append(short_obj.get_info())
        return short_clients

    def sort_by_field(self, field="last_name", reverse=False):
        clients = self.read_all()
        clients.sort(key=lambda client: getattr(client, field) or "", reverse=reverse)
        return clients

    def add_client(self, last_name, first_name, phone, address, otch=None):
        try:
            clients = self.read_all()
            if clients:
                max_id = 0
                for client in clients:
                    if client.client_id > max_id:
                        max_id = client.client_id
                new_id = max_id + 1
            else:
                new_id = 1
            new_client = Client(
                client_id=new_id,
                last_name=last_name,
                first_name=first_name,
                otch=otch,
                address=address,
                phone=phone,
            )
            clients.append(new_client)
            if self.write_all(clients):
                print(f"Клиент успешно добавлен с ID: {new_id}")
                return new_client
            else:
                print("Ошибка при сохранении данных")
                return None
        except Exception as e:
            print(f"Ошибка при добавлении клиента: {e}")
            return None

    def update_client(self, client_id, last_name=None, first_name=None, phone=None, address=None, otch=None):
        clients = self.read_all()
        for i, client in enumerate(clients):
            if client.client_id == client_id:
                new_last_name = last_name if last_name is not None else client.last_name
                new_first_name = first_name if first_name is not None else client.first_name
                new_phone = phone if phone is not None else client.phone
                new_address = address if address is not None else client.address
                new_otch = otch if otch is not None else client.otch
                new_client = Client(
                    client_id=client_id,
                    last_name=new_last_name,
                    first_name=new_first_name,
                    phone=new_phone,
                    address=new_address,
                    otch=new_otch,
                )
                clients[i] = new_client
                self.write_all(clients)
                return new_client
        return None

    def delete_client(self, client_id):
        clients = self.read_all()
        for i, client in enumerate(clients):
            if client.client_id == client_id:
                deleted_client = clients.pop(i)
                self.write_all(clients)
                return deleted_client
        return None

    def get_count(self):
        clients = self.read_all()
        return len(clients)


class ClientRepJson(ClientRep):
    def __init__(self, filename="clients.json"):
        super().__init__(filename)

    def read_all(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
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
                    "phone": client.phone,
                }
                data.append(client_data)
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")
            return False


class ClientRepYaml(ClientRep):
    def __init__(self, filename="clients.yaml"):
        super().__init__(filename)

    def read_all(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data is None:
                    return []
                clients = []
                for item in data:
                    client = Client(
                        client_id=item.get("client_id"),
                        last_name=item.get("last_name"),
                        first_name=item.get("first_name"),
                        otch=item.get("otch"),
                        address=item.get("address"),
                        phone=item.get("phone"),
                    )
                    clients.append(client)
                return clients
        except FileNotFoundError:
            print(f"Файл {self.filename} не найден")
            return []
        except yaml.YAMLError:
            print(f"Ошибка чтения YAML из файла {self.filename}")
            return []
        except Exception as e:
            print(f"Ошибка при создании клиентов: {e}")
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
                    "phone": client.phone,
                }
                data.append(client_data)
            with open(self.filename, "w", encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")
            return False


repo_json = ClientRepJson(".venv/clients.json")
# print("\nДобавление нового клиента в файл JSON:")
# new_client = repo_json.add_client(
#     last_name="Павлова",
#     first_name="Анна",
#     otch="Александровна",
#     phone="+79161115556",
#     address="г. Псков",
# )
count_json = repo_json.get_count()
print(f"Количество клиентов: {count_json}")
repo_yaml = ClientRepYaml(".venv/clients.yaml")
page_json = repo_json.get_k_n_short_list(2, 3)
for i, client_short in enumerate(page_json):
    print(f"{i}. {client_short}")


print("\nДобавление нового клиента в файл YAML:")
# new_client = repo_yaml.add_client(
#     last_name="Сомкина",
#     first_name="Марина",
#     otch="Исмаиловна",
#     phone="+791622224785",
#     address="г. Москва",
# )
count_yaml = repo_yaml.get_count()
sort_yaml = repo_yaml.sort_by_field()
print(f"Количество клиентов: {count_yaml}")
page_yaml = repo_yaml.get_k_n_short_list(5, 1)
for i, client_short in enumerate(page_yaml, 1):
    print(f"{i}. {client_short}")
print("-*******-")
sorted_clients = repo_yaml.sort_by_field("last_name", reverse=False)
for i, client in enumerate(sorted_clients, 1):
    print(f"{i}. {client.short().get_info()}")
