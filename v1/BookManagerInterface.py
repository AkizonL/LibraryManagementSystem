import sys
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import (
    QWidget, QAbstractItemView, QTableView, QApplication, QVBoxLayout, QMessageBox
)
from books import BookManager

class Worker(QThread):
    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        print("子线程创建")

    def run(self):
        try:
            # 添加详细日志定位问题
            print("Worker thread started")
            columns, books = BookManager().select_all_book()
            print("Query completed:", columns, books)
        except Exception as e:
            # 捕获所有异常并打印
            print(f"!!! Worker thread crashed: {e}")

class BookManagerInterface(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化UI布局
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 创建表格视图
        self.tableView = QTableView()
        layout.addWidget(self.tableView)

        t=Worker(parent=self)
        t.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = BookManagerInterface()
    w.setWindowTitle("图书管理器")
    w.resize(800, 600)
    w.show()
    sys.exit(app.exec())
