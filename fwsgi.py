from wsgiref.simple_server import make_server


def index_view(request):
    print(request)
    return '200 OK', [b'Index']


def abc_view(request):
    print(request)
    return '200 OK', [b'ABC']


def not_found_404_view(request):
    print(request)
    return '404 WHAT', [b'404 PAGE Not Found']


class Other:

    def __call__(self, request):
        print(request)
        return '200 OK', [b'<h1>other</h1>']


routes = {
    '/': index_view,
    '/abc/': abc_view,
    '/other/': Other()
}


def secret_front(request):
    request['secret'] = 'some secret'


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]


class Application:

    def __init__(self, routes, fronts):
        self.routes = routes
        self.fronts = fronts

    def __call__(self, environ, start_response):

        path = environ['PATH_INFO']
        if path in self.routes:
            view = self.routes[path]
        else:
            view = not_found_404_view
        request = {}
        # front controller
        for front in self.fronts:
            front(request)
        print(request)
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return body


application = Application(routes, fronts)

with make_server('', 8000, application) as httpd:
    print("Serving on port 8000...")
    httpd.serve_forever()
