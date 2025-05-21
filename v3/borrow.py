from datetime import datetime, timedelta

from tabulate import tabulate

from connector_pymysql import DBConnector, db_config

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
    最小改动版本，适应字典列表结构
    """
    if not results:
        return "无匹配结果", {}

    # 保持原始表头顺序
    field_order = headers

    if translated_headers:
        translated_headers = [borrow_dict.get(header, header) for header in headers]
    else:
        translated_headers = headers

    # 关键修改点：从字典按顺序提取值
    numbered_results = [
        (i + 1,) + tuple(row[field] for field in field_order)  # 按原始字段顺序生成元组
        for i, row in enumerate(results)
    ]

    translated_headers = ["编号"] + translated_headers

    table = tabulate(
        tabular_data=numbered_results,
        headers=translated_headers,
        tablefmt="outline",
        stralign="center",
        numalign="right",
    )

    # 关键修改点：从字典获取ISBN
    id_mapping = {i + 1: row[field_order[0]] for i, row in enumerate(results)}  # 假设第一个字段是唯一标识

    return table, id_mapping


class BorrowManager:

    def borrow_book(self, student_id: int, isbn: str, days: int):
        """
        借书功能
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()

                # 检查库存
                cursor.execute("SELECT stock FROM books WHERE isbn = %s", (isbn,))
                stock = cursor.fetchone()
                if not stock or stock['stock'] < 1:
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
                print(type(record))
                print(record)
                # print(record[0])
                if not record:
                    print("未找到有效借阅记录！")
                    return

                # 更新归还日期
                return_date = datetime.now()
                cursor.execute(
                    "UPDATE borrow_records SET returned_date = %s WHERE id = %s",
                    (return_date, record['id']))

                # 恢复库存
                cursor.execute(
                    "UPDATE books SET stock = stock + 1 WHERE isbn = %s",
                    (isbn,))

                conn.commit()

                # 计算逾期
                cursor.execute(
                    "SELECT due_date FROM borrow_records WHERE id = %s",
                    (record['id'],))
                due_date = cursor.fetchone()['due_date']
                # print(due_date)

                if return_date > due_date:
                    days = (return_date - due_date).days
                    print(f"逾期归还！超期{days}天")
                else:
                    print("按时归还成功！")

        except Exception as e:
            print(f"还书失败: {e}")

    def return_book_w(self, isbn: str, student_id: str):
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                # 查找未归还记录
                cursor.execute(
                    """SELECT id, borrow_date, due_date FROM borrow_records 
                    WHERE isbn = %s AND student_id = %s AND returned_date IS NULL
                    ORDER BY borrow_date DESC LIMIT 1""",
                    (isbn, student_id)
                )
                record = cursor.fetchone()
                if not record:
                    print("未找到有效借阅记录！")
                    return False
                # 更新归还日期
                return_date = datetime.now()
                cursor.execute(
                    "UPDATE borrow_records SET returned_date = %s WHERE id = %s",
                    (return_date, record['id'])
                )
                # 恢复库存
                cursor.execute(
                    "UPDATE books SET stock = stock + 1 WHERE isbn = %s",
                    (isbn,)
                )
                conn.commit()
                # 计算逾期
                due_date = record['due_date']
                if return_date > due_date:
                    days = (return_date - due_date).days
                    print(f"逾期归还！超期{days}天")
                else:
                    print("按时归还成功！")
                return True
        except Exception as e:
            print(f"还书失败: {e}")
            return False

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

    def get_all_borrow_records_by_isbn(self, id):
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                # 使用条件排序实现复合排序逻辑
                cursor.execute(f"""SELECT * FROM borrow_records WHERE id = '{id}'""")
                columns = [col[0] for col in cursor.description]
                records = cursor.fetchall()
                return columns, records
        except Exception as e:
            print(f"查询失败: {e}")
            return [], []

    def renew_book_by_id(self, id, due_date):
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                # 使用条件排序实现复合排序逻辑
                cursor.execute(
                    f"""
                        UPDATE borrow_records
                        SET due_date = '{due_date}'
                        WHERE id = '{id}'
                    """)
                conn.commit()
                return True
        except Exception as e:
            print(f"续借失败: {e}")
            return [], []

    def get_all_borrow_records(self):
        """
        查询所有借阅记录（包括已归还和未归还）
        排序规则：
        1. 未归还的记录排在前半部分，按距离当前日期从近到远排序（due_date升序）
        2. 已归还的记录排在后半部分，按归还时间从新到旧排序（returned_date降序）
        :return: (表头列表, 借阅记录数据列表)
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                # 使用条件排序实现复合排序逻辑
                cursor.execute("""
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
                    ORDER BY 
                        CASE 
                            WHEN br.returned_date IS NULL THEN 0  -- 未归还记录优先
                            ELSE 1  -- 已归还记录在后
                        END,
                        CASE 
                            WHEN br.returned_date IS NULL THEN DATEDIFF(NOW(), br.due_date)  -- 未归还按逾期天数正序
                            ELSE DATEDIFF(NOW(), br.returned_date)  -- 已归还按归还天数倒序
                        END DESC
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
