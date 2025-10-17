import json
import yaml
import re
from typing import Any, Callable, List, Optional, Union

import psycopg2


class ShortClient:
    def __init__(self, client_id=None, last_name=None, first_name=None, phone=None):
        self.__client_id = client_id
        self.__last_name = last_name
        self.__first_name = first_name
        self.__phone = phone

    @property
    def client_id(self):
        return self.__client_id

    @property
    def last_name(self):
        return self.__last_name

    @property
    def first_name(self):
        return self.__first_name

    @property
    def phone(self):
        return self.__phone

    @staticmethod
    def is_valid_id(client_id):
        return client_id is not None and client_id > 0

    @staticmethod
    def is_valid_name(name):
        return name is not None and re.match(r"^[А-Яа-яЁё\s]+$", name) is not None

    @staticmethod
    def is_valid_phone(phone):
        return phone is not None and re.match(r"^\+\d{11}$", phone) is not None

    def set_client_id(self, client_id):
        if not ShortClient.is_valid_id(client_id):
            raise ValueError("ID клиента должно быть положительным числом")
        self.__client_id = client_id

    def set_last_name(self, last_name):
        if not ShortClient.is_valid_name(last_name):
            raise ValueError("Фамилия должна содержать только буквы")
        self.__last_name = last_name

    def set_first_name(self, first_name):
        if not ShortClient.is_valid_name(first_name):
            raise ValueError("Имя должно содержать только буквы")
        self.__first_name = first_name

    def set_phone(self, phone):
        if not ShortClient.is_valid_phone(phone):
            raise ValueError(
                "Номер телефона должен начинаться с '+' и содержать 11 цифр, а также не быть пустым"
            )
        self.__phone = phone

    def get_info(self):
        return f"ФИ: {self.last_name} {self.first_name[0]}., Телефон: {self.phone}"


class Client(ShortClient):
    def __init__(self, *args, **kwargs):
        data = kwargs.pop("data", None)

        if data is not None:
            super().__init__()
            self.__otch = None
            self.__address = None
            self.from_str(data)
        elif args:
            if len(args) >= 4:
                client_id, last_name, first_name, phone = (
                    args[0],
                    args[1],
                    args[2],
                    args[3],
                )
                otch = args[4] if len(args) > 4 else None
                address = args[5] if len(args) > 5 else None
                super().__init__(client_id, last_name, first_name, phone)
                self.__otch = None
                self.__address = None
                self.set_otch(otch)
                self.set_address(address)
            else:
                raise ValueError("Недостаточно аргументов")
        elif kwargs:
            client_id = kwargs.get("client_id")
            last_name = kwargs.get("last_name")
            first_name = kwargs.get("first_name")
            phone = kwargs.get("phone")
            otch = kwargs.get("otch")
            address = kwargs.get("address")

            if (
                client_id is not None
                and last_name is not None
                and first_name is not None
                and phone is not None
            ):
                super().__init__(client_id, last_name, first_name, phone)
                self.__otch = None
                self.__address = None
                self.set_otch(otch)
                self.set_address(address)
            else:
                raise ValueError(
                    "Обязательные параметры: client_id, last_name, first_name, phone"
                )
        else:
            super().__init__()
            self.__otch = None
            self.__address = None

    @property
    def otch(self):
        return self.__otch

    @property
    def address(self):
        return self.__address

    def set_otch(self, otch):
        if otch and otch.strip() != "":
            if not re.match(r"^[А-Яа-яЁё\s]+$", otch):
                raise ValueError("Отчество должно содержать только буквы")
        self.__otch = otch

    def set_address(self, address):
        if address is None or address.strip() == "":
            raise ValueError("Адрес не должен быть пустым")
        self.__address = address

    def from_str(self, data):
        data = data.strip()
        if data.startswith("{"):
            data_dict = json.loads(data)
            self.set_client_id(data_dict.get("client_id"))
            self.set_last_name(data_dict.get("last_name"))
            self.set_first_name(data_dict.get("first_name"))
            self.set_otch(data_dict.get("otch"))
            self.set_address(data_dict.get("address"))
            self.set_phone(data_dict.get("phone"))
        else:
            parts = data.split(",")
            self.set_client_id(int(parts[0]))
            self.set_last_name(parts[1])
            self.set_first_name(parts[2])
            self.set_otch(parts[3])
            self.set_address(parts[4])
            self.set_phone(parts[5])

    def short(self):
        return ShortClient(
            client_id=self.client_id,
            last_name=self.last_name,
            first_name=self.first_name,
            phone=self.phone,
        )

    def get_long_info(self):
        otch_info = f", Отчество: {self.otch}" if self.otch else ""
        return (
            f"client_id={self.client_id}, Фамилия: {self.last_name}, "
            f"Имя: {self.first_name}{otch_info}, "
            f"Адрес: {self.address}, Телефон: {self.phone}"
        )

    def __eq__(self, other):
        if not isinstance(other, Client):
            return False
        return (
            self.client_id == other.client_id
            and self.last_name == other.last_name
            and self.first_name == other.first_name
            and self.otch == other.otch
            and self.address == other.address
            and self.phone == other.phone
        )


