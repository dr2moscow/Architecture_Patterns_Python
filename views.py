from datetime import date
from catalog import flowers
from framework.templator import render
from patterns.сreational_patterns import Engine, Logger

site = Engine()
logger = Logger('main')


class Index:
    # Просто возвращаем текст
    def __call__(self, request):
        return '200 OK', render('index.html', flowers=flowers,
                                select_menu1='selected', select_menu='selected', date=request.get('date', None))


class About:
    # Возвращаем разделы каталога
    def __call__(self, request):
        return '200 OK', render('about.html', objects_list=site.categories, select_menu2='selected', date=request.get('date', None))


class Contact:
    # Просто возвращаем текст
    def __call__(self, request):
        return '200 OK', render('contact.html', select_menu3='selected', date=request.get('date', None))


class NotFound404:
    # контроллер 404
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


# контроллер - букеты
class Bouquets:
    def __call__(self, request):
        return '200 OK', render('bouquets.html', select_menu2='selected', date=date.today())


# контроллер - список букетов
class BouquetList:
    def __call__(self, request):
        logger.log('Список букетов')

        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('bouquet_list.html',
                                    objects_list=category.bouquets, select_menu2='selected',
                                    name=category.name, id=category.id, date=date.today())
        except KeyError:
            return '200 OK', 'No bouquets have been added yet'


# контроллер - создать букет
class CreateBouquet:
    category_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                bouquet = site.create_bouquet('record', name, category)
                site.bouquets.append(bouquet)

            return '200 OK', render('bouquet_list.html',
                                    objects_list=category.bouquets, select_menu2='selected',
                                    name=category.name,
                                    id=category.id, date=date.today())

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_bouquet.html', select_menu2='selected',
                                        name=category.name,
                                        id=category.id, date=date.today())
            except KeyError:
                return '200 OK', 'No categories have been added yet'


# контроллер - создать категорию
class CreateCategory:
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('about.html', objects_list=site.categories, select_menu2='selected',
                                    date=date.today())
        else:
            categories = site.categories
            return '200 OK', render('create_category.html', select_menu2='selected',
                                    categories=categories, date=date.today())


# контроллер - список категорий
class CategoryList:
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', select_menu2='selected',
                                objects_list=site.categories, date=date.today())


# контроллер - копировать букет
class CopyBouquet:
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_bouquet = site.get_bouquet(name)
            if old_bouquet:
                new_name = f'{name}_copy'
                new_bouquet = old_bouquet.clone()
                new_bouquet.name = new_name
                site.bouquets.append(new_bouquet)

            return '200 OK', render('bouquet_list.html', objects_list=site.bouquets,
                                    name=new_bouquet.category.name, date=date.today())
        except KeyError:
            return '200 OK', 'No bouquets have been added yet'
