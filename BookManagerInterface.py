import sys

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView, QApplication, QTableView, QGridLayout
)
from qfluentwidgets import TableWidget, LineEdit, PrimaryToolButton, FluentIcon, PrimaryPushButton, BodyLabel, \
    PushButton, InfoBar, InfoBarPosition, Dialog, Action, RoundMenu

from books import BookManager
from connector_pymysql import DBConnector, db_config


class Worker(QThread):
    result_ready = pyqtSignal(list, list)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        print("子线程创建")

    def run(self):
        try:
            print("Worker thread started")
            columns, books = BookManager().select_all_book()

            sorted_books = sorted(books, key=lambda book: book.get('shelves', 1), reverse=True)

            print("Query completed with shelves-sorted results")
            self.result_ready.emit(columns, sorted_books)
        except Exception as e:
            print(f"Worker thread error: {str(e)}")
            # self.result_ready.emit([], [])


class BookManagerInterface(QWidget):
    # 更新表格信号
    search_result_ready = pyqtSignal(list, list)
    show_success_delete_InfoBars = pyqtSignal(bool, str)

    def __init__(self, text: str, parent=None):
        super().__init__()
        self.initUI()
        # 更新表格信号
        self.search_result_ready.connect(self.update_table)
        self.setObjectName(text.replace(' ', '-'))

    def initUI(self):
        self.show_success_delete_InfoBars.connect(self.show_success_delete_InfoBar)
        # 初始化UI布局
        # 总垂直布局
        vBoxLayout = QVBoxLayout(self)  # 将布局设置为窗口的主布局

        # 搜索和按钮
        hBoxLayout1 = QHBoxLayout()
        le1 = LineEdit()
        le1.textChanged.connect(self.search_books)
        le1.setPlaceholderText("搜索ISBN码或者书名")
        ptbtn1 = PrimaryToolButton()
        ptbtn1.setIcon(FluentIcon.SEARCH)
        ppbtn1 = PrimaryPushButton()
        ptbtn2 = PrimaryToolButton()
        ptbtn2.setIcon(FluentIcon.SYNC)
        ptbtn2.clicked.connect(self.search_books)
        ppbtn1.setIcon(FluentIcon.ADD)
        ppbtn1.setText("添加图书")
        ppbtn1.clicked.connect(self.add_book_window)
        hBoxLayout1.addWidget(le1)
        hBoxLayout1.addWidget(ptbtn1)
        hBoxLayout1.addWidget(ptbtn2)
        hBoxLayout1.addWidget(ppbtn1)

        # 启动子线程加载数据
        self.worker = Worker(parent=self)
        self.worker.result_ready.connect(self.update_table)  # 连接信号和槽
        self.worker.start()  # 启动线程

        # 表格
        hBoxLayout2 = QHBoxLayout()
        self.tableView = TableWidget()
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.show_context_menu)
        self.tableView.setSortingEnabled(True)  # 原生排序
        hBoxLayout2.addWidget(self.tableView)

        # 设置表格属性
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(5)
        self.tableView.setHorizontalHeaderLabels(['ISBN', '书名', '分类', '库存', '上架状态'])
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自动拉伸
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)  # 禁用直接编辑

        # 将布局添加到主布局
        vBoxLayout.addLayout(hBoxLayout1)
        vBoxLayout.addLayout(hBoxLayout2)

    def show_context_menu(self, pos):
        row = self.tableView.rowAt(pos.y())
        if row == -1:  # 未选中有效行
            return

        # 获取选中行的图书数据
        book_item = self.tableView.item(row, 0)
        if not book_item:
            return

        # 获取图书的上架状态
        shelves_item = self.tableView.item(row, 4)
        if not shelves_item:
            return

        shelves = shelves_item.text()  # 上架状态（0: 下架, 1: 上架）

        # 如果图书是下架状态，不弹出菜单
        if shelves == "下架":
            return

        # 创建菜单
        menu = RoundMenu()
        menu.addAction(Action(FluentIcon.EDIT, '修改图书信息', triggered=lambda: self.edit_book(row)))
        menu.addAction(Action(FluentIcon.BROOM, '下架图书', triggered=lambda: self.delete_book(row)))

        # 显示菜单
        menu.exec_(self.tableView.viewport().mapToGlobal(pos))

    def edit_book(self, row):
        isbn = self.tableView.item(row, 0).text()
        # print(isbn)
        columns, books = BookManager().select_book_by_column("isbn", isbn)
        print(books)
        print(books[0]['isbn'])
        # print(columns, books)
        self.edit_book_window = Edit_Book(books)
        self.edit_book_window.show_success_edit_InfoBar.connect(self.show_success_edit_infobar)
        self.edit_book_window.show()

    def delete_book(self, row):
        isbn = self.tableView.item(row, 0).text()
        columns, books = BookManager().select_book_by_column("isbn", isbn)
        title = books[0]['title']
        mess = Dialog("确认下架", f"确认下架ISBN：{isbn}\n书名：{title}\n\n的图书吗？")
        mess.yesButton.setText("确认")
        mess.cancelButton.setText("取消")

        if mess.exec():
            print('确认下架')
            BookManager().set_book_inactive(isbn)

            self.show_success_delete_InfoBars.emit(True, isbn)
            # mess.close()
        else:
            print('取消添加')

    # def update_table(self, columns, books):
    #     """更新表格数据"""
    #     print("Books data:", books)
    #     self.tableView.setRowCount(len(books))  # 设置行数
    #     for row, book in enumerate(books):
    #         # 确保 book 是字典
    #         if isinstance(book, dict):
    #             self.tableView.setItem(row, 0, QTableWidgetItem(book['isbn']))  # ISBN
    #             self.tableView.setItem(row, 1, QTableWidgetItem(book['title']))  # 书名
    #             self.tableView.setItem(row, 2, QTableWidgetItem(book['category']))  # 分类
    #             self.tableView.setItem(row, 3, QTableWidgetItem(str(book['stock'])))  # 库存
    #         else:
    #             print(f"Error: book at row {row} is not a dictionary: {book}")

    def update_table(self, columns, books):
        """更新表格数据"""
        print("Books data:", books)
        self.tableView.setRowCount(len(books))  # 设置行数
        for row, book in enumerate(books):
            # 确保 book 是字典
            if isinstance(book, dict):
                # 获取上架状态（确保是整数类型）
                try:
                    shelves = int(book.get('shelves', 1))  # 默认值为1（上架）
                except (ValueError, TypeError):
                    shelves = 1  # 异常时默认设为上架

                # 根据上架状态设置字体颜色
                if shelves == 0:  # 下架
                    color = QColor(128, 128, 128)  # 灰色
                else:
                    color = QColor(0, 0, 0)  # 默认黑色

                # 创建并设置单元格
                for col in range(5):  # 假设共4列（0-3）
                    if col == 0:
                        text = book['isbn']
                    elif col == 1:
                        text = book['title']
                    elif col == 2:
                        text = book['category']
                    elif col == 3:
                        text = str(book.get('stock', 0))  # 库存值
                    elif col == 4:
                        text = "上架" if book['shelves'] == 1 else "下架"

                    item = QTableWidgetItem(text)
                    item.setForeground(color)  # 设置字体颜色
                    self.tableView.setItem(row, col, item)
            else:
                print(f"Error: book at row {row} is not a dictionary: {book}")

    def search_books(self, keyword):
        """根据关键字搜索书籍"""
        if not keyword:
            # 如果关键字为空，加载所有书籍
            columns, books = BookManager().select_all_book()
            self.search_result_ready.emit(columns, books)
        else:
            # 如果关键字不为空，分别查询 title 和 isbn
            columns_title, results_title = BookManager().select_book_by_column("title", keyword)
            columns_isbn, results_isbn = BookManager().select_book_by_column("isbn", keyword)
            # 确保列名一致
            if columns_title != columns_isbn:
                raise ValueError("列名不一致，无法合并结果")
            # 将 results_title 转换为列表（如果它是元组）
            if isinstance(results_title, tuple):
                results_title = list(results_title)
            # 将 results_isbn 转换为列表（如果它是元组）
            if isinstance(results_isbn, tuple):
                results_isbn = list(results_isbn)
            # 合并结果并去重
            combined_results = results_title + results_isbn
            unique_results = []
            seen = set()
            for book in combined_results:
                if book['isbn'] not in seen:
                    seen.add(book['isbn'])
                    unique_results.append(book)
            # 发射信号，传递合并后的结果
            self.search_result_ready.emit(columns_title, unique_results)

    def add_book_window(self):
        # self.add_book.show()
        self.add_book_window = Add_Book()
        self.add_book_window.show_success_InfoBar.connect(self.show_success_add_InfoBar)
        self.add_book_window.show()

    def show_success_add_InfoBar(self, b, ibsn):
        if b:
            w = InfoBar.success(
                title='添加成功',
                content=f"图书{ibsn}添加成功！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                # position='Custom',   # NOTE: use custom info bar manager
                duration=2000,
                parent=self
            )
            w.show()
            self.search_books("")  # 自动刷新表格

    def show_success_edit_infobar(self, b, ibsn):
        if b:
            w = InfoBar.success(
                title='修改成功',
                content=f"图书{ibsn}修改成功！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                # position='Custom',   # NOTE: use custom info bar manager
                duration=2000,
                parent=self
            )
            w.show()
            self.search_books("")

    def show_success_delete_InfoBar(self, b, isbn):
        if b:
            w = InfoBar.success(
                title='下架成功',
                content=f"图书{isbn}下架成功！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                # position='Custom',   # NOTE: use custom info bar manager
                duration=2000,
                parent=self
            )
            w.show()
            # time.sleep(2000)
            # w.close()
            self.search_books("")
    # def edit_book_window(self):
    #     # self.add_book.show()
    #     self.add_book_window = Edit_Book()
    #     self.add_book_window.show_success_InfoBar.connect(self.show_success_InfoBar)
    #     self.add_book_window.show()


