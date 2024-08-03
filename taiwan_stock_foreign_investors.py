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

            # 假設第一行為合併行，將其拆分為兩行
            if not df.empty and df.shape[0] > 0:
                first_row = df.iloc[0].values
                df.columns = first_row  # 使用合併行作為列標題
                df = df[1:]  # 移除合併行
                df.reset_index(drop=True, inplace=True)  # 重置索引

            # 格式化數字
            def format_number(x):
                try:
                    # 將數字轉換為浮點數
                    value = float(x)
                    # 四捨五入至億元（即以 1e8 為單位），保留小數點後兩位
                    value_in_billion = round(value / 1e8, 2)
                    # 返回格式化後的字符串，並添加「億元」單位
                    return f'{value_in_billion} 億元'
                except (ValueError, TypeError):
                    return x  # 如果轉換失敗，返回原始值

            # 應用格式化
            df = df.applymap(format_number)

            # 打印表格的前幾行以確認數據
            print("DataFrame head:")
            print(df.head())

            # 設置 matplotlib 字體以支持中文字符
            plt.rcParams['font.family'] = 'SimHei'  # 設置為支持中文的字體
            plt.rcParams['font.size'] = 10  # 設置字體大小

            # 計算圖片的大小以適應內容
            fig, ax = plt.subplots(figsize=(len(df.columns) * 2, len(df) * 0.6), dpi=150)  # 根據內容調整大小
            ax.axis('off')  # 隱藏坐標軸
            
            # 顯示表格標題
            title = '三大法人買賣金額統計表'
            ax.text(0.5, 1.05, title, fontsize=14, ha='center', va='center', fontweight='bold')
            
            # 顯示表格內容
            table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1.2, 1.2)  # 調整表格縮放比例

            # 將圖片保存為 bytes
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
            buf.seek(0)

            image = Image.open(buf)
            return buf.getvalue()  # 返回圖片的 bytes
        else:
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
        
        # 打印響應狀態和內容
        print(f'Status Code: {response.status_code}')
        print(f'Response Text: {response.text}')
        
        response.raise_for_status()  # 確保 POST 請求成功
        print('Notification sent successfully!')
    except requests.exceptions.RequestException as e:
        print(f'Failed to send notification. Error: {str(e)}')

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
