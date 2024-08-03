import requests
import pandas as pd
from io import StringIO

def fetch_taiwan_stock_data():
    url = 'https://www.twse.com.tw/zh/trading/foreign/bfi82u.html'
    response = requests.get(url)
    
    if response.status_code == 200:
        html_content = StringIO(response.text)
        tables = pd.read_html(html_content)
        if tables:
            df = tables[0]
            return df.to_string(index=False)
        else:
            return "No tables found on the webpage."
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'message': message
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print('Notification sent successfully!')
    else:
        print(f'Failed to send notification. Status code: {response.status_code}')

if __name__ == "__main__":
    token = 'YOUR_ACCESS_TOKEN_HERE'  # Replace with your LINE Notify token
    stock_data = fetch_taiwan_stock_data()
    message = f"今日台灣股市三大法人買賣金額統計表：\n\n{stock_data}"
    send_line_notify(message, token)
