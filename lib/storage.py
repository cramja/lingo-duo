import sqlite3
from time import time


def time_ms():
    return int(time() * 1000.0)


class SessionStorage(object):

    def __init__(self, db="session.db"):
        self.db = db
        self._init_db()

    def _get_c(self):
        c = sqlite3.connect(self.db)
        c.row_factory = sqlite3.Row
        return c

    @staticmethod
    def _replace_c(c):
        c.commit()
        c.close()

    def _init_db(self):
        c = self._get_c()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS session (
                id VARCHAR PRIMARY KEY,
                create_time INTEGER NOT NULL,
                access_time INTEGER NOT NULL,
                state VARCHAR NOT NULL
            );
            """)
        self._replace_c(c)

    def put_session(self, id, state):
        c = self._get_c()
        s_tpl = self._get_session_tpl(c, id)
        if s_tpl is not None:
            self._update_session(c, id, state)
        else:
            self._create_session(c, id, state)
        self._replace_c(c)

    def remove_session(self, id):
        c = self._get_c()
        c.execute("DELETE FROM session WHERE id = ?", (id,))
        self._replace_c(c)

    def get_session(self, id):
        if id is None:
            return None

        c = self._get_c()
        tpl = self._get_session_tpl(c, id)
        self._replace_c(c)
        if tpl is not None:
            return tpl['state']
        return None

    def _update_session(self, c, id, state):
        c.execute("UPDATE session SET state = ?, access_time = ? WHERE id = ?", (state, time_ms(), id,))

    def _create_session(self, c, id, state):
        c.execute("INSERT INTO session (id, create_time, access_time, state) VALUES (?,?,?,?)",
                  (id, time_ms(), time_ms(), state,))

    def _get_session_tpl(self, c, id):
        cr = c.execute("SELECT * FROM session WHERE id = ?", (id,))
        s = cr.fetchone()
        if s is not None:
            c.execute("UPDATE session SET access_time = ? WHERE id = ?", (time_ms(), id))
            return s
        return None
