class Client:
    def __init__(self):
        self.__client_id = None
        self.__last_name = None
        self.__first_name = None
        self.__otch = None
        self.__address = None
        self.__phone = None

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
        self.__client_id = client_id
    def set_last_name(self, last_name):
        self.__last_name = last_name
    def set_first_name(self, first_name):
        self.__first_name = first_name
    def set_otch(self, otch):
        self.__otch = otch
    def set_address(self, address):
        self.__address = address
    def set_phone(self, phone):
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