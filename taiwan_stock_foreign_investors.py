import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

def fetch_taiwan_stock_data():
    try:
        url = 'https://www.twse.com.tw/rwd/zh/fund/BFI82U?response=html'
        response = requests.get(url)
        response.raise_for_status()  # 確保 HTTP 請求成功

        html_content = response.text

        # 使用 pandas 解析 HTML 表格
        tables = pd.read_html(html_content, flavor='lxml')
        if tables:
            df = pd.concat(tables, ignore_index=True)
            
            # 打印表格的前幾行以確認數據
            print("DataFrame head:")
            print(df.head())

            # 設置 matplotlib 字體以支持中文字符
            plt.rcParams['font.family'] = 'Noto Sans CJK'  # 確保使用的字體正確
            plt.rcParams['font.size'] = 10

            # 將 DataFrame 繪製為圖片
            fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
            ax.axis('off')
            table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.5, 1.5)

            # 將圖片保存為 bytes
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
            buf.seek(0)

            image_size = len(buf.getvalue())
            print(f'Generated image size: {image_size} bytes')
            return buf.getvalue()
        else:
            return None
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

def send_line_notify(image_bytes, token):
    try:
        url = 'https://notify-api.line.me/api/notify'
        headers = {
            'Authorization': f'Bearer {token}'
        }
        files = {
            'imageFile': ('stock_data.png', image_bytes, 'image/png')
        }
        data = {
            'message': '三大法人買賣金額'
        }
        response = requests.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()  # 確保 POST 請求成功
        print(f'Status Code: {response.status_code}')
        print(f'Response Text: {response.text}')
        print('Notification sent successfully!')
    except requests.exceptions.RequestException as e:
        print(f'Failed to send notification. Error: {str(e)}')

if __name__ == "__main__":
    token = 'PDd9np9rpELBAoRBZJ6GEtv4NROA4lwVKNFZdRhLMVf'
    image_bytes = fetch_taiwan_stock_data()
    if image_bytes:
        send_line_notify(image_bytes, token)
    else:
        print("Failed to fetch or generate image.")
