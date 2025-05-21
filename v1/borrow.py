from datetime import datetime, timedelta
from tabulate import tabulate
from connector import DBConnector, db_config

# 表头转换字典
borrow_dict = {
    "id": "记录ID",
    "student_id": "学生学号",
    "isbn": "ISBN码",
    "title": "书名",  # 新增字段
    "borrow_date": "借书日期",
    "due_date": "应还日期",
    "returned_date": "实际归还日期"
}



def print_borrow_table(headers: list, results: list, translated_headers=True):
    """
    打印借阅记录表格
    """
    if not results:
        return "无借阅记录", {}

    if translated_headers:
        translated = [borrow_dict.get(h, h) for h in headers]
    else:
        translated = headers

    numbered = [(i + 1,) + row for i, row in enumerate(results)]
    translated_headers = ["编号"] + translated

    table = tabulate(
        numbered,
        headers=translated_headers,
        tablefmt="outline",
        stralign="center",
        numalign="right",
    )

    id_mapping = {i + 1: row[0] for i, row in enumerate(results)}
    return table, id_mapping


class BorrowManager:

    def borrow_book(self, student_id: int, isbn: str,days:int):
        """
        借书功能
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()

                # 检查库存
                cursor.execute("SELECT stock FROM books WHERE isbn = %s", (isbn,))
                stock = cursor.fetchone()
                if not stock or stock[0] < 1:
                    print("图书库存不足或不存在！")
                    return

                # 减少库存
                cursor.execute(
                    "UPDATE books SET stock = stock - 1 WHERE isbn = %s",
                    (isbn,))

                # 添加借阅记录
                borrow_date = datetime.now()
                due_date = borrow_date + timedelta(days=days)

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

    def return_book(self, isbn: str):
        """
        还书功能
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()

                # 查找未归还记录
                cursor.execute(
                    """SELECT id FROM borrow_records 
                    WHERE isbn = %s AND returned_date IS NULL
                    ORDER BY borrow_date DESC LIMIT 1""",
                    (isbn,)
                )
                record = cursor.fetchone()
                if not record:
                    print("未找到有效借阅记录！")
                    return

                # 更新归还日期
                return_date = datetime.now()
                cursor.execute(
                    "UPDATE borrow_records SET returned_date = %s WHERE id = %s",
                    (return_date, record[0]))

                # 恢复库存
                cursor.execute(
                    "UPDATE books SET stock = stock + 1 WHERE isbn = %s",
                    (isbn,))

                conn.commit()

                # 计算逾期
                cursor.execute(
                    "SELECT due_date FROM borrow_records WHERE id = %s",
                    (record[0],))
                due_date = cursor.fetchone()[0]

                if return_date > due_date:
                    days = (return_date - due_date).days
                    print(f"逾期归还！超期{days}天")
                else:
                    print("按时归还成功！")

        except Exception as e:
            print(f"还书失败: {e}")

    def get_borrow_records(self, student_id=None, isbn=None):
        """
        查询借阅记录（包含书名）
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                # 修改后的SQL查询
                query = """
                    SELECT 
                        br.id, 
                        br.student_id, 
                        b.title,
                        br.isbn, 
                        br.borrow_date, 
                        br.due_date,
                        br.returned_date
                    FROM borrow_records br
                    JOIN books b ON br.isbn = b.isbn
                    WHERE 1=1
                """
                params = []

                if student_id:
                    query += " AND br.student_id = %s"
                    params.append(student_id)
                if isbn:
                    query += " AND br.isbn = %s"
                    params.append(isbn)

                query += " ORDER BY br.borrow_date DESC"

                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                records = cursor.fetchall()
                return columns, records

        except Exception as e:
            print(f"查询失败: {e}")
            return [], []

    def get_unreturned_books(self):
        """
        查询所有未归还的图书借阅记录
        :return: (表头列表, 借阅记录数据列表)
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT br.id, br.student_id, b.title, br.isbn, 
                           br.borrow_date, br.due_date 
                    FROM borrow_records br
                    JOIN books b ON br.isbn = b.isbn
                    WHERE br.returned_date IS NULL
                    ORDER BY br.borrow_date DESC
                """)
                columns = [col[0] for col in cursor.description]
                records = cursor.fetchall()
                return columns, records
        except Exception as e:
            print(f"查询失败: {e}")
            return [], []

### test
# # 测试代码
# manager = BorrowManager()
#
# # 借书测试
# manager.borrow_book(2023001, "978-7-121-35632-6",30)
#
# # 查询记录
# headers, records = manager.get_borrow_records()
# table, _ = print_borrow_table(headers, records)
# print(table)
#
# # 还书测试（需根据实际记录ID操作）
# manager.return_book("978-7-121-35632-6")
#
# headers, records = manager.get_borrow_records()
# table, _ = print_borrow_table(headers, records)
# print(table)
#
# # 测试未归还查询
# print("\n=== 未归还书籍列表 ===")
# headers, records = manager.get_unreturned_books()
# table, _ = print_borrow_table(headers, records)
# print(table)
