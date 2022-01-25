from datetime import date
import views


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

routes = {
    '/': views.Index,
    '/about/': views.About,
    '/contact/': views.Contact
}
