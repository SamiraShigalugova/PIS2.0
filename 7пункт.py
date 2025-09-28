import psycopg2
from Clients import Client




class ClientRepository:
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

class ClientRepJson(ClientRepository):
    def __init__(self, filename="clients.json"):
        super().__init__(filename)

    def read_all(self):
        import json
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                clients = [Client(data=json.dumps(item)) for item in data]
                return clients
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def write_all(self, clients):
        import json
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

class ClientRepYaml(ClientRepository):
    def __init__(self, filename="clients.yaml"):
        super().__init__(filename)

    def read_all(self):
        import yaml
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
            return []
        except yaml.YAMLError:
            return []

    def write_all(self, clients):
        import yaml
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

class DatabaseConnection:
    _instance = None

    def __new__(cls, host="localhost", user="postgres", password="123", database="clients_database", port="5432"):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.host = host
            cls._instance.user = user
            cls._instance.password = password
            cls._instance.database = database
            cls._instance.port = port
            cls._instance.connection = None
            cls._instance.connect()
        return cls._instance

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            print(f"Успешное подключение к базе данных '{self.database}'")
        except psycopg2.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")

    def execute_query(self, query, params=None, fetch=False):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
            else:
                result = cursor.rowcount
                self.connection.commit()

            cursor.close()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")

class ClientRepDB:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_by_id(self, client_id):
        query = "SELECT client_id, last_name, first_name, otch, address, phone FROM clients WHERE client_id = %s"
        result = self.db.execute_query(query, (client_id,), fetch=True)

        if result and len(result) > 0:
            row = result[0]
            return Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                otch=row[3],
                address=row[4],
                phone=row[5]
            )
        return None

    def get_k_n_short_list(self, k, n):
        offset = (n - 1) * k
        query = """
        SELECT client_id, last_name, first_name, phone, address 
        FROM clients 
        ORDER BY client_id 
        LIMIT %s OFFSET %s
        """
        result = self.db.execute_query(query, (k, offset), fetch=True)

        short_clients = []
        for row in result:
            short_client = Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                phone=row[3],
                address=row[4]
            )
            short_clients.append(short_client.short())
        return short_clients

    def add_client(self, last_name, first_name, phone, address, otch=None):
        try:
            temp_client = Client()
            temp_client.set_last_name(last_name)
            temp_client.set_first_name(first_name)
            temp_client.set_phone(phone)
            temp_client.set_address(address)
            if otch:
                temp_client.set_otch(otch)

            query = """
            INSERT INTO clients (last_name, first_name, otch, address, phone) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING client_id
            """
            params = (last_name, first_name, otch, address, phone)

            result = self.db.execute_query(query, params, fetch=True)
            if result and len(result) > 0:
                new_id = result[0][0]
                print(f"Клиент успешно добавлен с ID: {new_id}")
                return self.get_by_id(new_id)
            return None

        except ValueError as e:
            print(f"Ошибка валидации данных: {e}")
            return None
        except Exception as e:
            print(f"Ошибка при добавлении клиента: {e}")
            return None

    def update_client(self, client_id, last_name=None, first_name=None, phone=None, address=None, otch=None):
        try:
            current_client = self.get_by_id(client_id)
            if not current_client:
                print(f"Клиент с ID {client_id} не найден")
                return None

            temp_client = Client(
                client_id=current_client.client_id,
                last_name=current_client.last_name,
                first_name=current_client.first_name,
                otch=current_client.otch,
                address=current_client.address,
                phone=current_client.phone
            )

            if last_name is not None:
                temp_client.set_last_name(last_name)
            if first_name is not None:
                temp_client.set_first_name(first_name)
            if phone is not None:
                temp_client.set_phone(phone)
            if address is not None:
                temp_client.set_address(address)
            if otch is not None:
                temp_client.set_otch(otch)

            new_last_name = last_name if last_name is not None else current_client.last_name
            new_first_name = first_name if first_name is not None else current_client.first_name
            new_phone = phone if phone is not None else current_client.phone
            new_address = address if address is not None else current_client.address
            new_otch = otch if otch is not None else current_client.otch

            query = """
            UPDATE clients 
            SET last_name = %s, first_name = %s, otch = %s, address = %s, phone = %s 
            WHERE client_id = %s
            """
            params = (new_last_name, new_first_name, new_otch, new_address, new_phone, client_id)

            rows_affected = self.db.execute_query(query, params)
            if rows_affected:
                print(f"Клиент с ID {client_id} успешно обновлен")
                return self.get_by_id(client_id)
            return None

        except ValueError as e:
            print(f"Ошибка валидации данных: {e}")
            return None
        except Exception as e:
            print(f"Ошибка при обновлении клиента: {e}")
            return None

    def delete_client(self, client_id):
        client_to_delete = self.get_by_id(client_id)
        if not client_to_delete:
            print(f"Клиент с ID {client_id} не найден")
            return None

        query = "DELETE FROM clients WHERE client_id = %s"
        rows_affected = self.db.execute_query(query, (client_id,))
        if rows_affected:
            print(f"Клиент с ID {client_id} успешно удален")
            return client_to_delete
        return None

    def get_all_clients(self):
        query = "SELECT client_id, last_name, first_name, otch, address, phone FROM clients ORDER BY client_id"
        result = self.db.execute_query(query, fetch=True)

        clients = []
        for row in result:
            client = Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                otch=row[3],
                address=row[4],
                phone=row[5]
            )
            clients.append(client)

        return clients

    def get_count(self):
        query = "SELECT COUNT(*) FROM clients"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0] if result else 0

    def close_connection(self):
        self.db.close()