class Add_Book(QWidget):
    check_exist_signal = pyqtSignal(list)
    show_success_InfoBar = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # w=QWidget()
        # 总垂直布局
        vboxLayout = QVBoxLayout(self)
        # ISBN
        hBoxLayout1 = QHBoxLayout()
        gridLayout = QGridLayout()
        label1 = BodyLabel("ISBN:")
        # self.lable2=BodyLabel()
        self.le1 = LineEdit()
        # le1.textChanged.connect(self.check_exist)
        # gridLayout.addWidget(label1,0,0)
        # gridLayout.addWidget(le1,0,1)
        # gridLayout.addWidget(self.lable2,1,1)
        # hBoxLayout1.addLayout(gridLayout)
        hBoxLayout1.addWidget(label1)
        hBoxLayout1.addWidget(self.le1)
        # 书名
        hBoxLayout2 = QHBoxLayout()
        label2 = BodyLabel("书名:")
        self.le2 = LineEdit()
        hBoxLayout2.addWidget(label2)
        hBoxLayout2.addWidget(self.le2)
        # 分类
        hBoxLayout3 = QHBoxLayout()
        label3 = BodyLabel("分类:")
        self.le3 = LineEdit()
        hBoxLayout3.addWidget(label3)
        hBoxLayout3.addWidget(self.le3)
        # 库存
        hBoxLayout4 = QHBoxLayout()
        label4 = BodyLabel("库存:")
        self.le4 = LineEdit()
        hBoxLayout4.addWidget(label4)
        hBoxLayout4.addWidget(self.le4)
        # 确认取消按钮
        hBoxLayout5 = QHBoxLayout()
        ppbtn = PrimaryPushButton("确认添加")
        ppbtn.clicked.connect(self.check_exist)
        pbtn = PushButton("取消添加")
        pbtn.clicked.connect(self.close)
        hBoxLayout5.addWidget(ppbtn)
        hBoxLayout5.addWidget(pbtn)

        vboxLayout.addLayout(hBoxLayout1)
        vboxLayout.addLayout(hBoxLayout2)
        vboxLayout.addLayout(hBoxLayout3)
        vboxLayout.addLayout(hBoxLayout4)
        vboxLayout.addLayout(hBoxLayout5)

        self.resize(500, 300)
        self.setWindowTitle("添加图书")
        # w.show()

    def check_exist(self):
        isbn = self.le1.text()
        title = self.le2.text()
        category = self.le3.text()
        stock = self.le4.text()
        columns = None
        books = None
        if not (len(isbn) == 0 or len(title) == 0 or len(stock) == 0):
            try:
                with DBConnector(db_config) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"SELECT * FROM books WHERE isbn = '{isbn}'")
                    columns = [col[0] for col in cursor.description]
                    books = cursor.fetchall()
                    # return columns, books
            except Exception as e:
                print(e)

            if books != ():  # 图书已存在
                w = InfoBar.warning(
                    title='图书已存在',
                    content=f"图书（{isbn}）已存在！",
                    orient=Qt.Horizontal,
                    isClosable=True,  # disable close button
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                w.show()
            else:
                mess = Dialog("确认添加",
                              f"确认添加ISBN：{isbn}\n书名：{title}\n分类：{category}\n库存：{stock}\n的图书吗？")
                mess.yesButton.setText("确认")
                mess.cancelButton.setText("取消")

                if mess.exec():
                    print('确认添加')
                    BookManager().add_book(isbn, title, category, int(stock))
                    self.show_success_InfoBar.emit(True, isbn)
                    self.close()

                else:
                    print('取消添加')
        else:
            w = InfoBar.warning(
                title='有字段为空',
                content=f"ISBN码，书名，库存均不能为空！",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            w.show()


class Edit_Book(QWidget):
    show_success_edit_InfoBar = pyqtSignal(bool, str)

    def __init__(self, books: list):
        super().__init__()
        self.books = books
        # print("sssssss",books)
        self.initUI()

    def initUI(self):
        # 总垂直布局
        vboxLayout = QVBoxLayout(self)
        # ISBN
        hBoxLayout1 = QHBoxLayout()
        gridLayout = QGridLayout()
        label1 = BodyLabel("ISBN:")
        self.le1 = LineEdit()
        self.le1.setText(self.books[0]['isbn'] + "（不可更改，更改请下架后重新添加）")
        # self.le1.setReadOnly(True)
        self.le1.setEnabled(False)
        hBoxLayout1.addWidget(label1)
        hBoxLayout1.addWidget(self.le1)
        # 书名
        hBoxLayout2 = QHBoxLayout()
        label2 = BodyLabel("书名:")
        self.le2 = LineEdit()
        self.le2.setText(self.books[0]['title'])
        hBoxLayout2.addWidget(label2)
        hBoxLayout2.addWidget(self.le2)
        # 分类
        hBoxLayout3 = QHBoxLayout()
        label3 = BodyLabel("分类:")
        self.le3 = LineEdit()
        self.le3.setText(self.books[0]['category'])
        hBoxLayout3.addWidget(label3)
        hBoxLayout3.addWidget(self.le3)
        # 库存
        hBoxLayout4 = QHBoxLayout()
        label4 = BodyLabel("库存:")
        self.le4 = LineEdit()
        self.le4.setText(str(self.books[0]['stock']))
        hBoxLayout4.addWidget(label4)
        hBoxLayout4.addWidget(self.le4)
        # 确认取消按钮
        hBoxLayout5 = QHBoxLayout()
        ppbtn = PrimaryPushButton("确认修改")
        ppbtn.clicked.connect(self.edit_book)
        pbtn = PushButton("取消修改")
        pbtn.clicked.connect(self.close)
        hBoxLayout5.addWidget(ppbtn)
        hBoxLayout5.addWidget(pbtn)

        vboxLayout.addLayout(hBoxLayout1)
        vboxLayout.addLayout(hBoxLayout2)
        vboxLayout.addLayout(hBoxLayout3)
        vboxLayout.addLayout(hBoxLayout4)
        vboxLayout.addLayout(hBoxLayout5)

        self.resize(500, 300)
        self.setWindowTitle("修改图书信息")

    def edit_book(self):
        isbn = self.le1.text().split("（")[0]
        title = self.le2.text()
        category = self.le3.text()
        stock = self.le4.text()
        if self.books[0]['title'] == title and self.books[0]['category'] == category and str(
                self.books[0]['stock']) == stock:
            w = InfoBar.warning(
                title='未修改',
                content="没有信息被修改！",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            w.show()
        else:
            mess = Dialog("确认修改",
                          f"确认修改ISBN：{isbn}\n书名：{self.books[0]['title']}->{title}\n分类：{self.books[0]['category']}->{category}\n库存：{self.books[0]['stock']}->{stock}\n的图书信息吗？")
            mess.yesButton.setText("确认")
            mess.cancelButton.setText("取消")

            if mess.exec():
                print('确认修改')
                BookManager().update_book(
                    isbn=isbn,
                    title=title,
                    category=category,
                    stock=int(stock)
                )
                self.show_success_edit_InfoBar.emit(True, isbn)
                self.close()

            else:
                print('取消修改')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = BookManagerInterface("123")
    w.setWindowTitle("图书管理器")
    w.resize(800, 600)
    w.show()
    sys.exit(app.exec())
