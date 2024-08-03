import requests
import pandas as pd
from io import StringIO

def fetch_taiwan_stock_data():
    try:
        url = 'https://www.twse.com.tw/rwd/zh/fund/BFI82U?response=html'
        response = requests.get(url)
        response.raise_for_status()  # 確保 HTTP 請求成功

        html_content = response.text

        # 使用 pandas 解析 HTML 表格
        tables = pd.read_html(html_content, flavor='lxml')
        if tables:
            # 合併所有表格的數據
            df = pd.concat(tables, ignore_index=True)
            
            # 打印表格的前幾行以確認數據
            print("DataFrame head:")
            print(df.head())

            # 格式化為字符串
            message = df.to_string(index=False)
            return f"三大法人買賣金額\n\n{message}"
        else:
            return "No tables found on the webpage."
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
