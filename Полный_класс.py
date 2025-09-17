import re
class Client:
    def __init__(self):
        self.__client_id = None
        self.__last_name = None
        self.__first_name = None
        self.__otch = None
        self.__address = None
        self.__phone = None

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

client = Client()
client.set_client_id(1230)
client.set_last_name("Шигалугова")
client.set_first_name("Самира")
client.set_otch("Беслановна")
client.set_address("Нальчик")
client.set_phone("+78965478850")
print("ID клиента:", client.client_id)
print("Фамилия:", client.last_name)
print("Имя:", client.first_name)
print("Отчество:", client.otch)
print("Адрес:", client.address)
print("Телефон:", client.phone)
