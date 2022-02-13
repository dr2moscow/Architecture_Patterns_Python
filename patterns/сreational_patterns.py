from copy import deepcopy
from quopri import decodestring
from sqlite3 import connect
from patterns.architectural_system_pattern_unit_of_work import DomainObject
from patterns.behavioral_patterns import FileWriter, Subject


# абстрактный пользователь
class User:
    def __init__(self, name):
        self.name = name


# цветок
class Flower(User):
    pass


# покупатель
class Buyer(User, DomainObject):

    def __init__(self, name):
        self.bouquets = []
        super().__init__(name)


# порождающий паттерн Абстрактная фабрика - фабрика пользователей
class UserFactory:
    types = {
        'buyer': Buyer,
        'flower': Flower
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name):
        return cls.types[type_](name)


# порождающий паттерн Прототип
class BouquetPrototype:
    # прототип букетов

    def clone(self):
        return deepcopy(self)


class Bouquet(BouquetPrototype, Subject):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.bouquets.append(self)
        self.buyers = []
        super().__init__()

    def __getitem__(self, item):
        return self.buyers[item]

    def add_buyer(self, buyer: Buyer):
        self.buyers.append(buyer)
        buyer.bouquets.append(self)
        self.notify()


# интерактивный букет
class InteractiveBouquet(Bouquet):
    pass


# букет в записи
class RecordBouquet(Bouquet):
    pass


# категория
class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.bouquets = []

    def bouquet_count(self):
        result = len(self.bouquets)
        if self.category:
            result += self.category.bouquet_count()
        return result

    @classmethod
    def create(cls, name, category):
        return cls.name(category)


# порождающий паттерн Абстрактная фабрика
class BouquetFactory:
    types = {
        'interactive': InteractiveBouquet,
        'record': RecordBouquet
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](name, category)


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.flowers = []
        self.buyers = []
        self.bouquets = []
        self.categories = []

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_bouquet(type_, name, category):
        return BouquetFactory.create(type_, name, category)

    def get_bouquet(self, name):
        for item in self.bouquets:
            if item.name == name:
                return item
        return None

    def get_buyer(self, name) -> Buyer:
        for item in self.buyers:
            if item.name == name:
                return item

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name, writer=FileWriter()):
        self.name = name
        self.writer = writer

    def log(self, text: object) -> object:
        """
        Логируем действия

        :rtype: object
        """
        text = f'log---> {text}'
        self.writer.write(text)


class BuyerMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'buyer'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            buyer = Buyer(name)
            buyer.id = id
            result.append(buyer)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Buyer(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = connect('patterns.sqlite')


# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    mappers = {
        'buyer': BuyerMapper,
    }

    @staticmethod
    def get_mapper(obj):

        if isinstance(obj, Buyer):

            return BuyerMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
