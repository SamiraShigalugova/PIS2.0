import psycopg2
from clients import Client


class Deleg:
    def __init__(self, db_connector):
        self.connector = db_connector
    def execute_select(self, table, columns, conditions):
        query = f"SELECT {', '.join(columns)} FROM {table}"
        if conditions:
            where_clause = ' AND '.join([f'{col}=%s' for col in conditions.keys()])
            query += f" WHERE {where_clause}"
        return self.connector.execute_query(query, tuple(conditions.values()), fetch=True)

    def execute_insert(self, table, values):
        cols = ', '.join(values.keys())
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        return self.connector.execute_query(query, list(values.values()))

    def execute_update(self, table, updates, condition):

        set_clause = ', '.join([f'{col}=%s' for col in updates.keys()])
        where_clause = f'{condition["column"]}=%s'
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        return self.connector.execute_query(query, list(updates.values()) + [condition['value']])

    def execute_delete(self, table, condition):
        where_clause = f'{condition["column"]}=%s'
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.connector.execute_query(query, (condition['value'], ))

    def execute_count(self, table):
        query = f"SELECT COUNT(*) FROM {table}"
        result = self.connector.execute_query(query, fetch=True)
        return result[0][0] if result else 0

    def select_with_limit_and_offset(self, table, columns, limit, offset):
        query = f"SELECT {', '.join(columns)} FROM {table} ORDER BY client_id LIMIT %s OFFSET %s"
        return self.connector.execute_query(query, (limit, offset), fetch=True)



class ClientRepDB:
    def __init__(self):
        self.db = DatabaseConnection()
        self.deleg_manager = Deleg(self.db)

    def get_by_id(self, client_id):
        columns = ['client_id', 'last_name', 'first_name', 'otch', 'address', 'phone']
        results = self.deleg_manager.execute_select('clients', columns, {'client_id': client_id})
        if results and len(results) > 0:
            row = results[0]
            return Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                otch=row[3],
                address=row[4],
                phone=row[5]
            )
        return None

    def add_client(self, last_name, first_name, phone, address, otch=None):
        values = {
            'last_name': last_name,
            'first_name': first_name,
            'otch': otch,
            'address': address,
            'phone': phone
        }
        self.deleg_manager.execute_insert('clients', values)
        print("Новый клиент успешно добавлен.")

    def update_client(self, client_id, updates):
        self.deleg_manager.execute_update('clients', updates, {"column": "client_id", "value": client_id})
        print(f"Клиент с ID {client_id} успешно обновлён.")

    def delete_client(self, client_id):
        self.deleg_manager.execute_delete('clients', {"column": "client_id", "value": client_id})
        print(f"Клиент с ID {client_id} успешно удалён.")

    def get_count(self):
        return self.deleg_manager.execute_count('clients')

    def get_k_n_short_list(self, k, n):
        offset = (n - 1) * k
        columns = ['client_id', 'last_name', 'first_name', 'phone', 'address']
        results = self.deleg_manager.select_with_limit_and_offset('clients', columns, k, offset)
        short_clients = [
            Client(
                client_id=row[0],
                last_name=row[1],
                first_name=row[2],
                phone=row[3],
                address=row[4]
            ).short() for row in results
        ]
        return short_clients

    def close_connection(self):
        self.db.close()



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
