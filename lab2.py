import psycopg2
from clients import Client

class DatabaseSingleton:
    _instance = None

    def __new__(cls, host="localhost", user="postgres", password="123", database="clients_database", port="5432"):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            cls._instance._initialize(host, user, password, database, port)
        return cls._instance

    def _initialize(self, host, user, password, database, port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self._connect()

    def _connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
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
            self.connection.rollback()
            return None

    def close(self):
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")


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
        znach = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({znach})"
        return self.db.execute_query(sql, list(data.values()))

    def update(self, table, updates, id_value):
        set_znach = ", ".join([f"{key} = %s" for key in updates.keys()])
        sql = f"UPDATE {table} SET {set_znach} WHERE client_id = %s"
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
                phone=row[5]
            )
        return None

    def get_k_n_short(self, k, n):
        offset = (n - 1) * k
        results = self.delegate.get_all_paginated("clients", k, offset)
        short_clients = []
        for row in results:
            client = Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                phone=row[3],
                address=row[4],
            )
            short_clients.append(client.short())
        return short_clients

    def add_client(self, last_name, first_name, phone, address, otch=None):
        try:
            client = Client(
                last_name=last_name,
                first_name=first_name,
                phone=phone,
                address=address,
                otch=otch
            )
            data = {
                "last_name": last_name,
                "first_name": first_name,
                "phone": phone,
                "address": address,
                "otch": otch
            }
            self.delegate.insert("clients", data)
            print("Клиент добавлен!")
        except ValueError as e:
            print(f"Ошибка добавления клиента: {e}")

    def update_client(self, client_id, last_name=None, first_name=None, phone=None, address=None, otch=None):
        try:
            current_client = self.get_by_id(client_id)
            if not current_client:
                print(f"Клиент с ID {client_id} не найден")
                return None
            updated_client = Client(
                client_id=client_id,
                last_name=last_name if last_name is not None else current_client.last_name,
                first_name=first_name if first_name is not None else current_client.first_name,
                phone=phone if phone is not None else current_client.phone,
                address=address if address is not None else current_client.address,
                otch=otch if otch is not None else current_client.otch,
            )
            updates = {
                "last_name": updated_client.last_name,
                "first_name": updated_client.first_name,
                "otch": updated_client.otch,
                "address": updated_client.address,
                "phone": updated_client.phone
            }
            rows_affected = self.delegate.update("clients", updates, client_id)
            if rows_affected:
                print(f"Клиент с ID {client_id} успешно обновлен")
                return updated_client
            return None

        except ValueError as e:
            print(f"Ошибка валидации данных: {e}")
            return None
        except Exception as e:
            print(f"Ошибка при обновлении клиента: {e}")
            return None

    def delete_client(self, client_id):
        self.delegate.delete("clients", client_id)
        print(f"Клиент {client_id} удален!")

    def get_count(self):
        return self.delegate.count("clients")




repo1 = ClientRepDB()
repo2 = ClientRepDB()
print(f"Один и тот же объект БД: {repo1.db is repo2.db}")
print(f"\nКоличество клиентов в первом экземпляре: {repo1.get_count()}")
print(f"Количество клиентов во втором: {repo2.get_count()}")
print("\nВыборка клиентов:")
short_clients = repo1.get_k_n_short(k=4, n=1)
for i, short_client in enumerate(short_clients, 1):
    print(f"{i}. {short_client.get_info()}")

# new_client = repo1.add_client(
#     last_name="Смирнов",
#     first_name="Алексей",
#     otch="Владимирович",
#     phone="+79165554433",
#     address="г. Москва, ул. Ленина 15"
# )
# if new_client:
#     client_id_to_update = 82
#     updated_client = repo1.update_client(
#         client_id=client_id_to_update,
#         last_name="Иванов",
#         phone="+79167778899"
#     )
