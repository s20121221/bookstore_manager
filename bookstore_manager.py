import sqlite3
from DataBaseTool import DataBaseTool

DBTOOL = DataBaseTool("bookstore.db")
SaleTable = ["sdate", "mid", "bid", "sqty", "sdiscount", "stotal"]


def count_chinese(text: str) -> int:
    """
    計算字串中的中文字數

    Args:
        text (str): 要計算的文字 
    Returns:
        int: 中文字數
    """
    chinese_count = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            chinese_count += 1
    return chinese_count

import sqlite3


def initialize_database() -> None:
    """
    初始化 SQLite 資料庫：
    - 確認是否已存在 'member'、'book'、'sale' 三個資料表
    - 若有任一表不存在，則建立資料表並插入預設資料

    Returns:
        None
    """
    with sqlite3.connect("bookstore.db") as conn:
        cursor = conn.cursor()

        # 查詢目前已存在的資料表
        cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ('member', 'book', 'sale')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]

        # 必要資料表
        required_tables = ['member', 'book', 'sale']

        # 有任一資料表不存在就建立所有表格與初始資料
        if not all(table in existing_tables for table in required_tables):
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS member (
                mid TEXT PRIMARY KEY,
                mname TEXT NOT NULL,
                mphone TEXT NOT NULL,
                memail TEXT
            );

            CREATE TABLE IF NOT EXISTS book (
                bid TEXT PRIMARY KEY,
                btitle TEXT NOT NULL,
                bprice INTEGER NOT NULL,
                bstock INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sale (
                sid INTEGER PRIMARY KEY AUTOINCREMENT,
                sdate TEXT NOT NULL,
                mid TEXT NOT NULL,
                bid TEXT NOT NULL,
                sqty INTEGER NOT NULL,
                sdiscount INTEGER NOT NULL,
                stotal INTEGER NOT NULL
            );
            """)

            cursor.executescript("""
            INSERT INTO member VALUES ('M001', 'Alice', '0912-345678', 'alice@example.com');
            INSERT INTO member VALUES ('M002', 'Bob', '0923-456789', 'bob@example.com');
            INSERT INTO member VALUES ('M003', 'Cathy', '0934-567890', 'cathy@example.com');

            INSERT INTO book VALUES ('B001', 'Python Programming', 600, 50);
            INSERT INTO book VALUES ('B002', 'Data Science Basics', 800, 30);
            INSERT INTO book VALUES ('B003', 'Machine Learning Guide', 1200, 20);

            INSERT INTO sale (sdate, mid, bid, sqty, sdiscount, stotal) VALUES ('2024-01-15', 'M001', 'B001', 2, 100, 1100);
            INSERT INTO sale (sdate, mid, bid, sqty, sdiscount, stotal) VALUES ('2024-01-16', 'M002', 'B002', 1, 50, 750);
            INSERT INTO sale (sdate, mid, bid, sqty, sdiscount, stotal) VALUES ('2024-01-17', 'M001', 'B003', 3, 200, 3400);
            INSERT INTO sale (sdate, mid, bid, sqty, sdiscount, stotal) VALUES ('2024-01-18', 'M003', 'B001', 1, 0, 600);
            """)
            conn.commit()
            print("✅ 資料表建立完成")
        else:
            print("✅ 所有資料表皆已存在")




def StartMenu() -> int | str:
    """
    顯示主選單並接收使用者輸入。

    Returns:
        int: 使用者選擇的功能項目（1 到 5）
        str: 若直接按 Enter 則回傳空字串表示離開
    """
    while True:
        print("***************選單***************")
        print("1. 新增銷售記錄")
        print("2. 顯示銷售報表")
        print("3. 更新銷售記錄")
        print("4. 刪除銷售記錄")
        print("5. 離開")
        print("**********************************")
        try:
            inp = input("請選擇操作項目(Enter 離開)：")
            if inp == "":
                return ""

            if 1 <= int(inp) <= 5:
                return int(inp)
            else:
                raise ValueError()
        except ValueError:
            print("=> 請輸入有效的選項（1-5）")

def NewSales() -> None:
    """
    建立一筆新的銷售記錄，透過使用者輸入資料進行驗證與資料庫新增。

    操作流程：
    - 輸入銷售日期（格式 YYYY-MM-DD）
    - 輸入會員編號與書籍編號
    - 輸入購買數量與折扣金額（需為正整數）
    - 驗證書籍是否存在與庫存是否足夠
    - 寫入銷售資料表

    Returns:
        None
    """
    while True:
        while True:
            try:
                sdate = input("請輸入銷售日期 (YYYY-MM-DD)：")
                if len(sdate) == 10 and sdate.count('-') == 2:
                    break
                else:
                    print('=> 錯誤：銷售日期格式錯誤，請重新輸入')
            except ValueError:
                print('=> 錯誤：銷售日期格式錯誤，請重新輸入')

        mid = input("請輸入會員編號：")
        bid = input("請輸入書籍編號：")

        while True:
            try:
                sqty = int(input("請輸入購買數量："))
                if sqty > 0:
                    break
                else:
                    print('=> 錯誤：數量必須為正整數，請重新輸入')
            except ValueError:
                print('=> 錯誤：數量或折扣必須為整數，請重新輸入')

        while True:
            try:
                sdiscount = int(input("請輸入折扣金額："))
                if sdiscount > 0:
                    break
                else:
                    print('=> 錯誤：折扣必須為正整數，請重新輸入')
            except ValueError:
                print('=> 錯誤：數量或折扣必須為整數，請重新輸入')

        bprice = DBTOOL.DBSelect("book", ["bprice"], "bid", bid)
        if bprice and bprice[0]:
            num = DBTOOL.DBSelect("book", ["bstock"], "bid", bid)
            if int(num[0][0]) < sqty:
                print(f"=> 錯誤：書籍庫存不足 (現有庫存: {int(num[0][0])})")
                continue

            stotal = (int(bprice[0][0]) * sqty) - sdiscount
            IsSuccess = DBTOOL.DBInsert(
                "sale", SaleTable, [
                    sdate, mid, bid, sqty, sdiscount, stotal])
            if IsSuccess:
                print(f"=> 銷售記錄已新增！(銷售總額: {stotal})")
                break
            else:
                print("=> 錯誤：會員編號或書籍編號無效")
                break
        else:
            print("=> 錯誤：會員編號或書籍編號無效")
            break

def SalesReport() -> None:
    """
    顯示完整銷售報表：
    - 包含會員資訊與書籍資料
    - 顯示單筆銷售的詳細資訊（編號、日期、單價、數量、折扣、小計）

    Returns:
        None
    """
    with sqlite3.connect("bookstore.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
        SELECT * FROM sale
        JOIN member ON sale.mid = member.mid
        JOIN book ON sale.bid = book.bid
        ORDER BY sale.sid;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        print()
        print("==================== 銷售報表 ====================")
        for row in rows:
            print(f"銷售 #{row['sid']}")
            print(f"銷售編號: {row['sid']}")
            print(f"銷售日期: {row['sdate']}")
            print(f"會員姓名: {row['mname']}")
            print(f"書籍標題: {row['btitle']}")
            print("--------------------------------------------------")
            print(f"{'單價'.ljust(12 - count_chinese('單價'))}"
                  f"{'數量'.ljust(12 - count_chinese('數量'))}"
                  f"{'折扣'.ljust(12 - count_chinese('折扣'))}"
                  f"{'小計'.ljust(12 - count_chinese('小計'))}")
            print("--------------------------------------------------")
            print(f"{row['bprice']:<12}{row['sqty']:<12}{row['sdiscount']:<12}{row['stotal']:<12}")
            print("==================== 銷售報表 ====================")
            print("")



def SalesUpdate() -> None:
    """
    更新一筆銷售記錄的折扣金額：
    - 顯示所有銷售資料供使用者選擇
    - 根據 sid 修改折扣金額欄位
    - 重新計算總金額並顯示更新結果

    Returns:
        None
    """
    with sqlite3.connect("bookstore.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
        SELECT * FROM sale
        JOIN member ON sale.mid = member.mid
        ORDER BY sale.sid;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        print()
        print("======== 銷售記錄列表 ========")
        i = 1
        for row in rows:
            print(f"{i}. 銷售編號: {row['sid']} - 會員: {row['mname']} - 日期: {row['sdate']}")
            i += 1
        print("================================")

        while True:
            try:
                sid = input("請選擇要更新的銷售編號 (輸入數字或按 Enter 取消):")
                if sid == "":
                    return
                elif int(sid) > 0:
                    int(sid)
                    break
                else:
                    print('=> 錯誤：銷售編號必須為正整數，請重新輸入')
            except ValueError:
                print('=> 錯誤：銷售編號或折扣必須為整數，請重新輸入')

        while True:
            try:
                sdiscount = int(input("請輸入新的折扣金額："))
                if sdiscount > 0:
                    break
                else:
                    print('=> 錯誤：數量必須為正整數，請重新輸入')
            except ValueError:
                print('=> 錯誤：數量或折扣必須為整數，請重新輸入')

        IsSuccess = DBTOOL.DBUpdate(
            "sale", ["sdiscount"], [sdiscount], "sid", sid)
        if IsSuccess:
            bid = DBTOOL.DBSelect("sale", ["bid", "sqty"], "sid", sid)
            bprice = DBTOOL.DBSelect("book", ["bprice"], "bid", bid[0][0])
            stotal = (int(bprice[0][0]) * bid[0][1]) - sdiscount
            print(f"=> 銷售編號 {sid} 已更新！(銷售總額: {stotal})")



def SalesDelete() -> None:
    """
    刪除一筆銷售記錄：
    - 顯示所有銷售資料供使用者選擇
    - 根據使用者輸入的 sid 進行刪除
    - 若輸入不合法則提示錯誤

    Returns:
        None
    """
    with sqlite3.connect("bookstore.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
        SELECT * FROM sale
        JOIN member ON sale.mid = member.mid
        ORDER BY sale.sid;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        print()
        print("======== 銷售記錄列表 ========")
        i = 1
        for row in rows:
            print(f"{i}. 銷售編號: {row['sid']} - 會員: {row['mname']} - 日期: {row['sdate']}")
            i += 1
        print("================================")

        while True:
            try:
                sid = input("請選擇要刪除的銷售編號 (輸入數字或按 Enter 取消): ")
                if sid == "":
                    return
                elif int(sid) > 0:
                    exists = False
                    for row in rows:
                        if row['sid'] == int(sid):
                            exists = True
                            break
                    if exists:
                        DBTOOL.DBDelete("sale", "sid", sid)
                        print(f"=> 銷售編號 {sid} 已刪除")
                        return
                    else:
                        print("=> 錯誤：請輸入有效的數字")
                else:
                    print('=> 錯誤：銷售編號必須為正整數，請重新輸入')
            except ValueError:
                print('=> 錯誤：銷售編號或折扣必須為整數，請重新輸入')

def main():
    initialize_database()
    while (True):
        Choose = StartMenu()
        if (Choose == 1):
            NewSales()
        elif (Choose == 2):
            SalesReport()
        elif (Choose == 3):
            SalesUpdate()
        elif (Choose == 4):
            SalesDelete()
        elif (Choose == 5):
            break
        elif (Choose == ""):
            break


if __name__ == "__main__":
    main()
