from PyQt5.QtCore import QThread, pyqtSignal, Qt, QDate
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView, QTableView
)
from qfluentwidgets import TableWidget, LineEdit, PrimaryToolButton, FluentIcon, PrimaryPushButton, BodyLabel, \
    PushButton, InfoBar, InfoBarPosition, Dialog, Action, RoundMenu, FastCalendarPicker

from books import BookManager
from connector_pymysql import DBConnector, db_config


class Worker(QThread):
    # 定义一个信号，用于传递查询结果
    result_ready = pyqtSignal(list, list)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        print("子线程创建")

    def select_all_books_sorted_by_stock(self):
        """
        获取所有图书数据，并按库存降序排列
        :return: (表头列表, 图书数据列表)
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                # 按库存降序排序，下架图书（shelves=0）排在最后
                cursor.execute('''
                    SELECT * FROM books 
                    ORDER BY shelves DESC, stock DESC
                ''')
                columns = [col[0] for col in cursor.description]
                books = cursor.fetchall()
                return columns, books
        except Exception as e:
            print(f"获取排序数据失败: {e}")
            return [], []

    def run(self):
        try:
            print("Worker thread started")
            columns, books = self.select_all_books_sorted_by_stock()
            print("Query completed:", columns, books)
            # 发出信号，传递查询结果
            self.result_ready.emit(columns, books)
        except Exception as e:
            print(f"!!! Worker thread crashed: {e}")


class BorrowInterface(QWidget):
    search_result_ready = pyqtSignal(list, list)

    def __init__(self, text: str, parent=None):
        super(BorrowInterface, self).__init__(parent)
        self.initUI()
        self.search_result_ready.connect(self.update_table)
        self.setObjectName(text.replace(' ', '-'))

    def initUI(self):
        vBoxLayout = QVBoxLayout(self)  # 将布局设置为窗口的主布局

        # 搜索和按钮
        hBoxLayout1 = QHBoxLayout()
        le1 = LineEdit()
        le1.textChanged.connect(self.search_books)
        le1.setPlaceholderText("搜索ISBN码或者书名")
        le1.setStyleSheet("background-color: rgba(245, 245, 245, 0.2);border-radius: 4px")
        ptbtn1 = PrimaryToolButton()
        ptbtn1.setIcon(FluentIcon.SEARCH)
        # ppbtn1 = PrimaryPushButton()
        ptbtn2 = PrimaryToolButton()
        ptbtn2.setIcon(FluentIcon.SYNC)
        ptbtn2.clicked.connect(self.search_books)
        # ppbtn1.setIcon(FluentIcon.ADD)
        # ppbtn1.setText("添加图书")
        # ppbtn1.clicked.connect(self.add_book_window)
        hBoxLayout1.addWidget(le1)
        hBoxLayout1.addWidget(ptbtn1)
        hBoxLayout1.addWidget(ptbtn2)
        # hBoxLayout1.addWidget(ppbtn1)

        # 表格
        hBoxLayout2 = QHBoxLayout()
        self.tableView = TableWidget()
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.show_context_menu)
        # self.tableView.setSortingEnabled(True)  # 原生排序
        hBoxLayout2.addWidget(self.tableView)

        # 设置表格属性
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(5)
        self.tableView.setHorizontalHeaderLabels(['ISBN', '书名', '分类', '库存', '上架状态'])
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自动拉伸
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)  # 禁用直接编辑

        # 启动子线程加载数据
        self.worker = Worker(parent=self)
        self.worker.result_ready.connect(self.update_table)  # 连接信号和槽
        self.worker.start()  # 启动线程

        # 将布局添加到主布局
        vBoxLayout.addLayout(hBoxLayout1)
        vBoxLayout.addLayout(hBoxLayout2)

    def show_context_menu(self, pos):
        """显示右键菜单，下架图书不弹出菜单"""
        row = self.tableView.rowAt(pos.y())
        if row == -1:  # 未选中行
            return

        # 获取当前行的图书数据
        item = self.tableView.item(row, 0)  # 假设第一列是 ISBN
        if not item:
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
        menu.addAction(Action(FluentIcon.RIGHT_ARROW, '借书', triggered=lambda: self.borrow_book(row)))
        # menu.addAction(Action(FluentIcon.BROOM, '从数据库删除', triggered=lambda: self.delete_book(row)))

        # 显示菜单
        menu.exec_(self.tableView.viewport().mapToGlobal(pos))

    def borrow_book(self, row):
        isbn = self.tableView.item(row, 0).text()
        # print(isbn)
        columns, books = BookManager().select_book_by_column("isbn", isbn)
        print(books)
        print(books[0]['isbn'])
        if books[0]['stock'] == 0:
            w = InfoBar.warning(
                title='库存不足',
                content="库存不足，换一本书吧:-(",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            w.show()
        else:
            self.borrow_book_window = Borrow_Book(books)
            self.borrow_book_window.show_success_borrow_InfoBar.connect(self.show_success_InfoBar)
            self.borrow_book_window.show()

    def show_success_InfoBar(self, b, infos):
        if b:
            w = InfoBar.success(
                title='借书成功',
                content=f"学生:{infos[0]}借书{infos[1]}成功！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                # position='Custom',   # NOTE: use custom info bar manager
                duration=2000,
                parent=self
            )
            w.show()
            self.search_books("")
            # print("diaoyongsousuo")
            # self.worker = Worker(parent=self)
            # self.worker.result_ready.connect(self.update_table)  # 连接信号和槽
            # self.worker.start()

    def search_books(self, keyword):
        """根据关键字搜索书籍"""
        if not keyword:
            # 如果关键字为空，加载所有书籍
            columns, books = BookManager().select_all_book()
            sorted_results = sorted(books, key=lambda x: x['stock'], reverse=True)
            sorted_books = sorted(sorted_results, key=lambda book: book.get('shelves', 1), reverse=True)
            # print("降序：")
            # print(sorted_results)
            self.search_result_ready.emit(columns, sorted_books)
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

            sorted_results = sorted(unique_results, key=lambda x: x['stock'], reverse=True)
            # print("降序：")
            # print(sorted_results)
            # 发射信号，传递合并后的结果
            self.search_result_ready.emit(columns_title, sorted_results)

    def update_table(self, columns, books):
        """更新表格数据"""
        print("Books data:", books)
        self.tableView.setRowCount(len(books))  # 设置行数
        for row, book in enumerate(books):
            # 确保 book 是字典
            if isinstance(book, dict):
                # 获取库存值（确保是整数类型）
                try:
                    stock = int(book.get('stock', 0))
                except (ValueError, TypeError):
                    stock = 0  # 异常时默认设为0

                # 获取上架状态（确保是整数类型）
                try:
                    shelves = int(book.get('shelves', 1))  # 默认上架
                except (ValueError, TypeError):
                    shelves = 1  # 异常时默认上架

                # 根据库存设置颜色（仅对上架图书生效）
                if shelves == 1:  # 上架图书
                    if stock < 5:
                        color = QColor(255, 200, 200)  # 淡红色
                    elif stock < 10:
                        color = QColor(255, 255, 200)  # 淡黄色
                    else:
                        color = QColor(200, 255, 200)  # 淡绿色
                else:  # 下架图书
                    color = None  # 不填充背景颜色

                # 创建并设置单元格
                for col in range(5):  # 假设共4列（0-3）
                    if col == 0:
                        text = book['isbn']
                    elif col == 1:
                        text = book['title']
                    elif col == 2:
                        text = book['category']
                    elif col == 3:
                        text = str(stock)
                    elif col == 4:
                        text = "上架" if book['shelves'] == 1 else "下架"

                    item = QTableWidgetItem(text)
                    if shelves == 0:  # 下架图书
                        item.setForeground(QColor(128, 128, 128))  # 字体设置为灰色
                    if color:  # 上架图书
                        item.setBackground(color)
                    self.tableView.setItem(row, col, item)
            else:
                print(f"Error: book at row {row} is not a dictionary: {book}")


class Borrow_Book(QWidget):
    show_success_borrow_InfoBar = pyqtSignal(bool, list)

    def __init__(self, books: list, parent=None):
        super(Borrow_Book, self).__init__(parent)
        self.books = books
        self.init_UI()

    def init_UI(self):
        vboxLayout = QVBoxLayout(self)
        # 学号
        hBoxLayout6 = QHBoxLayout()
        label6 = BodyLabel("学号:")
        self.le_student_id = LineEdit()
        hBoxLayout6.addWidget(label6)
        hBoxLayout6.addWidget(self.le_student_id)
        # ISBN
        hBoxLayout1 = QHBoxLayout()
        label1 = BodyLabel("借书ISBN:")
        self.le_isbn = LineEdit()
        self.le_isbn.setText(self.books[0]['isbn'])
        # self.le_isbn.setReadOnly(True)
        self.le_isbn.setEnabled(False)
        hBoxLayout1.addWidget(label1)
        hBoxLayout1.addWidget(self.le_isbn)
        # 书名
        hBoxLayout2 = QHBoxLayout()
        label2 = BodyLabel("书名:")
        self.le_title = LineEdit()
        self.le_title.setText(self.books[0]['title'])
        # self.le_title.setReadOnly(True)
        self.le_title.setEnabled(False)
        hBoxLayout2.addWidget(label2)
        hBoxLayout2.addWidget(self.le_title)
        # 借书日期（当前系统时间，不可编辑）
        hBoxLayout3 = QHBoxLayout()
        label3 = BodyLabel("借书日期:")
        self.le_borrow_date = LineEdit()
        self.le_borrow_date.setText(QDate.currentDate().toString("yyyy-MM-dd"))
        self.le_borrow_date.setEnabled(False)  # 不可编辑
        hBoxLayout3.addWidget(label3)
        hBoxLayout3.addWidget(self.le_borrow_date)
        # 还书日期
        hBoxLayout4 = QHBoxLayout()
        label4 = BodyLabel("还书日期(默认30天后):")
        self.date_picker = FastCalendarPicker()
        self.date_picker.setDate(QDate.currentDate().addDays(30))  # 默认30天后
        hBoxLayout4.addWidget(label4)
        hBoxLayout4.addWidget(self.date_picker)
        # 确认取消按钮
        hBoxLayout5 = QHBoxLayout()
        self.ppbtn_confirm = PrimaryPushButton("确认借书")
        self.ppbtn_confirm.clicked.connect(self.ppbtn_confirm_do)
        self.pbtn_cancel = PushButton("取消")
        hBoxLayout5.addWidget(self.ppbtn_confirm)
        hBoxLayout5.addWidget(self.pbtn_cancel)
        # 添加布局
        vboxLayout.addLayout(hBoxLayout6)
        vboxLayout.addLayout(hBoxLayout1)
        vboxLayout.addLayout(hBoxLayout2)
        vboxLayout.addLayout(hBoxLayout3)
        vboxLayout.addLayout(hBoxLayout4)
        vboxLayout.addLayout(hBoxLayout5)
        # 窗口设置
        self.resize(500, 300)
        self.setWindowTitle("借书界面")

    def ppbtn_confirm_do(self):
        student_id = self.le_student_id.text()
        isbn = self.le_isbn.text()
        title = self.le_title.text()
        borrow_date = self.le_borrow_date.text()
        due_date = self.date_picker.getDate().toString("yyyy-MM-dd")
        # print(student_id, isbn, borrow_date, due_date)
        mess = Dialog("借书确认", f"确认学生：{student_id}\n借阅图书:{isbn}\n书名:{title}\n还书日期:{due_date}")
        mess.yesButton.setText("确认")
        mess.cancelButton.setText("取消")

        if mess.exec():
            print('确认')
            self.borrow_book(student_id=student_id, isbn=isbn, borrow_date=borrow_date, due_date=due_date)
            print("写入数据库成功")
            self.show_success_borrow_InfoBar.emit(True, [student_id, isbn])
            self.close()
        else:
            print('取消借书')

    def borrow_book(self, student_id: str, isbn: str, borrow_date: str, due_date: str):
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                # 减少库存
                cursor.execute(
                    "UPDATE books SET stock = stock - 1 WHERE isbn = %s",
                    (isbn,))

                cursor.execute(
                    """INSERT INTO borrow_records 
                    (student_id, isbn, borrow_date, due_date)
                    VALUES (%s, %s, %s, %s)""",
                    (student_id, isbn, borrow_date, due_date)
                )

                conn.commit()
                print(f"学生 {student_id} 借阅 {isbn} 成功！")

        except Exception as e:
            print(f"借书失败: {e}")

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     w = BorrowInterface()
#     w.setWindowTitle("借书系统")
#     w.resize(800, 600)
#     w.show()
#     sys.exit(app.exec())
