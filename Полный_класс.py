import re
import json

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
    def is_valid_id(id):
        return id is not None and id > 0

    @staticmethod
    def is_valid_name(name):
        return name is not None and re.match(r'^[А-Яа-яЁё\s]+$', name) is not None

    @staticmethod
    def is_valid_phone(phone):
        return phone is not None and re.match(r'^\+\d{11}$', phone) is not None

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
            raise ValueError("Номер телефона должен начинаться с '+' и содержать 11 цифр, а также не быть пустым")
        self.__phone = phone

    def get_info(self):
        return f"ФИ: {self.last_name} {self.first_name[0]}., Телефон: {self.phone}"


class Client(ShortClient):
    def __init__(self, client_id=None, last_name=None, first_name=None, otch=None, address=None, phone=None, data=None):
        super().__init__(client_id, last_name, first_name, phone)
        self.__otch = None
        self.__address = None

        if data is not None:
            self.from_str(data)
        elif client_id is not None and last_name is not None and first_name is not None and phone is not None:
            self.set_otch(otch)
            self.set_address(address)

    @property
    def otch(self):
        return self.__otch

    @property
    def address(self):
        return self.__address

    def set_otch(self, otch):
        if otch and otch.strip() != "":
            if not re.match(r'^[А-Яа-яЁё\s]+$', otch):
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
            self.set_client_id(data_dict["client_id"])
            self.set_last_name(data_dict["last_name"])
            self.set_first_name(data_dict["first_name"])
            self.set_otch(data_dict["otch"])
            self.set_address(data_dict["address"])
            self.set_phone(data_dict["phone"])
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
            phone=self.phone
        )

    def get_long_info(self):
        otch_info = f", Отчество: {self.otch}" if self.otch else ""
        return (f"client_id={self.client_id}, Фамилия: {self.last_name}, "
                f"Имя: {self.first_name}{otch_info}, "
                f"Адрес: {self.address}, Телефон: {self.phone}")

    def __eq__(self, other):
        if not isinstance(other, Client):
            return False
        return (self.client_id == other.client_id and
                self.last_name == other.last_name and
                self.first_name == other.first_name and
                self.otch == other.otch and
                self.address == other.address and
                self.phone == other.phone)


print("\nКонструктор с параметрами:")
client1 = Client(client_id=12, last_name="Иванов", first_name="Иван",
                 otch="Иванович", address="г.Краснодар, ул. Садовая 2",
                 phone="+74185693025")
print(client1.get_long_info())
print("\nКороткая версия:")
print(client1.short().get_info())

print("\nКонструктор из строки:")
client2 = Client(data="13,Сидорова,Анна,Владимировна,г.Пятигорск,+71524698208")
print(client2.get_long_info())

print("\nКонструктор из json:")
json_str = (
    '{"client_id": 74, '
    '"last_name": "Кошкин", '
    '"first_name": "Кошка", '
    '"otch": "Кошкович", '
    '"address": "г.Ставрополь", '
    '"phone": "+72036987456"}'
)
client3 = Client(data=json_str)
print(client3.get_long_info())


print("\nРавны объекты?")
print("client1 == client2:", client1 == client2)
print("client2 == client3:", client2 == client3)
