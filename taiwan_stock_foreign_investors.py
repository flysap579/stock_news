import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

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

            # 打印原始表格的前幾行以確認數據
            print("Original DataFrame head:")
            print(df.head())

            # 分割第一列為兩列
            if df.shape[1] > 0:
                # 假設第一列是合併了類別和日期，需要分割
                df[['類別', '日期']] = df.iloc[:, 0].str.extract(r'(.+?)(\d{4}/\d{2}/\d{2})')
                df = df[['類別', '日期'] + df.columns[1:].tolist()]

            # 打印分割後的表格以確認結果
            print("Modified DataFrame head:")
            print(df.head())

            # 格式化數字
            def format_number(x):
                try:
                    return f'{int(x):,}'  # 將數字格式化為帶有逗號的格式
                except (ValueError, TypeError):
                    return x

            # 應用格式化
            df = df.applymap(format_number)

            # 打印格式化後的表格
            print("Formatted DataFrame head:")
            print(df.head())

            # 設置 matplotlib 字體以支持中文字符
            plt.rcParams['font.family'] = 'SimHei'  # 設置為支持中文的字體
            plt.rcParams['font.size'] = 80

            # 將 DataFrame 繪製為圖片
            fig, ax = plt.subplots(figsize=(8, 4), dpi=800)  # 設置更高解析度
            ax.axis('off')  # 隱藏坐標軸
            table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 3)  # 調整表格縮放比例

            # 將圖片保存為 bytes
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
            buf.seek(0)

            image = Image.open(buf)
            return buf.getvalue()  # 返回圖片的 bytes
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
        print(f'Notification sent successfully! Status Code: {response.status_code}')
        print(f'Response Text: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'Failed to send notification. Error: {str(e)}')

if __name__ == "__main__":
    token = 'PDd9np9rpELBAoRBZJ6GEtv4NROA4lwVKNFZdRhLMVf'  # 使用你的 LINE Notify token
    image_bytes = fetch_taiwan_stock_data()
    if image_bytes:
        send_line_notify(image_bytes, token)
    else:
        print("Failed to fetch or generate image.")
