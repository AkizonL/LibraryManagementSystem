import math
import sys

from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, QPointF, QTime, QTimer, QRectF
from PyQt5.QtGui import QLinearGradient, QPainter, QColor, QFont, QRadialGradient, QBrush, QPainterPath
# 导入主页面相关模块
from PyQt5.QtWidgets import QApplication, QLabel, QGraphicsBlurEffect, QMessageBox
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from qfluentwidgets import FluentIcon as FIF, Dialog
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

        self._animation_progress = 0.0  # 新增动画进度属性
        self.initAnimations()

        self.stackedWidget.setAttribute(Qt.WA_TranslucentBackground)
        # self.stackedWidget.setStyleSheet("background: transparent;")

    def initAnimations(self):
        """ 初始化背景动画 """
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.updateAnimation)
        self.anim_timer.start(16)  # ~60fps
        self.start_time = QTime.currentTime()

    def updateAnimation(self):
        """ 更新动画进度 """
        elapsed = self.start_time.msecsTo(QTime.currentTime())
        self._animation_progress = (elapsed % 15000) / 15000.0
        self.update()

    def paintEvent(self, event):
        """ 重写绘制事件 """
        # 先绘制父类背景（保留Fluent样式）
        super().paintEvent(event)

        # 添加自定义渐变层
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.drawAnimatedGradients(painter)
        painter.end()

    def drawAnimatedGradients(self, painter):
        """ 绘制五个动态渐变层（移植自LoginPage） """
        t = self._animation_progress
        size = max(self.width(), self.height())
        gradients = [
            {"color": QColor(235, 105, 78), "phase": 0.0, "sizes": [1.3, 1.0, 0.8, 0.9]},
            {"color": QColor(243, 11, 164), "phase": 0.25, "sizes": [0.8, 0.9, 1.1, 0.9]},
            {"color": QColor(254, 234, 131), "phase": 0.5, "sizes": [0.9, 1.0, 0.8, 1.0]},
            {"color": QColor(170, 142, 245), "phase": 0.75, "sizes": [1.1, 0.9, 0.6, 0.9]},
            {"color": QColor(248, 192, 147), "phase": 1.0, "sizes": [0.9, 0.6, 0.8, 0.7]}
        ]
        for grad in gradients:
            pos = self.calcGradientPosition(t + grad["phase"])
            grad_size = self.calcGradientSize(t, grad["sizes"]) * size
            self.drawGradient(painter, grad["color"], pos, grad_size)

    # 以下方法可以直接从LoginPage移植（保持相同实现）
    def calcGradientPosition(self, phase):
        angle = phase * 2 * math.pi
        x = math.cos(angle) * 0.4
        y = math.sin(angle) * 0.4
        return QPointF(
            self.width() / 2 + x * self.width(),
            self.height() / 2 + y * self.height()
        )

    def calcGradientSize(self, t, sizes):
        phases = [0, 0.25, 0.5, 0.75, 1.0]
        for i in range(len(phases) - 2):
            if phases[i] <= t < phases[i + 1]:
                return sizes[i] + (sizes[i + 1] - sizes[i]) * (t - phases[i]) * 4
        return sizes[-1] + (sizes[0] - sizes[-1]) * (t - phases[-2]) * 4

    def drawGradient(self, painter, color, center, size):
        gradient = QRadialGradient(center, size)
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, Qt.transparent)
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

    def initNavigation(self):
        self.addSubInterface(self.BookManagerInterface, FIF.BOOK_SHELF, '图书管理')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.BorrowInterface, FIF.RIGHT_ARROW, '借书管理')
        self.addSubInterface(self.ReturnInterface, FIF.CHECKBOX, '还书\续借管理')


