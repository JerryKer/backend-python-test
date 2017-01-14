"""
This module contains all models related to database.
It will be much easier to use Flask-SQLalchemy, instead I want to demonstrate my coding ability.
I notice for the user password is not encrypted. We could include FlaskwTF to include CSRF token for all forms.
"""

from flask import g


class DbModel:
    """
    Common tools calls for the table
    """
    table = None

    def __init__(self, table_name):
        self.table = table_name

    def get_by_id(self, id):
        cur = g.db.execute("SELECT * FROM '%s' WHERE id ='%s'" % (self.table, id))
        args = cur.fetchone()

        if not args:
            return None

        return args

    def all(self):
        cur = g.db.execute("SELECT * FROM " + self.table)

        return cur.fetchall()

    def delete(self, id):
        if id:
            g.db.execute("DELETE FROM '%s' WHERE id ='%s'" % (self.table, id))
            g.db.commit()

            return True

        return False


class User(DbModel):
    table = 'users'

    id = None
    username = None
    password = None

    def __init__(self, args=None):
        DbModel.__init__(self, self.table)

        if args:
            self.id = args[0]
            self.username = args[1]
            self.password = args[2]

    def get_users_list(self):
        """
        Give a list of all user into objects
        :return: list of user
        """
        return [User(t) for t in self.all()]

    @staticmethod
    def get_user(username, password):

        if not username and not password:
            return None

        sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
        cur = g.db.execute(sql % (username, password))
        user = cur.fetchone()

        return user


class Todo(DbModel):
    table = 'todos'

    id = None
    description = None
    status = None
    user_id = None

    def __init__(self, args=None):
        DbModel.__init__(self, self.table)

        if args:
            self.id = args[0]
            self.description = args[2]
            self.status = args[3]
            self.user_id = args[1]

    def get_todos_list(self):
        """
        Give a list of todo into objects
        :return:
        """
        return [Todo(t) for t in self.all()]

    def add(self, user_id, description, status):
        if user_id and description and status is not None:
            g.db.execute(
                "INSERT INTO '%s' (user_id, description, status) VALUES ('%s', '%s', '%s')"
                % (self.table, user_id, description, status)
            )

            g.db.commit()
            print "test"
            return True
        return False


class Pagination:
    total_pages = None
    limit = None
    current_page = 1

    dbmodel = None

    def __init__(self, dbmodel, limit, current_page=1):
        if current_page > 0:
            self.current_page = current_page

        self.limit = limit
        self.dbmodel = dbmodel
        self.total_pages = self.get_total_pages(dbmodel)

    def get_total_pages(self, dbmodel):
        number_pages = 0

        if not dbmodel:
            return 0

        if dbmodel:
            total_pages = len(dbmodel.all())

            if self.limit and total_pages > 0:
                if total_pages % self.limit > 0:
                    number_pages += 1

                number_pages += (total_pages / self.limit)

        return number_pages

    def get_current_items(self):
        if self.total_pages == 1:
            return self.dbmodel.all()

        if self.current_page > 0:
            offset = (self.current_page - 1) * self.limit
            cur = g.db.execute("SELECT * FROM '%s' LIMIT '%s' OFFSET '%s'" % (
                self.dbmodel.table, self.limit, offset))

            return cur

        return []