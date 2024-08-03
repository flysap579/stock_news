from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests

def fetch_taiwan_stock_data():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 無頭模式（不顯示瀏覽器）

        # 使用 WebDriver Manager 自動下載和管理 ChromeDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        url = 'https://www.twse.com.tw/zh/trading/foreign/bfi82u.html'
        driver.get(url)

        # 使用顯式等待來等待表格加載完成
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table.table-striped.table-bordered'))
            )
        except Exception as e:
            print(f'Error while waiting for table element: {str(e)}')
            driver.quit()
            return "未找到表格元素。"

        # 查找數據表格
        table = driver.find_element(By.CSS_SELECTOR, 'table.table.table-striped.table-bordered')
        html_content = table.get_attribute('outerHTML')

        driver.quit()

        # 使用 pandas 解析 HTML 表格
        df = pd.read_html(html_content, flavor='lxml')[0]

        # 打印表格的前幾行以確認數據
        print("DataFrame head:")
        print(df.head())

        df.columns = df.iloc[0]  # 第一行是表頭
        df = df[1:]  # 去掉第一行表頭
        df.columns = df.columns.str.strip()  # 去掉列名中的空格

        # 查找最近一天的數據
        if '日期' in df.columns:
            recent_date = df['日期'].max()
            recent_data = df[df['日期'] == recent_date]

            # 格式化為字符串
            message = recent_data.to_string(index=False)
            return f"最近一天（三大法人買賣金額）\n\n{message}"
        else:
            return "未找到日期列。請檢查網頁表格結構。"
    except Exception as e:
        return f"Error occurred: {str(e)}"

def send_line_notify(message, token):
    try:
        url = 'https://notify-api.line.me/api/notify'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'message': message
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # 確保 POST 請求成功
        print(f'Notification sent successfully! Status Code: {response.status_code}')
        print(f'Response Text: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'Failed to send notification. Error: {str(e)}')

if __name__ == "__main__":
    token = 'PDd9np9rpELBAoRBZJ6GEtv4NROA4lwVKNFZdRhLMVf'  # 替換為你的 LINE Notify token
    stock_data = fetch_taiwan_stock_data()
    print(f'Stock Data:\n{stock_data}')  # 輸出抓取的數據
    send_line_notify(stock_data, token)
