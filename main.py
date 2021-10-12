import tornado
import sqlite3
import json
import aiopg
import tornado.locks
from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop
from tornado.options import define, options


define("port", default=8888, help="run on the given port", type=int)
define("db_host", default="127.0.0.1", help="project database host")
define("db_port", default=5432, help="project database port")
define("db_database", default="rootdb", help="project database name")
define("db_user", default="root", help="project database user")
define("db_password", default="root", help="project database password")


class Application(tornado.web.Application):
    def __init__(self, db):
        self.db = db
        handlers = [
            (r"/api/item/", MainHandler),
            (r"/api/item/([^/]+)", MainHandler),
        ]
        super().__init__(handlers)


async def create_table(db):
    try:
        with (await db.cursor()) as cur:
            await cur.execute(
                """CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, user_name TEXT, email_id TEXT, password TEXT)""")
        print("Db Connected")
    except Exception as e:
        print("Db error : ", e)


class BaseHandler(RequestHandler):
    def row_to_obj(self, row, cur):
        obj = tornado.util.ObjectDict()
        for val, desc in zip(row, cur.description):
            obj[desc.name] = val

        return obj

    async def execute(self, stmt, *args):
        with (await self.application.db.cursor()) as cur:
            await cur.execute(stmt, args)

    async def query(self, stmt, *args):
        with (await self.application.db.cursor()) as cur:
            await cur.execute(stmt, args)
            return [self.row_to_obj(row, cur) for row in await cur.fetchall()]

    async def query_one(self, stmt, *args):
        results = await self.query(stmt, *args)
        if len(results) == 0:
            raise Exception()
        elif len(results) > 1:
            raise ValueError("Expected 1 result, got %d" % len(results))
        return results[0]


class MainHandler(BaseHandler):
    async def get(self):
        try:
            entries = await self.query("SELECT * FROM users ORDER BY id")
            self.write(json.dumps(entries))
        except Exception as e:
            self.write({"Error": e})

    async def post(self):
        try:
            data = json.loads(self.request.body)
            user = await self.query_one(
                "INSERT INTO users (user_name, email_id, password) "
                "VALUES (%s, %s, %s) RETURNING id",
                data.get('user_name'),
                data.get('email_id'),
                data.get('password'),
            )
            entry = await self.query_one("SELECT * FROM users WHERE id = %s", int(user.id))
            self.write(json.dumps(entry))
        except Exception as e:
            self.write({"Error": e})

    async def patch(self, pk):
        try:
            data = json.loads(self.request.body)
            await self.execute("update users set email_id = %s WHERE id = %s", data.get('email'), pk,)
            entry = await self.query_one("SELECT * FROM users WHERE id = %s", int(pk))
            self.write(json.dumps(entry))
        except Exception as e:
            self.write({"Error": e})


async def main():
    tornado.options.parse_command_line()

    handlers = [
        (r"/api/item/", MainHandler),
        (r"/api/item/([^/]+)", MainHandler),
    ]

    async with aiopg.create_pool(host=options.db_host, port=options.db_port, user=options.db_user,
                                 password=options.db_password, dbname=options.db_database, ) as db:
        await create_table(db)
        app = Application(db)
        app.listen(port=options.port)

        shutdown_event = tornado.locks.Event()
        await shutdown_event.wait()


if __name__ == "__main__":
    IOLoop.current().run_sync(main)
