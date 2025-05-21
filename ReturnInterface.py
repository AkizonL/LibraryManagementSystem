from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal, Qt, QDate
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView, QTableView, \
    QGridLayout
from qfluentwidgets import (
    TableWidget, LineEdit, PrimaryToolButton, FluentIcon, BodyLabel,
    PushButton, InfoBar, InfoBarPosition, Dialog, Action, RoundMenu, PrimaryPushButton, FastCalendarPicker
)

from borrow import BorrowManager


class ReturnWorker(QThread):
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


class ReturnInterface(QWidget):
    search_result_ready = pyqtSignal(list, list)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.borrow_manager = BorrowManager()
        self.init_ui()
        self.search_result_ready.connect(self.update_table)
        self.setObjectName(text.replace(' ', '-'))

    def init_ui(self):
        self.setObjectName("ReturnInterface")
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
        self.worker = ReturnWorker()
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
        return_action = Action(
            FluentIcon.CHECKBOX,
            '归还图书',
            triggered=lambda: self.handle_return_book(row)
        )
        menu.addAction(return_action)
        renew_action = Action(FluentIcon.UPDATE, "续借图书", triggered=lambda: self.handle_renew_book(row))
        menu.addAction(renew_action)

        # 显示菜单
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def handle_renew_book(self, row):
        if row == -1:
            InfoBar.warning(
                title="警告",
                content="请先选择一条记录",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=2000
            )
            return
        # 获取选中行的记录信息
        record_id = int(self.table.item(row, 0).text())
        student_id = self.table.item(row, 1).text()
        isbn = self.table.item(row, 3).text()
        title = self.table.item(row, 2).text()
        due_date = self.table.item(row, 5).text()

        renew_info = {
            "record_id": record_id,
            "student_id": student_id,
            "isbn": isbn,
            "title": title,
            "due_date": due_date
        }

        self.renew_window = Renew_window(renew_info)
        # self.renew_window.destroyed.connect(self.load_data)
        self.renew_window.updata_table.connect(self.load_data)
        self.renew_window.show()

    # TODO
    # self.worker = ReturnWorker()
    # self.worker.result_ready.connect(self.update_table)
    # self.worker.start()

    def handle_return_book(self, row):
        # 获取当前选中的行

        if row == -1:
            InfoBar.warning(
                title="警告",
                content="请先选择一条记录",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=2000
            )
            return
        # 获取选中行的记录信息
        record_id = int(self.table.item(row, 0).text())
        student_id = self.table.item(row, 1).text()
        isbn = self.table.item(row, 3).text()
        title = self.table.item(row, 2).text()
        # 弹出确认对话框
        dialog = Dialog("确认归还", f"确认归还《{title}》\nISBN: {isbn}\n学号: {student_id} 吗？", self)
        dialog.yesButton.setText("确认")
        dialog.cancelButton.setText("取消")
        if dialog.exec():
            try:
                # 调用归还方法，传入 ISBN 和 student_id
                self.borrow_manager.return_book_w(isbn, student_id)
                self.show_info_bar("success", "归还成功", f"《{title}》已成功归还")
                self.search_records(self.search_edit.text())  # 刷新表格
            except Exception as e:
                self.show_info_bar("error", "归还失败", str(e))

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


class Renew_window(QWidget):
    updata_table = pyqtSignal()

    def __init__(self, renew_info: dict):
        super().__init__()
        self.renew_info = renew_info
        print(self.renew_info)
        self.init_ui()

    def init_ui(self):
        # 总垂直布局
        vboxLayout = QVBoxLayout(self)
        # ISBN
        hBoxLayout1 = QHBoxLayout()
        gridLayout = QGridLayout()
        label1 = BodyLabel("ISBN:")
        self.le1 = LineEdit()
        self.le1.setText(self.renew_info['isbn'])
        # self.le1.setReadOnly(True)
        self.le1.setEnabled(False)
        hBoxLayout1.addWidget(label1)
        hBoxLayout1.addWidget(self.le1)
        # 书名
        hBoxLayout2 = QHBoxLayout()
        label2 = BodyLabel("书名:")
        self.le2 = LineEdit()
        self.le2.setText(self.renew_info['title'])
        self.le2.setEnabled(False)
        hBoxLayout2.addWidget(label2)
        hBoxLayout2.addWidget(self.le2)
        # 学号
        hBoxLayout3 = QHBoxLayout()
        label3 = BodyLabel("学号:")
        self.le3 = LineEdit()
        self.le3.setText(self.renew_info['student_id'])
        self.le3.setEnabled(False)
        hBoxLayout3.addWidget(label3)
        hBoxLayout3.addWidget(self.le3)
        # 库存
        hBoxLayout4 = QHBoxLayout()
        label4 = BodyLabel("续借日期:")
        self.calendarpicker = FastCalendarPicker()
        # 将字符串分割为年、月、日
        year, month, day = map(int, self.renew_info['due_date'].split('-'))
        # 创建 QDate 对象
        qdate = QDate(year, month, day)
        self.calendarpicker.setDate(qdate)
        hBoxLayout4.addWidget(label4)
        hBoxLayout4.addWidget(self.calendarpicker)
        # 确认取消按钮
        hBoxLayout5 = QHBoxLayout()
        ppbtn = PrimaryPushButton("确认修改")
        ppbtn.clicked.connect(self.renew)
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

    def renew(self):
        mess = Dialog("确认续借",
                      f"确认续借ISBN：{self.renew_info['isbn']}\n书名：{self.renew_info['title']}\n学生：{self.renew_info['student_id']}\n续借至：{self.calendarpicker.date.toString()}")
        mess.yesButton.setText("确认")
        mess.cancelButton.setText("取消")

        if mess.exec():
            print('确认续借')
            id, due_data = self.renew_info['record_id'], self.calendarpicker.getDate().toString("yyyy-MM-dd")
            # print(id)
            print(f'due_date:{due_data}')
            if BorrowManager.renew_book_by_id(self, id, due_data):
                w = InfoBar.success(
                    title=' 续借成功',
                    content=f"图书{self.renew_info['isbn']}续借成功！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    # position='Custom',   # NOTE: use custom info bar manager
                    duration=2000,
                    parent=self
                )
                w.show()
                self.updata_table.emit()
                # self.search_books("")

            # mess.close()
        else:
            print('取消续借')
        self.close()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = ReturnInterface("122")
#     window.setWindowTitle("图书归还管理")
#     window.resize(800, 600)
#     window.show()
#     sys.exit(app.exec())