class ClientRep:
    def __init__(self, filename):
        self.filename = filename

    def read_all(self):
        raise NotImplementedError

    def write_all(self, clients):
        raise NotImplementedError

    def get_by_id(self, client_id):
        clients = self.read_all()
        for client in clients:
            if client.client_id == client_id:
                return client
        return None

    def sort_by_field(self, field="last_name", reverse=False):
        clients = self.read_all()
        clients.sort(key=lambda client: getattr(client, field) or "", reverse=reverse)
        return clients

    def get_k_n_short_list(self, k, n):
        clients = self.read_all()
        start_index = (n - 1) * k
        end_index = start_index + k
        result = []
        for i in range(start_index, end_index):
            if i < len(clients):
                short_client = clients[i].short()
                result.append(short_client)
        return result

    def add_client(self, last_name, first_name, phone, address, otch=None):
        clients = self.read_all()
        new_id = 0
        for client in clients:
            if client.client_id > new_id:
                new_id = client.client_id
        new_id += 1
        try:
            new_client = Client(
                client_id=new_id,
                last_name=last_name,
                first_name=first_name,
                phone=phone,
                address=address,
                otch=otch,
            )
            clients.append(new_client)
            return new_client if self.write_all(clients) else None
        except ValueError:
            return None

    def update_client(
        self,
        client_id,
        last_name=None,
        first_name=None,
        phone=None,
        address=None,
        otch=None,
    ):
        clients = self.read_all()
        for i, client in enumerate(clients):
            if client.client_id == client_id:
                new_last_name = last_name if last_name is not None else client.last_name
                new_first_name = (
                    first_name if first_name is not None else client.first_name
                )
                new_phone = phone if phone is not None else client.phone
                new_address = address if address is not None else client.address
                new_otch = otch if otch is not None else client.otch
                updated_client = Client(
                    client_id=client_id,
                    last_name=new_last_name,
                    first_name=new_first_name,
                    phone=new_phone,
                    address=new_address,
                    otch=new_otch,
                )
                clients[i] = updated_client
                return updated_client if self.write_all(clients) else None
        return None

    def delete_client(self, client_id: int):
        clients = self.read_all()
        index_to_delete = None
        for i, c in enumerate(clients):
            if c.client_id == client_id:
                index_to_delete = i
                break
        if index_to_delete is None:
            return False
        clients.pop(index_to_delete)
        return self.write_all(clients)

    def get_count(self):
        return len(self.read_all())


class ClientRepJson(ClientRep):
    def read_all(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
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
        except (FileNotFoundError, json.JSONDecodeError):
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
        except Exception:
            return False


class ClientRepYaml(ClientRep):
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
        except Exception:
            return False


class DatabaseSingleton:
    _instance = None

    def __new__(
        cls,
        host="localhost",
        user="postgres",
        password="123",
        database="clients_database",
        port="5432",
    ):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(host, user, password, database, port)
        return cls._instance

    def _initialize(self, host, user, password, database, port):
        self.connection = psycopg2.connect(
            host=host, user=user, password=password, database=database, port=port
        )

    def execute_query(self, query, params=None, fetch=False):
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        result = cursor.fetchall() if fetch else cursor.rowcount
        self.connection.commit()
        cursor.close()
        return result

    def close(self):
        if self.connection:
            self.connection.close()
            self._instance = None


class DatabaseDelegate:
    def __init__(self, db_connector):
        self.db = db_connector

    def find_by_id(self, table, id_value):
        sql = f"SELECT * FROM {table} WHERE client_id = %s"
        return self.db.execute_query(sql, [id_value], fetch=True)

    def get_all_paginated(self, table, limit, offset):
        sql = f"SELECT * FROM {table} ORDER BY client_id LIMIT %s OFFSET %s"
        return self.db.execute_query(sql, [limit, offset], fetch=True)

    def insert(self, table, data):
        columns = ", ".join(data.keys())
        values_placeholder = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({values_placeholder})"
        return self.db.execute_query(sql, list(data.values()))

    def update(self, table, updates, id_value):
        set_expr = ", ".join([f"{key} = %s" for key in updates.keys()])
        sql = f"UPDATE {table} SET {set_expr} WHERE client_id = %s"
        params = list(updates.values()) + [id_value]
        return self.db.execute_query(sql, params)

    def delete(self, table, id_value):
        sql = f"DELETE FROM {table} WHERE client_id = %s"
        return self.db.execute_query(sql, [id_value])

    def count(self, table):
        sql = f"SELECT COUNT(*) FROM {table}"
        result = self.db.execute_query(sql, fetch=True)
        return result[0][0] if result else 0


class ClientRepDB:
    def __init__(self):
        self.db = DatabaseSingleton()
        self.delegate = DatabaseDelegate(self.db)

    def close(self):
        self.db.close()

    def get_by_id(self, client_id):
        result = self.delegate.find_by_id("clients", client_id)
        if result:
            row = result[0]
            return Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                otch=row[3],
                address=row[4],
                phone=row[5],
            )
        return None

    def get_k_n_short_list(self, k, n):
        offset = (n - 1) * k
        rows = self.delegate.get_all_paginated("clients", k, offset)
        short_clients = []
        for row in rows:
            client = Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                otch=row[3],
                address=row[4],
                phone=row[5],
            )
            short_clients.append(client.short())
        return short_clients

    def add_client(self, last_name, first_name, phone, address, otch=None):
        data = {
            "last_name": last_name,
            "first_name": first_name,
            "phone": phone,
            "address": address,
            "otch": otch,
        }
        self.delegate.insert("clients", data)

    def update_client(
        self,
        client_id,
        last_name=None,
        first_name=None,
        phone=None,
        address=None,
        otch=None,
    ):
        current_client = self.get_by_id(client_id)
        if not current_client:
            return None
        updates = {
            "last_name": (
                last_name if last_name is not None else current_client.last_name
            ),
            "first_name": (
                first_name if first_name is not None else current_client.first_name
            ),
            "phone": phone if phone is not None else current_client.phone,
            "address": address if address is not None else current_client.address,
            "otch": otch if otch is not None else current_client.otch,
        }
        self.delegate.update("clients", updates, client_id)
        return self.get_by_id(client_id)

    def delete_client(self, client_id):
        return self.delegate.delete("clients", client_id)

    def get_count(self):
        return self.delegate.count("clients")


