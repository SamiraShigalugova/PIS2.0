import re
import json

class ShortClient():
    def __init__(self, client_id, last_name, first_name, otch = None, phone = None):
        self.__client_id = client_id
        self.__last_name = last_name
        self.__first_name = first_name
        self.__otch = otch
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
    def otch(self):
        return self.__otch

    @property
    def phone(self):
        return self.__phone

    def get_info(self):
        return f"{self.last_name} {self.__first_name} {self.__otch} {self.__phone}"

class Client:
    def __init__(self, client_id=None, last_name=None, first_name=None, otch=None, address=None, phone=None, data=None):
        self.__client_id = None
        self.__last_name = None
        self.__first_name = None
        self.__otch = None
        self.__address = None
        self.__phone = None
        if data is not None:
            self.from_str(data)
        elif client_id is not None and last_name is not None and first_name is not None and otch is not None and address is not None and phone is not None:
            self.set_client_id(client_id)
            self.set_last_name(last_name)
            self.set_first_name(first_name)
            self.set_otch(otch)
            self.set_address(address)
            self.set_phone(phone)
    @staticmethod
    def is_valid_id(id):
        return id is not None and id > 0

    @staticmethod
    def is_valid_name(name):
        return name is not None and re.match(r'^[А-Яа-яЁё]+$', name) is not None

    @staticmethod
    def is_valid_otch(otch):
        return otch is None or otch == "" or re.match(r'^[А-Яа-яЁё]+$', otch) is not None

    @staticmethod
    def is_valid_phone(phone):
        return phone is not None and re.match(r'^\+\d{11}$', phone) is not None

    @staticmethod
    def is_valid_address(address):
        return address is not None and address.strip() != ""

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
    def otch(self):
        return self.__otch

    @property
    def address(self):
        return self.__address

    @property
    def phone(self):
        return self.__phone



    def set_client_id(self, client_id):
        if not Client.is_valid_id(client_id):
            raise ValueError("ID клиента должно быть положительным числом")
        self.__client_id = client_id

    def set_last_name(self, last_name):
        if not Client.is_valid_name(last_name):
            raise ValueError("Фамилия должна содержать только буквы и не буть пустой")
        self.__last_name = last_name

    def set_first_name(self, first_name):
        if not Client.is_valid_name(first_name):
            raise ValueError("Имя должно содержать только буквы и не быть пустым")
        self.__first_name = first_name

    def set_otch(self, otch):
        if not Client.is_valid_otch(otch):
            raise ValueError("Отчество должно содержать только буквы")
        self.__otch = otch

    def set_address(self, address):
        if not self.is_valid_address(address):
            raise ValueError("Адрес не должен быть пустым")
        self.__address = address

    def set_phone(self, phone):
        if not Client.is_valid_phone(phone):
            raise ValueError("Номер телефона должен начинаться с '+' и содержать 11 цифр, а также не быть пустым")
        self.__phone = phone



    def from_str(self, data):
        data = data.strip()
        if data.startswith("{"):
            data_dict = json.loads(data)
            self.set_client_id(data_dict["clientId"])
            self.set_last_name(data_dict["lastName"])
            self.set_first_name(data_dict["firstName"])
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

    def get_long_info(self):
        return (f"(client_id={self.client_id}, Фамилия: '{self.last_name}', "
                f"Имя: '{self.first_name}', Отчество: '{self.otch}', "
                f"Адрес: '{self.address}', Телефон: '{self.phone}')")


    def __eq__(self, other):
        if not isinstance(other, Client):
            return False
        return (self.client_id == other.client_id and
                self.last_name == other.last_name and
                self.first_name == other.first_name and
                self.otch == other.otch and
                self.address == other.address and
                self.phone == other.phone)
    def short(self):
        return ShortClient(
            client_id=self.client_id,
            last_name=self.last_name,
            first_name=self.first_name,
            otch=self.otch,
            phone=self.phone
        )








print("\nКонструктор с параметрами: ")
client1 = Client(client_id=12, last_name="Иванов", first_name="Иван", otch="Иванович", address="г.Краснодар, ул. Садовая 2", phone="+74185693025")
print("Полная версия: ", client1.get_long_info())
client_short = client1.short()
print("Краткая версия:")
print(client_short.get_info())
print("\nКонструктор из строки: ")
client2 = Client(data="13,Сидорова,Анна,Владимировна,Пятигорск,+71524698208")
print(client2.get_long_info())
print("\nКонструктор из json: ")
str = (
    '{"clientId": 74, '
    '"lastName": "Кошкин", '
    '"firstName": "Кошка", '
    '"otch": "Кошкович", '
    '"address": "г.Ставрополь", '
    '"phone": "+72036987456"}'
)
client3 = Client(data=str)
print(client3.get_long_info())
print("\nРавны ли объекты?")
print("client1 == client2:", client1 == client2)
print("client1 == client3:", client1 == client3)
print("client2 == client3:", client2 == client3)


