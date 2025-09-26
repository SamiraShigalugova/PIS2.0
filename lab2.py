import json
import yaml
from Clients import Client

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
        sort_list.sort(key=lambda x: x[0], reverse=reverse)
        return [client for key, client in sort_list]

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
                phone=phone
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
                    otch=new_otch
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
            return True

        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")
            return False



class ClientRepYaml(ClientRep):
    def __init__(self, filename="clients.yaml"):
        super().__init__(filename)

    def read_all(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                if data is None:
                    return []

                clients = []
                for item in data:
                    client = Client(
                        client_id=item.get('client_id'),
                        last_name=item.get('last_name'),
                        first_name=item.get('first_name'),
                        otch=item.get('otch'),
                        address=item.get('address'),
                        phone=item.get('phone')
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
                    "phone": client.phone
                }
                data.append(client_data)

            with open(self.filename, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True, default_flow_style=False)
            return True

        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")
            return False





repo_json = ClientRepJson("clients.json")
print("\nДобавление нового клиента в файл JSON:")
new_client = repo_json.add_client(
    last_name="Иванов",
    first_name="Иван",
    otch="Петрович",
    phone="+79161111111",
    address="г. Краснодар"
)

count_json = repo_json.get_count()
print(f"Количество клиентов: {count_json}")



repo_yaml = ClientRepYaml("clients.yaml")
print("\nДобавление нового клиента в файл YAML:")
new_client = repo_yaml.add_client(
    last_name="Сидоров",
    first_name="Петр",
    otch="Иванович",
    phone="+79162222222",
    address="г. Нальчик"
)

count_yaml = repo_yaml.get_count()
print(f"Количество клиентов: {count_yaml}")




repositories = [repo_json, repo_yaml]
names = ["JSON", "YAML"]
for repo, name in zip(repositories, names):
    print(f"\n--- {name} репозиторий ---")
    print(f"Количество: {repo.get_count()}")
    client = repo.get_by_id(1)
    if client:
        print(f"Клиент с ID 1: {client.last_name}")
    sorted_clients = repo.sort_by_field("last_name")
    print(f"Первые 3 фамилии: {[c.last_name for c in sorted_clients[:3]]}")
