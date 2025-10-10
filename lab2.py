import psycopg2
from clients import Client

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

    def get_k_n_short_list(self, k, n):
        clients = self.read_all()
        start_index = (n - 1) * k
        end_index = start_index + k
        return [client.short() for client in clients[start_index:end_index]]

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
                otch=otch
            )
            clients.append(new_client)
            return new_client if self.write_all(clients) else None
        except ValueError:
            return None

    def get_count(self):
        return len(self.read_all())


class ClientRepJson(ClientRep):
    def read_all(self):
        import json
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
                        phone=item.get("phone")
                    )
                    clients.append(client)
                return clients
        except (FileNotFoundError, json.JSONDecodeError):
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
        import yaml
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

    def __new__(cls, host="localhost", user="postgres", password="123", database="clients_database", port="5432"):
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


class ClientRepDB:
    def __init__(self):
        self.db = DatabaseSingleton()

    def insert_client(self, last_name, first_name, phone, address, otch=None):
        data = {
            "last_name": last_name,
            "first_name": first_name,
            "phone": phone,
            "address": address,
            "otch": otch
        }
        columns = ", ".join(data.keys())
        znach = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO clients ({columns}) VALUES ({znach})"
        return self.db.execute_query(sql, list(data.values()))

    def update_client_fields(self, client_id, updates):
        if not updates:
            return None
        set_znach = ", ".join([f"{key} = %s" for key in updates.keys()])
        sql = f"UPDATE clients SET {set_znach} WHERE client_id = %s"
        params = list(updates.values()) + [client_id]
        return self.db.execute_query(sql, params)

    def delete_client(self, client_id):
        sql = "DELETE FROM clients WHERE client_id = %s"
        return self.db.execute_query(sql, [client_id])

    def count_clients(self):
        sql = "SELECT COUNT(*) FROM clients"
        result = self.db.execute_query(sql, fetch=True)
        return result[0][0] if result else 0

    def get_client_by_id(self, client_id):
        sql = "SELECT * FROM clients WHERE client_id = %s"
        return self.db.execute_query(sql, [client_id], fetch=True)

    def get_clients_page(self, limit, offset):
        sql = "SELECT * FROM clients ORDER BY client_id LIMIT %s OFFSET %s"
        return self.db.execute_query(sql, [limit, offset], fetch=True)

    def get_all_clients_rows(self):
        sql = "SELECT * FROM clients ORDER BY client_id"
        return self.db.execute_query(sql, fetch=True)


class ClientRepDBAdapter(ClientRep):
    def __init__(self):
        super().__init__("database")
        self.adaptee = ClientRepDB()

    def read_all(self):
        results = self.adaptee.get_all_clients_rows()
        clients = []
        for row in results:
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

    def write_all(self, clients):
        try:
            self.adaptee.execute_sql("DELETE FROM clients")
            for client in clients:
                self.adaptee.insert_client(
                    client.last_name, client.first_name,
                    client.phone, client.address, client.otch
                )
            return True
        except Exception:
            return False

    def add_client(self, last_name, first_name, phone, address, otch=None):
        try:
            client = Client(last_name, first_name, phone, address, otch)
            result = self.adaptee.insert_client(last_name, first_name, phone, address, otch)
            return client if result else None
        except ValueError:
            return None


repositories = {
    "JSON": ClientRepJson("clients.json"),
    "YAML": ClientRepYaml("clients.yaml"),
    "БД": ClientRepDBAdapter()
}

for name, repo in repositories.items():
    print(f"\n{name}:")
    print(f"Клиентов: {repo.get_count()}")

    # repo.add_client(
    #     last_name="Иванов",
    #     first_name="Иван",
    #     phone="+79169998844",
    #     address="г. Москва"
    # )

    clients = repo.get_k_n_short_list(5, 1)
    for i, client in enumerate(clients, 1):
        print(f"{i}. {client.get_info()}")