class BlurOverlay(QWidget):
    """ 模糊效果层 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.effect = QGraphicsBlurEffect()
        self.effect.setBlurRadius(10)
        self.setGraphicsEffect(self.effect)


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self._animation_progress = 0.0
        self.initUI()
        self.initAnimations()

    def initUI(self):
        self.setWindowTitle("图书管理系统 - 登录")
        self.resize(1200, 800)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 添加模糊层
        self.blur_layer = BlurOverlay(self)
        self.blur_layer.resize(self.size())
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        # 登录卡片
        self.initLoginCard()

    def initLoginCard(self):
        # 卡片容器
        self.card = QWidget(self)
        self.card.setObjectName("loginCard")
        self.card.setFixedSize(400, 500)
        self.card.setStyleSheet("""
            #loginCard {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        # 卡片布局
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)
        # 标题
        title = QLabel("📚 图书管理系统")
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #333;
                padding-bottom: 15px;
            }
        """)
        card_layout.addWidget(title, alignment=Qt.AlignCenter)
        # 输入框
        self.username = LineEdit()
        self.password = LineEdit()
        for input_widget in [self.username, self.password]:
            input_widget.setPlaceholderText("用户名" if input_widget == self.username else "密码")
            input_widget.setFixedHeight(45)
            input_widget.setStyleSheet("""
                LineEdit {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 0 12px;
                    background: rgba(255,255,255,0.7);
                }
                LineEdit:hover { border-color: #4ecdc4; }
            """)
        self.password.setEchoMode(QLineEdit.Password)
        # 按钮
        login_btn = PrimaryPushButton("登录")
        # login_btn.setFont(QFont('Arial'))
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet("""
            PrimaryPushButton {
                background: #4ecdc4;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 500;
            }
            PrimaryPushButton:hover { background: #3dbeb5; }
            PrimaryPushButton:pressed { background: #2cad9c; }
        """)
        login_btn.clicked.connect(self.on_login_clicked)
        # 注册按钮
        register_btn = PrimaryPushButton("注册")
        register_btn.setFixedHeight(45)
        register_btn.setStyleSheet("""
            PrimaryPushButton {
                background: #ff6b6b;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 500;
            }
            PrimaryPushButton:hover { background: #ff5252; }
            PrimaryPushButton:pressed { background: #ff3838; }
        """)
        register_btn.clicked.connect(self.on_register_clicked)
        # 添加组件
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(register_btn)
        self.layout().addWidget(self.card, alignment=Qt.AlignCenter)

        exit_btn = PrimaryPushButton("退出系统")
        exit_btn.setFixedHeight(45)
        exit_btn.setStyleSheet("""
                    PrimaryPushButton {
                        background: #ff4757;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: 500;
                    }
                    PrimaryPushButton:hover { background: #ff2d3b; }
                    PrimaryPushButton:pressed { background: #ff1a2a; }
                """)
        exit_btn.clicked.connect(self.quit_application)
        # 修改布局添加顺序
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(register_btn)
        card_layout.addWidget(exit_btn)

    def quit_application(self):
        mess = Dialog("确认退出",
                      f"确认退出图书管理系统吗？")
        mess.yesButton.setText("确认")
        mess.cancelButton.setText("取消")

        if mess.exec():
            self.close()
        # QApplication.instance().quit()

    def initAnimations(self):
        """ 初始化背景动画 """
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.updateAnimation)
        self.anim_timer.start(16)  # ~60fps
        self.start_time = QTime.currentTime()

    def updateAnimation(self):
        """ 更新动画进度 """
        elapsed = self.start_time.msecsTo(QTime.currentTime())
        self._animation_progress = (elapsed % 15000) / 15000.0
        self.update()

    def paintEvent(self, event):
        """ 绘制窗口圆角和动态背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 15, 15)  # 设置15像素圆角

        # 应用剪切路径
        painter.setClipPath(path)

        # 绘制背景内容
        painter.fillRect(self.rect(), QColor("#e493d0"))
        self.drawAnimatedGradients(painter)

        # 绘制边框
        painter.setPen(QColor(255, 255, 255, 50))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 15, 15)

        painter.end()

    def drawAnimatedGradients(self, painter):
        """ 绘制五个动态渐变层 """
        t = self._animation_progress
        size = max(self.width(), self.height())

        gradients = [
            {"color": QColor(235, 105, 78), "phase": 0.0, "sizes": [1.3, 1.0, 0.8, 0.9]},
            {"color": QColor(243, 11, 164), "phase": 0.25, "sizes": [0.8, 0.9, 1.1, 0.9]},
            {"color": QColor(254, 234, 131), "phase": 0.5, "sizes": [0.9, 1.0, 0.8, 1.0]},
            {"color": QColor(170, 142, 245), "phase": 0.75, "sizes": [1.1, 0.9, 0.6, 0.9]},
            {"color": QColor(248, 192, 147), "phase": 1.0, "sizes": [0.9, 0.6, 0.8, 0.7]}
        ]
        for grad in gradients:
            pos = self.calcGradientPosition(t + grad["phase"])
            grad_size = self.calcGradientSize(t, grad["sizes"]) * size
            self.drawGradient(painter, grad["color"], pos, grad_size)

    def calcGradientPosition(self, phase):
        """ 计算渐变位置 """
        angle = phase * 2 * math.pi
        x = math.cos(angle) * 0.4
        y = math.sin(angle) * 0.4
        return QPointF(
            self.width() / 2 + x * self.width(),
            self.height() / 2 + y * self.height()
        )

    def calcGradientSize(self, t, sizes):
        """ 修复后的渐变尺寸计算方法 """
        phases = [0, 0.25, 0.5, 0.75, 1.0]

        # 确保循环在安全范围内
        for i in range(len(phases) - 2):  # 修改循环范围
            if phases[i] <= t < phases[i + 1]:
                return sizes[i] + (sizes[i + 1] - sizes[i]) * (t - phases[i]) * 4

        # 处理最后一个区间（当t >= 0.75时）
        return sizes[-1] + (sizes[0] - sizes[-1]) * (t - phases[-2]) * 4  # 循环到第一个尺寸

    def drawGradient(self, painter, color, center, size):
        """ 绘制单个渐变 """
        gradient = QRadialGradient(center, size)
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, Qt.transparent)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

    def on_login_clicked(self):
        """ 登录按钮点击事件 """
        username = self.username.text()
        password = self.password.text()
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
            self.close()
            self.main_window = Window()
            self.main_window.show()

    def on_register_clicked(self):
        """ 注册按钮点击事件 """
        InfoBar.warning(
            title="提示",
            content="暂不提供注册功能，请联系管理员",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont("Microsoft YaHei")
    app.setFont(font)

    # 全局样式
    app.setStyleSheet("""
        QToolTip {
            background-color: #333;
            color: white;
            border: none;
            padding: 5px;
            border-radius: 3px;
        }
    """)

    window = LoginPage()
    window.show()
    sys.exit(app.exec())