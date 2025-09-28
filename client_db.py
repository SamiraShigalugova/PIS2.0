import psycopg2
from Clients import Client


class ClientRepDB:
    def __init__(self, host="localhost", user="postgres", password="", database="clients_db", port="5432"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.connect()

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


    def get_by_id(self, client_id):
        query = "SELECT client_id, last_name, first_name, otch, address, phone FROM clients WHERE client_id = %s"
        result = self.execute_query(query, (client_id,), fetch=True)

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
        result = self.execute_query(query, (k, offset), fetch=True)

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




repo_db = ClientRepDB(
    host="localhost",
    user="postgres",
    password="123",
    database="clients_database",
    port="5432"
)
print("\nПоиск клиента по ID:")
client = repo_db.get_by_id(2)
if client:
    print(f"Найден клиент: {client.get_long_info()}")
print("\nВыборка клиентов:")
short_clients = repo_db.get_k_n_short_list(k=3, n=1)
for i, short_client in enumerate(short_clients, 1):
    print(f"{i}. {short_client.get_info()}")
