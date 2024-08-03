import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

def fetch_taiwan_stock_data():
    try:
        url = 'https://www.twse.com.tw/rwd/zh/fund/BFI82U?response=html'
        response = requests.get(url)
        response.raise_for_status()  # 确保 HTTP 请求成功

        html_content = response.text

        # 使用 pandas 解析 HTML 表格
        tables = pd.read_html(html_content, flavor='lxml')
        if tables:
            # 合并所有表格的数据
            df = pd.concat(tables, ignore_index=True)

            # 格式化数字
            def format_number(x):
                try:
                    # 将数字转换为浮点数
                    value = float(x)
                    # 四舍五入至亿元（即以 1e8 为单位）
                    value_in_billion = round(value / 1e8, 2)
                    # 返回格式化后的字符串，并添加「亿元」单位
                    return f'{value_in_billion} 億元'
                except (ValueError, TypeError):
                    return x  # 如果转换失败，返回原始值

            # 应用格式化
            df = df.applymap(format_number)

            # 打印表格的前几行以确认数据
            print("DataFrame head:")
            print(df.head())

            # 设置 matplotlib 字体以支持中文字符
            plt.rcParams['font.family'] = 'SimHei'
            plt.rcParams['font.size'] = 12

            # 计算图片大小
            num_rows, num_cols = df.shape
            fig_width = max(num_cols * 2, 10)  # 每列宽度约为2单位，最小宽度10
            fig_height = max(num_rows * 0.4, 6)  # 每行高度约为0.4单位，最小高度6

            # 将 DataFrame 绘制为图片
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
            ax.axis('off')  # 隐藏坐标轴

            # 显示表格内容
            table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.auto_set_column_width(range(len(df.columns)))  # 自动调整列宽

            # 将图片保存为 bytes
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
            buf.seek(0)

            image = Image.open(buf)
            return buf.getvalue()  # 返回图片的 bytes
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
        response.raise_for_status()  # 确保 POST 请求成功
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
