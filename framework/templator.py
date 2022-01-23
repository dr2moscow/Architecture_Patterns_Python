from jinja2 import Template
from os.path import join


def render(template_name, folder='templates', **kwargs):
    """
    Минимальный пример работы с шаблонизатором
    :param template_name: имя шаблона
    :param folder: папка в которой ищем шаблон
    :param kwargs: параметры для передачи в шаблон
    :return:
    """
    # Открываем шаблон по имени
    file_path = join(folder, template_name)
    with open(file_path, encoding='utf-8') as f:
        # Читаем
        template = Template(f.read())

    # рендерим шаблон с параметрами
    return template.render(**kwargs)
