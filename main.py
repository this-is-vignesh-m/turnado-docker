from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop
# import asyncmongo
import sqlite3
import json

conn = sqlite3.connect('docker_db.db')
c = conn.cursor()

items = []

try:
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT)''')
except sqlite3.OperationalError:
    pass

# class MyApp(Application):
#     def __init__(self, *args, **kwargs):
#         super(MyApp, self).__init__(*args, **kwargs)
#         # or even initilaize connection
#         self._db = None

#     @property
#     def db(self):
#         if self._db is None:
#             # self._db = asyncmongo.Client(pool_id='mydb', host='127.0.0.1', port=27017, maxcached=10, maxconnections=50, dbname='test')
#             self._db = asyncmongo.Client(
#                 host='127.0.0.1', port=27017, dbname='test', maxcached=10, maxconnections=50)
#         # additionally you can check here if session is time-outed or something
#         return self._db


class MainHandler(RequestHandler):
    def get(self):
        try:
            c.execute('select * from users')
            res = c.fetchall()

            resultat = {}
            for x, y in enumerate(res):
                result = {}
                for i, j in zip(c.description, y):
                    result[i[0]] = j
                resultat[f"user{x}"] = result

            self.write(resultat)
        except Exception as e:
            self.write(e)

    def post(self):
        try:
            data = json.loads(self.request.body)
            user_name = data.get('user_name')
            email_id = data.get('email')
            password = data.get('password')
            c.execute("insert into users (name, email, password) values (?, ?, ?)",
                      (user_name, email_id, password))
            conn.commit()

            c.execute('select * from users where id = ?', (c.lastrowid,))
            res = c.fetchone()
            print(c.description)
            resultat = {}
            for i, j in zip(c.description, res):
                resultat[i[0]] = j
            self.write(resultat)
        except Exception as e:
            self.write(e)

    def patch(self, pk):
        try:
            data = json.loads(self.request.body)
            email_id = data.get('email')
            c.execute("update users set email = ? WHERE id = ?",(email_id, pk))
            conn.commit()

            c.execute('select * from users where id = ?', (pk,))
            res = c.fetchone()
            print(c.description)
            resultat = {}
            for i, j in zip(c.description, res):
                resultat[i[0]] = j
            self.write(resultat)
        except Exception as e:
            self.write(e)


def make_app():
    urls = [
        (r"/api/item/", MainHandler),
        (r"/api/item/([^/]+)", MainHandler),
    ]
    return Application(urls, debug=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()
