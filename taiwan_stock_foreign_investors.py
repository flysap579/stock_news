import requests
import pandas as pd
from io import StringIO

def fetch_taiwan_stock_data():
    try:
        url = 'https://www.twse.com.tw/zh/trading/foreign/bfi82u.html'
        response = requests.get(url)
        response.raise_for_status()  # 確保 HTTP 請求成功

        html_content = StringIO(response.text)

        # 使用 'lxml' 解析器來解析 HTML
        tables = pd.read_html(html_content, flavor='lxml')
        if tables:
            # 假設第一個表格是我們需要的表格
            df = tables[0]
            
            # 提取最近一天的數據
            # 假設表格的第一列是日期
            # 需要根據實際表格的列名和內容來修改這部分
            df.columns = df.iloc[0]  # 第一行是表頭
            df = df[1:]  # 去掉第一行表頭
            df.columns = df.columns.str.strip()  # 去掉列名中的空格

            # 查找最近一天的數據
            recent_date = df['日期'].max()
            recent_data = df[df['日期'] == recent_date]

            # 格式化為字符串
            message = recent_data.to_string(index=False)
            return f"最近一天（三大法人買賣金額）\n\n{message}"
        else:
            return "No tables found on the webpage."
    except Exception as e:
        return f"Error occurred: {str(e)}"

def send_line_notify(message, token):
    try:
        url = 'https://notify-api.line.me/api/notify'
        headers = {
            'Authorization': f'Bearer {token}'
        }
        data = {
            'message': message
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # 確保 POST 請求成功
        print('Notification sent successfully!')
    except Exception as e:
        print(f'Failed to send notification. Error: {str(e)}')

if __name__ == "__main__":
    token = 'YOUR_ACCESS_TOKEN_HERE'  # 替換為你的 LINE Notify token
    stock_data = fetch_taiwan_stock_data()
    send_line_notify(stock_data, token)
