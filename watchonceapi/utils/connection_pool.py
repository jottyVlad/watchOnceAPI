import queue
import sqlite3
from contextlib import contextmanager
from sqlite3 import Connection


class ConnectionPool:
    def __init__(self, max_connections, database, check_same_thread=False):
        self.max_connections = max_connections
        self.database = database
        self.check_same_thread = check_same_thread
        self.pool = queue.Queue(maxsize=max_connections)

        for _ in range(max_connections):
            conn = self.create_connection()
            self.pool.put(conn)

    def create_connection(self):
        return sqlite3.connect(self.database,
                               check_same_thread=self.check_same_thread)

    def get_connection(self, timeout) -> Connection:
        if not timeout:
            timeout = 10
        try:
            return self.pool.get(timeout=timeout)
        except queue.Empty:
            raise RuntimeError("Timeout: No available pool in the pool.")

    def release_connection(self, conn):
        self.pool.put(conn)

    @contextmanager
    def connection(self, timeout=None) -> Connection:
        conn = self.get_connection(timeout)
        try:
            yield conn
        finally:
            self.release_connection(conn)

    def close(self):
        for conn in self.pool.queue:
            conn.close()
