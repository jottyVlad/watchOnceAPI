import queue
import aiosqlite
from contextlib import contextmanager
from aiosqlite import Connection


class ConnectionPool:
    pool: queue.Queue
    max_connections: int
    database: str

    @classmethod
    async def create(cls, max_connections: int, database: str):
        pool = cls()
        pool.max_connections = max_connections
        pool.database = database
        pool.pool = queue.Queue(maxsize=max_connections)

        for _ in range(max_connections):
            conn = await pool.create_connection()
            pool.pool.put(conn)

        return pool

    async def create_connection(self):
        return await aiosqlite.connect(self.database)

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

    async def close(self):
        for conn in self.pool.queue:
            await conn.close()
