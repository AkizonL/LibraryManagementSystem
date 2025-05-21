import sys
from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal, Qt, QDate
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView, QApplication, QTableView
from qfluentwidgets import (
    TableWidget, LineEdit, PrimaryToolButton, FluentIcon, BodyLabel,
    PushButton, InfoBar, InfoBarPosition, Action, RoundMenu, CalendarPicker
)

from borrow import BorrowManager


class RenewWorker(QThread):
    result_ready = pyqtSignal(list, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.borrow_manager = BorrowManager()

    def run(self):
        try:
            columns, records = self.borrow_manager.get_all_borrow_records()
            self.result_ready.emit(columns, records)
        except Exception as e:
            print(f"Worker error: {e}")


class RenewInterface(QWidget):
    search_result_ready = pyqtSignal(list, list)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.borrow_manager = BorrowManager()
        self.init_ui()
        self.search_result_ready.connect(self.update_table)
        self.setObjectName(text.replace(' ', '-'))

    def init_ui(self):
        self.setObjectName("RenewInterface")
        vbox_layout = QVBoxLayout(self)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_edit = LineEdit()
        self.search_edit.setPlaceholderText("搜索学号/ISBN/书名")
        self.search_edit.textChanged.connect(self.search_records)
        search_btn = PrimaryToolButton(FluentIcon.SEARCH)
        search_btn.clicked.connect(lambda: self.search_records(self.search_edit.text()))
        refresh_btn = PrimaryToolButton(FluentIcon.SYNC)
        refresh_btn.clicked.connect(self.load_data)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(refresh_btn)

        # 表格
        self.table = TableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['记录ID', '学号', '书名', 'ISBN', '借书日期', '应还日期'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        vbox_layout.addLayout(search_layout)
        vbox_layout.addWidget(self.table)

        # 初始加载数据
        self.load_data()

    def load_data(self):
        self.worker = RenewWorker()
        self.worker.result_ready.connect(self.update_table)
        self.worker.start()

    def update_table(self, columns, records):
        """更新表格数据并设置行颜色"""
        self.records = records
        self.table.setRowCount(len(records))
        current_date = datetime.today().date()  # 统一使用date类型

        for row, record in enumerate(records):
            row_color = None
            due_date = record['due_date'].date()  # 转换datetime到date
            delta_days = None  # 初始化 delta_days

            if record['returned_date'] is not None:
                # 已归还的记录不设置背景色
                pass
            else:
                delta_days = (due_date - current_date).days

                if delta_days < 0:
                    row_color = QColor(255, 200, 200)  # 逾期
                elif 0 <= delta_days <= 3:
                    row_color = QColor(255, 255, 200)  # 即将到期
                else:
                    row_color = QColor(200, 255, 200)  # 归还时限大于3天，设置绿色

            # 创建表格项并设置颜色
            for col in range(6):  # 共6列数据
                # 生成单元格文本
                if col == 0:
                    text = str(record['id'])
                elif col == 1:
                    text = str(record['student_id'])
                elif col == 2:
                    text = record['title']
                elif col == 3:
                    text = record['isbn']
                elif col == 4:
                    text = record['borrow_date'].strftime("%Y-%m-%d")
                elif col == 5:
                    text = record['due_date'].strftime("%Y-%m-%d")
                else:
                    text = ""

                item = QTableWidgetItem(text)

                if record['returned_date'] is not None:
                    # 已归还的记录设置字体为灰色
                    item.setForeground(QColor(128, 128, 128))
                    # 设置不可选择状态
                    item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

                # 设置整行背景色
                if row_color:
                    item.setBackground(row_color)

                # 特殊格式：逾期记录加粗
                if delta_days is not None and delta_days < 0 and not record['returned_date']:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                self.table.setItem(row, col, item)

    def show_context_menu(self, pos):
        # 获取点击位置的行号
        row = self.table.rowAt(pos.y())

        # 有效性校验
        if not (0 <= row < self.table.rowCount()):  # 行号越界保护
            return

        # 获取对应数据记录
        record = self.records[row]

        # 核心逻辑：已归还记录不弹出菜单
        if record.get('returned_date'):  # 使用get方法避免KeyError
            return  # 直接退出，不显示菜单

        # 创建菜单
        menu = RoundMenu()
        renew_action = Action(
            FluentIcon.ADD,
            '续借图书',
            triggered=lambda: self.handle_renew_book(row)
        )
        menu.addAction(renew_action)

        # 显示菜单
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def handle_renew_book(self, row):
        """
        处理续借图书操作
        :param row: 选中的行数据
        """
        id = self.table.item(row, 0).text()
        print(id)
        columns, books = BorrowManager.get_all_borrow_records_by_isbn(self, id)
        print(type(books))
        print(books)
        record_info = {
            'title': books[0]['title'],
            'isbn': books[0]['isbn'],
            'student_id': books[0]['student_id'],
            'borrow_date': books[0]['borrow_date'],
            'due_date': books[0]['due_date']
        }
        renew_dialog = RenewBookDialog(record_info, self)
        renew_dialog.accepted = False  # 初始化确认状态
        renew_dialog.show()  # 显示弹窗
        # 监听窗口关闭事件
        renew_dialog.closeEvent = lambda event: self.on_renew_dialog_close(renew_dialog, row)

    def on_renew_dialog_close(self, dialog, row):
        """
        续借弹窗关闭事件处理
        :param dialog: 续借弹窗实例
        :param row: 选中的行数据
        """
        if dialog.accepted:  # 如果用户点击了确认
            new_due_date = dialog.get_new_due_date()
            # 更新应还日期的逻辑
            self.update_due_date(row['record_id'], new_due_date)

    def search_records(self, keyword):
        """根据关键字搜索记录并更新表格"""
        columns, records = self.borrow_manager.get_all_borrow_records()

        if keyword:
            filtered = []
            keyword = keyword.lower()
            for record in records:
                # 检查关键字是否匹配学生ID、ISBN或书名
                if (keyword in str(record['student_id']).lower() or
                        keyword in record['isbn'].lower() or
                        keyword in record['title'].lower()):
                    filtered.append(record)
            records = filtered
            self.records = records

        # 调用更新表格函数
        self.update_table(columns, records)

    def show_info_bar(self, type_, title, content):
        creator = getattr(InfoBar, type_)
        creator(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        ).show()


class RenewBookDialog(QWidget):  # 继承自 QWidget
    def __init__(self, record_info, parent=None):
        """
        初始化续借弹窗
        :param record_info: 包含借阅记录信息的字典
        :param parent: 父窗口
        """
        super().__init__(parent)
        self.record_info = record_info
        self.init_ui()

    def init_ui(self):
        """初始化UI布局"""
        self.setWindowTitle("续借图书")
        self.resize(400, 300)
        self.setModal(True)  # 设置为模态窗口
        # 主布局
        vbox_layout = QVBoxLayout(self)
        # 添加不可编辑的信息展示
        vbox_layout.addWidget(BodyLabel(f"书名: {self.record_info['title']}"))
        vbox_layout.addWidget(BodyLabel(f"ISBN: {self.record_info['isbn']}"))
        vbox_layout.addWidget(BodyLabel(f"学号: {self.record_info['student_id']}"))
        vbox_layout.addWidget(BodyLabel(f"借书日期: {self.record_info['borrow_date']}"))
        vbox_layout.addWidget(BodyLabel(f"当前应还日期: {self.record_info['due_date']}"))
        # 添加日历控件
        calendar_label = BodyLabel("选择新的应还日期:")
        self.calendar = CalendarPicker(self)
        # 设置默认日期为当前应还日期
        due_date = datetime.strptime(self.record_info['due_date'], "%Y-%m-%d").date()
        qdate = QDate(due_date.year, due_date.month, due_date.day)  # 将 datetime.date 转换为 QDate
        self.calendar.setDate(qdate)
        vbox_layout.addWidget(calendar_label)
        vbox_layout.addWidget(self.calendar)
        # 添加确认和取消按钮
        btn_layout = QHBoxLayout()
        confirm_btn = PushButton("确认续借")
        confirm_btn.clicked.connect(self.on_confirm)
        cancel_btn = PushButton("取消")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        vbox_layout.addLayout(btn_layout)

    def on_confirm(self):
        """确认续借按钮点击事件"""
        new_due_date = self.get_new_due_date()
        # 检查新日期是否有效
        if new_due_date:
            self.accepted = True  # 标记为确认
            self.close()  # 关闭窗口
        else:
            w = InfoBar.error(
                title='日期无效',
                content="请选择有效的日期！",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            w.show()

    def get_new_due_date(self):
        """获取用户选择的新应还日期"""
        qdate = self.calendar.getDate()  # 获取 QDate 对象
        return qdate.toString("yyyy-MM-dd")  # 将 QDate 转换为字符串


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RenewInterface("续借管理")
    window.setWindowTitle("图书续借管理")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
