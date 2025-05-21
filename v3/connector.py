import mysql.connector
from mysql.connector import Error


class DBConnector:
    # 单例模式，确保任何时候只有一个连接，节省资源
    _instance = None

    def __new__(cls, config):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.config = config
            cls._instance.connection = None
        return cls._instance

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            return self.connection
        except Error as e:
            print(f"数据库连接失败: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection and self.connection.is_connected():
            self.connection.close()


# 数据库配置
db_config = {
    "host": "localhost",
    "database": "librarydatabase",
    "user": "root",
    "password": "114514"
}
