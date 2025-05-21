# main.py
import sys
from connector_pymysql import DBConnector, db_config
from books import BookManager, print_result_table
from borrow import BorrowManager, print_borrow_table


def login():
    """管理员登录验证"""
    username = input("用户名：").strip()
    password = input("密码：").strip()

    try:
        with DBConnector(db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM admins WHERE username = %s AND password = %s",
                (username, password))
            if cursor.fetchone():
                print("\n登录成功！")
                return True
            else:
                print("用户名或密码错误！")
                return False
    except Exception as e:
        print(f"数据库错误：{e}")
        return False


def show_dashboard():
    """统计看板"""
    try:
        with DBConnector(db_config) as conn:
            cursor = conn.cursor()

            # 总藏书量
            cursor.execute("SELECT SUM(stock) FROM books")
            total_books = cursor.fetchone()[0] or 0

            # 当前借出量
            cursor.execute("""
                SELECT COUNT(*) 
                FROM borrow_records 
                WHERE returned_date IS NULL
            """)
            borrowed = cursor.fetchone()[0] or 0

            # 逾期数量
            cursor.execute("""
                SELECT COUNT(*) 
                FROM borrow_records 
                WHERE returned_date IS NULL 
                AND due_date < NOW()
            """)
            overdue = cursor.fetchone()[0] or 0

            print("\n=== 统计看板 ===")
            print(f"总藏书量：{total_books} 册")
            print(f"当前借出量：{borrowed} 册")
            print(f"逾期未还数量：{overdue} 册")
    except Exception as e:
        print(f"获取统计信息失败：{e}")


def search_books():
    """图书搜索功能"""
    keyword = input("请输入书名或ISBN关键字：").strip()
    if not keyword:
        print("关键字不能为空！")
        return

    # 分别查询书名和ISBN
    bm = BookManager()
    columns_title, results_title = bm.select_book_by_column("title", keyword)
    columns_isbn, results_isbn = bm.select_book_by_column("isbn", keyword)

    # 合并去重
    seen = set()
    combined = []
    for book in results_title + results_isbn:
        if book[0] not in seen:
            seen.add(book[0])
            combined.append(book)

    if not combined:
        print("无匹配结果")
        return

    # 显示结果
    table, _ = print_result_table(columns_title, combined)
    print(table)


def show_all_books_sorted():
    """显示所有书籍，按库存降序排列，返回排序后的书籍列表和编号映射"""
    bm = BookManager()
    columns, books = bm.select_all_book()
    if not books:
        print("暂无书籍数据。")
        return None, None
    # 按库存降序排序
    sorted_books = sorted(books, key=lambda x: x[3], reverse=True)
    # 显示表格
    table, id_mapping = print_result_table(columns, sorted_books)
    print(table)
    return sorted_books, id_mapping


def book_management():
    """图书管理子菜单"""
    bm = BookManager()
    while True:
        print("\n=== 图书管理 ===")
        print("1. 添加图书")
        print("2. 删除图书")
        print("3. 修改图书信息")
        print("4. 查询图书")
        print("0. 返回上级")
        choice = input("请选择操作：").strip()

        if choice == '1':
            # 添加图书
            isbn = input("请输入ISBN（格式：XXX-XX-XXXXX-XX-X）：").strip()
            title = input("请输入书名：").strip()
            category = input("请输入分类（可选，直接回车跳过）：").strip() or None
            stock = input("请输入库存数量：").strip()

            if not stock.isdigit() or int(stock) < 0:
                print("库存必须是非负整数！")
                continue
            bm.add_book(isbn, title, category, int(stock))

        elif choice == '2':
            # 删除图书
            columns, books = bm.select_all_book()
            if not books:
                print("当前没有可删除的图书！")
                continue

            table, id_mapping = print_result_table(columns, books)
            print(table)

            try:
                num = int(input("请输入要删除的图书编号（输入0取消）："))
                if num == 0:
                    continue
                isbn = id_mapping[num]
                if input(f"确认删除 ISBN 为 {isbn} 的图书吗？(y/N)").lower() == 'y':
                    bm.delete_book(isbn)
            except:
                print("输入无效！")

        elif choice == '3':
            # 修改图书
            bm.interactive_update()

        elif choice == '4':
            # 查询图书
            search_books()

        elif choice == '0':
            return
        else:
            print("无效选项！")


def borrow_management():
    """借阅管理子菜单"""
    bm = BorrowManager()
    while True:
        print("\n=== 借阅管理 ===")
        print("1. 借书")
        print("2. 还书")
        print("3. 查询借阅记录")
        print("0. 返回上级")
        choice = input("请选择操作：").strip()

        if choice == '1':
            # 借书
            sorted_books, id_mapping = show_all_books_sorted()
            if not sorted_books:
                continue
            try:
                book_num = int(input("请输入要借阅的书籍编号：").strip())
                isbn = id_mapping[book_num]
            except (ValueError, KeyError):
                print("无效的编号！")
                continue
            student_id = input("请输入学生学号：").strip()
            if not student_id.isdigit():
                print("学号必须为数字！")
                continue
            bm.borrow_book(int(student_id), isbn, 30)

        elif choice == '2':
            # 还书
            sorted_books, id_mapping = show_all_books_sorted()
            if not sorted_books:
                continue
            try:
                book_num = int(input("请输入要归还的书籍编号：").strip())
                isbn = id_mapping[book_num]
            except (ValueError, KeyError):
                print("无效的编号！")
                continue
            student_id = input("请输入学生学号：").strip()
            bm.return_book(isbn)

        elif choice == '3':
            # 查询记录
            student_id = input("按学号查询（留空忽略）：").strip()
            isbn = input("按ISBN查询（留空忽略）：").strip()

            # 处理输入
            student_id = int(student_id) if student_id.isdigit() else None
            isbn = isbn if isbn else None

            columns, records = bm.get_borrow_records(
                student_id=student_id,
                isbn=isbn
            )
            table, _ = print_borrow_table(columns, records)
            print(table)

        elif choice == '0':
            return
        else:
            print("无效选项！")


def main_menu():
    """主菜单"""
    while True:
        print("\n=== 主菜单 ===")
        print("1. 图书管理")
        print("2. 借阅管理")
        print("3. 查看统计看板")
        print("4. 退出系统")
        choice = input("请选择操作：").strip()

        if choice == '1':
            book_management()
        elif choice == '2':
            borrow_management()
        elif choice == '3':
            show_dashboard()
        elif choice == '4':
            print("感谢使用，再见！")
            sys.exit(0)
        else:
            print("无效选项，请重新输入！")


if __name__ == "__main__":
    if login():
        main_menu()
    else:
        print("登录失败，程序退出。")
