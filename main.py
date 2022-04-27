import os, requests, json, datetime, time

try:
    todos = requests.get('https://json.medrating.org/todos')
    users = requests.get('https://json.medrating.org/users')

    todos.raise_for_status()
    users.raise_for_status()

    todos_json = todos.json()
    users_json = users.json()
    
except HTTPError as http_err:
    print(f'Произошла ошибка HTTP: {http_err}')
except Exception as err:
    print(f'Произошла ошибка: {err}')
else:
    print('Успешное получение данных')


class TasksUser():
    """Пользователь и его задачи"""
    def __init__(self, user_id, user_name, user_company, user_full_name, user_email, 
                quantity_tasks = 0, completed_tasks = 0, notcompleted_tasks = 0, 
                list_completed_tasks = '', list_notcompleted_tasks = ''):
        self.user_id = user_id
        self.user_name = user_name
        self.user_company = user_company
        self.user_full_name = user_full_name
        self.user_email = user_email
        
        self.quantity_tasks = int(quantity_tasks)
        self.completed_tasks = int(completed_tasks)
        self.notcompleted_tasks = int(notcompleted_tasks)
        self.list_completed_tasks = list_completed_tasks
        self.list_notcompleted_tasks = list_notcompleted_tasks
        self.current_datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

    def check_quantity_tasks(self, user_id):
        """Проверяет количество задач пользователя"""
        if self.user_id == user_id:
            self.quantity_tasks += 1

    def check_long_tasks(self, formatstr):
        """Проверяет длину задачи пользователя"""
        if len(formatstr) > 48: 
            formatstr[:48]
            return f'{formatstr}... \n'
        else:
            return f'{formatstr} \n'

    def check_completed_tasks(self, completed, formatstr):
        """Проверяет выполнена ли задача пользователя"""
        if completed == True:
            self.completed_tasks += 1
            self.list_completed_tasks += self.check_long_tasks(formatstr)
        else:
            self.notcompleted_tasks += 1
            self.list_notcompleted_tasks += self.check_long_tasks(formatstr)

    def rename_file(self):
        """Переименовывает существующий файл с отчетом пользователя"""
        if os.path.exists(f'tasks/{self.user_name}.txt'):
            datetime_creation = os.path.getmtime(f'tasks/{self.user_name}.txt')
            datetime_creation = datetime.datetime.fromtimestamp(datetime_creation)
            datetime_creation_full = datetime_creation.strftime('%Y-%m-%d' + 'T' + '%H')
            datetime_creation_min = datetime_creation.strftime('%M')

            os.rename(f'tasks/{self.user_name}.txt', f'tasks/old_{self.user_name}_'
                                                     f'{datetime_creation_full}꞉'
                                                     f'{datetime_creation_min}.txt')

    def record_file(self):
        """Записывает отчет пользователя в файл"""
        if not os.path.isdir("tasks"):
            os.mkdir("tasks")

        with open(f'tasks/{self.user_name}.txt', "w+") as my_file:
            my_file.write(f'Отчет для, {self.user_company}. \n{self.user_full_name} <{self.user_email}>'
                          f'{self.current_datetime} \nОбщее количество задач: {self.quantity_tasks} \n \n'
                          f'Завершённые задачи:({self.completed_tasks}) \n{self.list_completed_tasks} \n'
                          f'Оставшиеся задачи({self.notcompleted_tasks}): \n{self.list_notcompleted_tasks}')


def create_objects_users():
    """Создает экземпляр класса для каждого пользователя"""
    objects_users = []

    for i in users_json:
        new_object = TasksUser(i['id'], i['username'], i['company']['name'], i['name'], i['email'])
        objects_users.append(new_object)

    return objects_users


def analyse_todos():
    """Анализирует задачи каждого пользователя"""
    objects_users = create_objects_users()

    for i in todos_json:
        try:
            objects_users[i['userId'] - 1].check_quantity_tasks(i['userId'])
            objects_users[i['userId'] - 1].check_completed_tasks(i['completed'], i['title'])
        except KeyError:
            pass

    return objects_users


def create_report_file():
    """Создает файл с отчетом для каждого пользователя"""
    objects_users = analyse_todos()
    
    for i in objects_users:
        i.rename_file()
        i.record_file()


if __name__ == '__main__':
    create_report_file()