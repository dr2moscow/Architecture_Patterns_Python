from datetime import date
from views import Index, About, Contact, Bouquets, BouquetList, \
    CreateBouquet, CreateCategory, CategoryList, CopyBouquet


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/about/': About(),
    '/contact/': Contact(),
    '/bouquet-list/': BouquetList(),
    '/create-bouquet/': CreateBouquet(),
    '/create-category/': CreateCategory(),
    '/category-list/': CategoryList(),
    '/copy-bouquet/': CopyBouquet()
}
