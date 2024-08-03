import requests
import pandas as pd
from io import StringIO

def fetch_taiwan_stock_data():
    try:
        url = 'https://www.twse.com.tw/zh/trading/foreign/bfi82u.html'
        response = requests.get(url)
        response.raise_for_status()  # 確保 HTTP 請求成功

        html_content = StringIO(response.text)

        # 嘗試使用不同的解析器來解析 HTML
        try:
            tables = pd.read_html(html_content, flavor='lxml')
        except ValueError:
            try:
                tables = pd.read_html(html_content, flavor='html5lib')
            except Exception as e:
                return f"Error occurred while parsing HTML: {str(e)}"

        if tables:
            df = tables[0]
            return df.to_string(index=False)
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
    message = f"今日台灣股市三大法人買賣金額統計表：\n\n{stock_data}"
    send_line_notify(message, token)