class ClientRepDBAdapter(ClientRep):
    def __init__(self):
        super().__init__("")
        self.adaptee = ClientRepDB()

    def close(self):
        self.adaptee.close()

    def read_all(self):
        total_clients = self.adaptee.get_count()
        results = self.adaptee.delegate.get_all_paginated("clients", total_clients, 0)
        clients = []
        for row in results:
            client = Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                otch=row[3],
                address=row[4],
                phone=row[5],
            )
            clients.append(client)
        return clients

    def add_client(self, last_name, first_name, phone, address, otch=None):
        return self.adaptee.add_client(last_name, first_name, phone, address, otch)

    def get_count(self):
        return self.adaptee.get_count()

    def get_k_n_short_list(self, k, n):
        return self.adaptee.get_k_n_short_list(k, n)

    def update_client(
        self,
        client_id,
        last_name=None,
        first_name=None,
        phone=None,
        address=None,
        otch=None,
    ):
        return self.adaptee.update_client(
            client_id, last_name, first_name, phone, address, otch
        )

    def delete_client(self, client_id):
        return self.adaptee.delete_client(client_id)


class ClientRepDecorator(ClientRep):
    def __init__(self, wrapped_repo: ClientRep):
        self._wrapped_repo = wrapped_repo
        super().__init__(wrapped_repo.filename)

    def __getattr__(self, name):
        return getattr(self._wrapped_repo, name)


class FilterSortDecorator(ClientRepDecorator):
    def __init__(
        self, wrapped_repo, filter_func=None, sort_key=None, reverse_sort=False
    ):
        super().__init__(wrapped_repo)
        self.filter_func = filter_func
        self.sort_key = sort_key
        self.reverse_sort = reverse_sort

    def _filter_and_sort_clients(self, clients):
        if self.filter_func:
            filtered_clients = []
            for client in clients:
                if self.filter_func(client):
                    filtered_clients.append(client)
            clients = filtered_clients
        if self.sort_key:
            clients.sort(key=self.sort_key, reverse=self.reverse_sort)
        return clients

    def read_all(self):
        clients = self._wrapped_repo.read_all()
        return self._filter_and_sort_clients(clients)

    def get_k_n_short_list(self, k, n):
        clients = self.read_all()
        start_index = (n - 1) * k
        end_index = start_index + k
        result = []
        for i in range(start_index, end_index):
            if i < len(clients):
                short_client = clients[i].short()
                result.append(short_client)
        return result

    def get_count(self):
        clients = self.read_all()
        return len(clients)


json_repo = ClientRepJson("clients.json")
decorated_json = FilterSortDecorator(
    json_repo, sort_key=lambda client: client.first_name, reverse_sort=True
)
result_json = decorated_json.get_k_n_short_list(6, 1)
for client in result_json:
    print(client.get_info())
print(f"\nклиентов в JSON: {decorated_json.get_count()}\n")

yaml_repo = ClientRepYaml("clients.yaml")
decorated_yaml = FilterSortDecorator(
    yaml_repo,
    filter_func=lambda client: client.address == "Москва",
    sort_key=lambda client: client.first_name,
    reverse_sort=False,
)
result_yaml = decorated_yaml.get_k_n_short_list(5, 1)
for client in result_yaml:
    print(client.get_info())
print(f"\nклиентов в YAML отсортированные: {decorated_yaml.get_count()}")

try:
    db_repo = ClientRepDBAdapter()
    try:
        db_decorator = FilterSortDecorator(db_repo, sort_key=lambda c: c.first_name)
        print("\nвывод бд")
        db_page = db_decorator.get_k_n_short_list(5, 1)
        for i, client in enumerate(db_page, 1):
            print(f"{i}. {client.get_info()}")
        print(f"\nклиентов в бд: {db_decorator.get_count()}\n")
    finally:
        db_repo.close()
except Exception as e:
    print(f"БД репозиторий недоступен: {e}")
