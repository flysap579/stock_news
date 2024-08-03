import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
from PIL import Image

def fetch_taiwan_stock_data():
    try:
        url = 'https://www.twse.com.tw/rwd/zh/fund/BFI82U?response=html'
        response = requests.get(url)
        response.raise_for_status()  # 確保 HTTP 請求成功

        html_content = response.text

        # 使用 StringIO 來處理 HTML 字串
        html_io = StringIO(html_content)
        tables = pd.read_html(html_io, flavor='lxml')
        if tables:
            # 合併所有表格的數據
            df = pd.concat(tables, ignore_index=True)

            # 格式化數字
            def format_number(x):
                try:
                    # 將數字轉換為浮點數
                    value = float(x)
                    # 四捨五入至億元（即以 1e8 為單位），保留小數點後兩位
                    value_in_billion = round(value / 1e8)
                    # 返回格式化後的字符串，並添加「億元」單位
                    return f'{value_in_billion} 億元'
                except (ValueError, TypeError):
                    return x  # 如果轉換失敗，返回原始值

            # 應用格式化
            df = df.applymap(format_number)

            # 添加日期標題行
            date_title = '113年08月03日 三大法人買賣金額統計表'
            header_row = pd.DataFrame([[''] * len(df.columns)], columns=df.columns)
            date_header = pd.DataFrame([[date_title] + [''] * (len(df.columns) - 1)], columns=df.columns)
            df_with_title = pd.concat([date_header, header_row, df], ignore_index=True)

            # 打印表格的前幾行以確認數據
            print("DataFrame head:")
            print(df_with_title.head())

            # 設置 matplotlib 字體以支持中文字符
            plt.rcParams['font.family'] = 'SimHei'  # 設置為支持中文的字體
            plt.rcParams['font.size'] = 12

            # 計算圖片大小
            num_rows, num_cols = df_with_title.shape
            fig_width = max(num_cols * 2, 10)  # 每列寬度約為2單位，最小寬度10
            fig_height = max(num_rows * 0.4, 6)  # 每行高度約為0.4單位，最小高度6

            # 將 DataFrame 繪製為圖片
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
            ax.axis('off')  # 隱藏坐標軸

            # 顯示表格內容
            table = ax.table(cellText=df_with_title.values, colLabels=df_with_title.columns, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.auto_set_column_width(range(len(df_with_title.columns)))  # 自動調整列寬

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
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/x-www-form-urlencoded'  # 添加正確的 Content-Type
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
    token = '你的_LINE_Notify_token'  # 使用你的 LINE Notify token
    image_bytes = fetch_taiwan_stock_data()
    if image_bytes:
        send_line_notify(image_bytes, token)
    else:
        print("Failed to fetch or generate image.")