class ClientRepDBAdapter(ClientRepository):
    def __init__(self):
        super().__init__("database")

        self.adaptee = ClientRepDB()

    def read_all(self):
        return self.adaptee.get_all_clients()

    def write_all(self, clients):

        try:

            current_clients = self.read_all()
            for client in current_clients:
                self.adaptee.delete_client(client.client_id)

            for client in clients:
                self.adaptee.add_client(
                    last_name=client.last_name,
                    first_name=client.first_name,
                    phone=client.phone,
                    address=client.address,
                    otch=client.otch
                )
            return True
        except Exception as e:
            print(f"Ошибка при пакетной записи: {e}")
            return False

    def get_by_id(self, client_id):
        return self.adaptee.get_by_id(client_id)

    def get_k_n_short_list(self, k, n):
        return self.adaptee.get_k_n_short_list(k, n)

    def add_client(self, last_name, first_name, phone, address, otch=None):
        return self.adaptee.add_client(last_name, first_name, phone, address, otch)

    def update_client(self, client_id, last_name=None, first_name=None, phone=None, address=None, otch=None):
        return self.adaptee.update_client(client_id, last_name, first_name, phone, address, otch)

    def delete_client(self, client_id):
        return self.adaptee.delete_client(client_id)

    def get_count(self):
        return self.adaptee.get_count()

    def get_all_clients(self):
        return self.adaptee.get_all_clients()

class FilterDecorator:
    def __init__(self, repository, filter_func=None):
        self._repository = repository
        self.filter_func = filter_func

    def __getattr__(self, name):
        return getattr(self._repository, name)

    def _apply_filter(self, clients):
        if self.filter_func:
            return [client for client in clients if self.filter_func(client)]
        return clients

    def get_k_n_short_list(self, k, n):
        clients = self._repository.read_all()
        filtered_clients = self._apply_filter(clients)
        start_index = (n - 1) * k
        end_index = start_index + k
        if start_index >= len(filtered_clients):
            return []
        short_clients = []
        for client in filtered_clients[start_index:end_index]:
            short_clients.append(client.short())
        return short_clients

    def get_count(self):
        clients = self._repository.read_all()
        filtered_clients = self._apply_filter(clients)
        return len(filtered_clients)



class SortDecorator:
    def __init__(self, repository, sort_field="last_name", reverse=False):
        self._repository = repository
        self.sort_field = sort_field
        self.reverse = reverse

    def __getattr__(self, name):
        return getattr(self._repository, name)

    def _apply_sort(self, clients):
        valid_fields = ["last_name", "first_name", "client_id", "phone"]
        if self.sort_field not in valid_fields:
            raise ValueError(f"Недопустимое поле для сортировки")

        sort_list = []
        for client in clients:
            if self.sort_field == "client_id":
                key = client.client_id
            elif self.sort_field == "last_name":
                key = client.last_name or ""
            elif self.sort_field == "first_name":
                key = client.first_name or ""
            elif self.sort_field == "phone":
                key = client.phone or ""
            sort_list.append((key, client))

        sort_list.sort(key=lambda x: x[0], reverse=self.reverse)
        return [client for key, client in sort_list]

    def get_k_n_short_list(self, k, n):
        clients = self._repository.read_all()
        sorted_clients = self._apply_sort(clients)
        start_index = (n - 1) * k
        end_index = start_index + k
        if start_index >= len(sorted_clients):
            return []
        short_clients = []
        for client in sorted_clients[start_index:end_index]:
            short_clients.append(client.short())
        return short_clients




base_repo = ClientRepDBAdapter()
def filter_by_city(city):
    def filter_func(client):
        return city.lower() in client.address.lower()
    return filter_func
print(f"Всего клиентов: {base_repo.get_count()}")
print("Первые 3 клиента:")
clients = base_repo.get_k_n_short_list(3, 1)
for i, client in enumerate(clients, 1):
    print(f"  {client.get_info()}")
print("-" * 40)
moscow_filter = filter_by_city("Москва")
filtered_repo = FilterDecorator(base_repo, moscow_filter)
print(f"Количество клиентов из Москвы: {filtered_repo.get_count()}")
print("Клиенты из Москвы:")
moscow_clients = filtered_repo.get_k_n_short_list(5, 1)
for i, client in enumerate(moscow_clients, 1):
    print(f"  {client.get_info()}")
print("-" * 40)
sorted_repo = SortDecorator(base_repo, "last_name", reverse=True)
print("Сортировка по фамилии:")
sorted_clients = sorted_repo.get_k_n_short_list(5, 1)
for i, client in enumerate(sorted_clients, 1):
    print(f"  {client.get_info()}")


