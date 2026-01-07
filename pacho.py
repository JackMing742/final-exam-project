from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3

# 建立 Chrome 瀏覽器實例 (最常用)
options = webdriver.ChromeOptions()

# 前往指定網址
url = "http://quotes.toscrape.com/js/"
options.add_argument("--incognito")
options.add_argument("--start-maximized")
options.add_argument("--disable-popup-blocking")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)
try:
    browser.get(url)
    page = 1
    wait = WebDriverWait(browser, 10)
    conn = sqlite3.connect("quotes.db")  # 連線資料庫
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS quotes")  # 防止重複抓取
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    author TEXT NOT NULL,
    tags TEXT
    );
    """
    )
    conn.commit()
    while True:
        # 限制最多抓取 5 頁
        if page > 5:
            print("抓取完畢")
            break
        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "quote"))
        )  # 等待頁面載入完成
        print(f"正在抓取第 {page} 頁的資料...")
        quotes = browser.find_elements(By.CLASS_NAME, "quote")
        for quote in quotes:
            text = quote.find_element(By.CLASS_NAME, "text").text
            author = quote.find_element(By.CLASS_NAME, "author").text
            # 取得多個標籤

            tags = [tag.text for tag in quote.find_elements(By.CLASS_NAME, "tag")]
            """tag_list = []
            tags = quote.find_elements(By.CLASS_NAME, "tag")
            for tag in tags:
                tag_list.append(tag.text)
            """
            tags_list = ", ".join(tags)
            cursor.execute(
                "INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)",
                (text, author, tags_list),
            )
            # print(f"Quote: {text}\nAuthor: {author}\nTags: {tags_list}\n")
        conn.commit()
        try:
            # 嘗試尋找下一頁按鈕
            next_button = browser.find_element(By.CSS_SELECTOR, "li.next > a")
            next_button.click()
            page += 1
        except:
            # 如果找不到下一頁按鈕，則結束迴圈
            print("換頁失敗，結束抓取")
            break
finally:
    # 執行完畢後，關閉瀏覽器以釋放資源
    browser.quit()
    conn.close()
