from tabulate import tabulate

from connector_pymysql import DBConnector, db_config

# 用于转换表头
books_dict = {"isbn": "ISBN码", "title": "书名", "category": "分类", "stock": "库存"}


def print_result_table(headers: list, results: list, translated_headers=True):
    """
    最小改动版本，适应字典列表结构
    """
    if not results:
        return "无匹配结果", {}

    # 保持原始表头顺序
    field_order = headers

    if translated_headers:
        translated_headers = [books_dict.get(header, header) for header in headers]
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


class BookManager:

    def add_book(self, isbn: str, title: str, category: str, stock: int):
        """
        添加图书
        :param isbn: ISBN码
        :param title: 书名
        :param category: 分类
        :param stock: 库存数量
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO books (isbn, title, category, stock) VALUES (%s, %s, %s, %s)""",
                    (isbn, title, category, stock)
                )
                conn.commit()
                print(f"图书《{title}》添加成功！")
        except Exception as e:
            print(e)

    def set_book_inactive(self, isbn: str) -> bool:
        """
        根据ISBN将图书下架（shelves设为0）
        :param isbn: ISBN码
        :return: 操作是否成功
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                # UPDATE 语句直接设置 shelves = 0
                cursor.execute(
                    """UPDATE books SET shelves = 0 WHERE isbn = %s""",
                    (isbn,)
                )
                conn.commit()
                print(f"图书（ISBN: {isbn}）已下架")
                return True
        except Exception as e:
            print(f"下架失败: {e}")
            return False

    def delete_book(self, isbn: str):
        """
        根据ISBN删除图书
        :param isbn: ISBN码
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """DELETE FROM books WHERE isbn = %s""",
                    (isbn,)
                )
                conn.commit()
                print(f"图书（ISBN: {isbn}）删除成功！")
        except Exception as e:
            print(e)

    def update_book(self, isbn: str, **kwargs):
        """
        修改图书信息
        :param isbn: ISBN码
        :param kwargs: 需要修改的字段和值（如 title='新书名', stock=20）
        """
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
                values = list(kwargs.values())
                values.append(isbn)
                cursor.execute(
                    f"""UPDATE books SET {set_clause} WHERE isbn = %s""",
                    values
                )
                conn.commit()
                print(f"图书（ISBN: {isbn}）信息更新成功！")
        except Exception as e:
            print(e)

    def interactive_update(self):
        # 获取图书列表
        columns, books = BookManager().select_all_book()
        if not books:
            print("当前没有可修改的图书")
            return

        # 显示带编号的表格
        table, id_mapping = print_result_table(columns, books)
        print("当前图书列表：\n" + table)

        # 选择图书编号
        try:
            update_id = int(input(
                "\n请输入要修改的图书编号(q退出)(直接回车保留原值)(ISBN码不支持修改，若要修改，请删除图书再添加！): ").strip())
        except:
            print("操作已取消")
            return

        if update_id not in id_mapping:
            print("无效编号")
            return

        # 获取目标图书
        isbn = id_mapping[update_id]
        detail_cols, detail_data = BookManager().select_book_by_column("isbn", isbn)

        if not detail_data:
            print("该图书不存在")
            return

        # 构建当前信息字典
        current_info = dict(zip(detail_cols, detail_data[0]))
        updates = {}

        # 遍历可修改字段
        for col in ['title', 'category', 'stock']:
            current_val = current_info[col]
            new_val = input(f"{col} ({current_val}): ").strip()

            if not new_val:  # 跳过空输入
                continue

            # 特殊处理库存字段
            if col == 'stock':
                try:
                    new_val = int(new_val)
                    if new_val < 0:
                        print("库存不能为负数")
                        continue
                except ValueError:
                    print("请输入有效数字")
                    continue

            # 记录修改
            if str(new_val) != str(current_val):
                updates[col] = new_val

        # 保存修改
        if updates:
            print("\n修改内容：")
            for k, v in updates.items():
                print(f"{k}: {current_info[k]} → {v}")

            if input("\n确认保存修改？(y/N) ").lower() == 'y':
                BookManager().update_book(isbn, **updates)
                print("✅ 修改已保存")
        else:
            print("没有需要保存的修改")

    def select_all_book(self):
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM books')
                columns = [col[0] for col in cursor.description]
                books = cursor.fetchall()
                return columns, books
        except Exception as e:
            print(e)

    def select_book_by_column(self, column, sth):
        try:
            with DBConnector(db_config) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""SELECT * FROM books WHERE {column} like '%{sth}%'""")
                columns = [col[0] for col in cursor.description]
                books = cursor.fetchall()
                return columns, books
        except Exception as e:
            print(e)

### test
# BookManager().add_book("978-7-5399-8591-5", "三体3：死神永生", "科幻", 8)
# BookManager().update_book("978-7-5399-8591-5", title="三体3：死神永生（修订版）", stock=10)
# BookManager().delete_book("978-7-5399-8591-5")
# columns, books = BookManager().select_book_by_column("title","三")
# books,id_mapping=print_result_table(columns, books,translated_headers=True)
# print(books)
# print(id_mapping)
# BookManager().interactive_update()
