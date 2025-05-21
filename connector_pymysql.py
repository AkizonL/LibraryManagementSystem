import pymysql
from pymysql import Error
from pymysql.connections import Connection


class DBConnector:
    """使用pymysql实现的保持原接口的数据库连接器"""
    _instance = None

    def __new__(cls, config):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # 转换参数名为pymysql兼容格式
            cls._instance.config = {
                "host": config["host"],
                "user": config["user"],
                "password": config["password"],
                "db": config["database"],  # pymysql使用db参数
                "charset": "utf8mb4",
                "cursorclass": pymysql.cursors.DictCursor
            }
            cls._instance.connection = None
        return cls._instance

    def __enter__(self) -> Connection:
        try:
            self.connection = pymysql.connect(**self.config)
            return self.connection
        except Error as e:
            print(f"数据库连接失败: {e}")
            raise
        except KeyError as e:
            print(f"配置参数错误: {e}")
            raise ValueError("无效的数据库配置") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection and self.connection.open:
            self.connection.close()
            # 重置连接状态避免僵尸连接
            self.connection = None


# 保持原有配置结构不变
db_config = {
    "host": "localhost",
    "database": "lrx",  # 自动转换为pymysql的db参数
    "user": "root",
    "password": "114514"
}
