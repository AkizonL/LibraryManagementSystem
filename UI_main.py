import sys

from PyQt5.QtCore import Qt
# 导入主页面相关模块
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import FluentWindow
from qfluentwidgets import InfoBar, InfoBarPosition, LineEdit, BodyLabel, PrimaryPushButton

from BookManagerInterface import BookManagerInterface
from BorrowInterface import BorrowInterface
from ReturnInterface import ReturnInterface
from connector_pymysql import DBConnector, db_config


class Window(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        self.BookManagerInterface = BookManagerInterface('BookManagerInterface', self)
        self.BorrowInterface = BorrowInterface('BorrowInterface', self)
        self.ReturnInterface = ReturnInterface('ReturnInterface', self)

        self.initNavigation()
        self.navigationInterface.setExpandWidth(160)
        self.navigationInterface.setCollapsible(False)
        self.resize(1450, 900)

    def initNavigation(self):
        self.addSubInterface(self.BookManagerInterface, FIF.BOOK_SHELF, '图书管理')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.BorrowInterface, FIF.RIGHT_ARROW, '借书管理')
        self.addSubInterface(self.ReturnInterface, FIF.CHECKBOX, '还书\续借管理')


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口标题
        self.setWindowTitle("登录页面")
        self.resize(1200, 800)

        # 创建布局
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 标题
        title_label = BodyLabel("欢迎登录")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 用户名输入框
        self.username_input = LineEdit(self)
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFixedWidth(300)
        layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # 密码输入框
        self.password_input = LineEdit(self)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(300)
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # 登录按钮
        login_button = PrimaryPushButton("登录", self)
        login_button.setFixedWidth(300)
        login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # 注册按钮
        register_button = PrimaryPushButton("注册", self)
        register_button.setFixedWidth(300)
        register_button.clicked.connect(self.on_register_clicked)
        layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # 设置布局
        self.setLayout(layout)

    def on_login_clicked(self):
        """ 登录按钮点击事件 """
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            InfoBar.error(
                title="错误",
                content="用户名和密码不能为空",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=2000
            )
        else:
            try:
                with DBConnector(db_config) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT * FROM admins WHERE username = %s AND password = %s",
                        (username, password))
                    if cursor.fetchone():
                        InfoBar.success(
                            title="登录成功",
                            content=f"欢迎回来，{username}！",
                            parent=self,
                            position=InfoBarPosition.TOP,
                            duration=2000
                        )
                        self.close()  # 关闭登录页面
                        self.show_main_window()  # 打开主页面
                    else:
                        InfoBar.error(
                            title="错误",
                            content="用户名或密码错误",
                            parent=self,
                            position=InfoBarPosition.TOP,
                            duration=2000
                        )
            except Exception as e:
                InfoBar.error(
                    title="错误",
                    content=f"数据库错误：{e}",
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=2000
                )

    def show_main_window(self):
        """ 显示主页面 """
        self.main_window = Window()
        self.main_window.show()

    def on_register_clicked(self):
        """ 注册按钮点击事件 """
        InfoBar.warning(
            title="提示",
            content="暂不提供注册功能,注册请联系数据库管理员",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建登录页面
    login_page = LoginPage()
    login_page.show()

    sys.exit(app.exec())
