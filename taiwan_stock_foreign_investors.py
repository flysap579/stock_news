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

            # 打印表格的前幾行以確認數據
            print("Original DataFrame head:")
            print(df.head())

            # 假設需要處理的合併列是第一列，並且第一行和第二行合併在一起
            if df.shape[1] > 0:
                # 提取列標題
                header = df.iloc[0, 0].split(' ', 1)
                # 更新列名
                new_columns = [header[0], header[1]] + df.columns[1:].tolist()
                df.columns = new_columns

                # 移除第一行（已經用來做列名）
                df = df[1:]

                # 格式化數字
                def format_number(x):
                    try:
                        return f'{int(x):,}'  # 將數字格式化為帶有逗號的格式
                    except (ValueError, TypeError):
                        return x

                # 應用格式化
                df = df.applymap(format_number)

                # 打印修改後的表格前幾行
                print("Modified DataFrame head:")
                print(df.head())

                # 設置 matplotlib 字體以支持中文字符
                plt.rcParams['font.family'] = 'SimHei'  # 設置為支持中文的字體
                plt.rcParams['font.size'] = 10

                # 創建圖片
                fig, ax = plt.subplots(figsize=(14, 8), dpi=150)  # 設置更高解析度
                ax.axis('off')  # 隱藏坐標軸
                
                # 顯示表格標題
                title = '三大法人買賣金額統計表'
                ax.text(0.5, 1.05, title, fontsize=14, ha='center', va='center', fontweight='bold')
                
                # 顯示表格內容
                table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1.2, 1.2)  # 調整表格縮放比例

                # 將圖片保存為 bytes
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
                buf.seek(0)

                image = Image.open(buf)
                return buf.getvalue()  # 返回圖片的 bytes
            else:
                return None
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
