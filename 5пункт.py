import psycopg2
from Clients import Client


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


    def get_count(self):
        query = "SELECT COUNT(*) FROM clients"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0] if result else 0

    def close_connection(self):
        self.db.close()




repo1 = ClientRepDB()
repo2 = ClientRepDB()
print(f"Один и тот же объект БД: {repo1.db is repo2.db}")

try:

    print(f"\nКоличество клиентов в первом экземпляре: {repo1.get_count()}")
    print(f"Количество клиентов во втором: {repo2.get_count()}")
    print("\nТест на валидацию:")
    invalid_client = repo1.add_client(
        last_name="123",
        first_name="Тест",
        phone="+79161112233",
        address="г. Тест"
    )
    print("\nВыборка клиентов:")
    short_clients = repo1.get_k_n_short_list(k=2, n=1)
    for i, short_client in enumerate(short_clients, 1):
        print(f"{i}. {short_client.get_info()}")

finally:
    repo1.close_connection()