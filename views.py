from datetime import date
from catalog import flowers
from framework.templator import render
from patterns.сreational_patterns import Engine, Logger
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, ListView, CreateView, \
    BaseSerializer, FileWriter

site = Engine()
logger = Logger('main', FileWriter())
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()

routes = {}


# контроллер - главная страница
@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', flowers=flowers, objects_list=site.categories,
                                select_menu1='selected', select_menu='selected', date=request.get('date', None))


# контроллер "Каталог"
@AppRoute(routes=routes, url='/catalog/')
class Catalog:
    @Debug(name='Catalog')
    def __call__(self, request):
        return '200 OK', render('catalog.html',  objects_list=site.categories, select_menu2='selected',
                                date=request.get('date', None))


# контроллер "Покупатели"
@AppRoute(routes=routes, url='/buyers/')
class Catalog:
    @Debug(name='Buyers')
    def __call__(self, request):
        return '200 OK', render('buyers.html',  objects_list=site.categories, select_menu2='selected',
                                date=request.get('date', None))


# контроллер "Контакты"
@AppRoute(routes=routes, url='/contact/')
class Contact:
    @Debug(name='Contact')
    def __call__(self, request):
        return '200 OK', render('contact.html',  objects_list=site.categories, select_menu4='selected',
                                date=request.get('date', None))


# контроллер 404
class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


# контроллер - букеты
class Bouquets:
    def __call__(self, request):
        return '200 OK', render('catalog.html', select_menu2='selected', date=date.today())


# контроллер - список букетов
@AppRoute(routes=routes, url='/bouquet-list/')
class BouquetList:
    @Debug(name='BouquetList')
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
@AppRoute(routes=routes, url='/create-bouquet/')
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

                bouquet.observers.append(email_notifier)
                bouquet.observers.append(sms_notifier)

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
@AppRoute(routes=routes, url='/create-category/')
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

            return '200 OK', render('catalog.html', objects_list=site.categories, select_menu2='selected',
                                    date=date.today())
        else:
            categories = site.categories
            return '200 OK', render('create_category.html', select_menu2='selected',
                                    categories=categories, date=date.today())


# контроллер - список категорий
@AppRoute(routes=routes, url='/category-list/')
class CategoryList:
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', select_menu2='selected',
                                objects_list=site.categories, date=date.today())


# контроллер - копировать букет
@AppRoute(routes=routes, url='/copy-bouquet/')
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


@AppRoute(routes=routes, url='/buyers-list/')
class BuyerListView(ListView):
    queryset = site.buyers
    logger.log('Список покупателей')
    template_name = 'buyers-list.html'


@AppRoute(routes=routes, url='/create-buyer/')
class BuyerCreateView(CreateView):
    template_name = 'create_buyer.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('buyer', name)
        site.buyers.append(new_obj)


@AppRoute(routes=routes, url='/add-buyer/')
class AddBuyerByBouquetCreateView(CreateView):
    template_name = 'add_buyer.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['bouquets'] = site.bouquets
        context['buyers'] = site.buyers
        return context

    def create_obj(self, data: dict):
        bouquet_name = data['bouquet_name']
        print(bouquet_name)
        bouquet_name = site.decode_value(bouquet_name)
        bouquet = site.get_bouquet(bouquet_name)
        buyer_name = data['buyer_name']
        buyer_name = site.decode_value(buyer_name)
        buyer = site.get_buyer(buyer_name)
        bouquet.add_buyer(buyer)


@AppRoute(routes=routes, url='/api/')
class BouquetApi:
    @Debug(name='BouquetApi')
    def __call__(self, request):
        logger.log('Вызов API')
        return '200 OK', BaseSerializer(site.bouquets).save()
