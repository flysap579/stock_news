name: Send Taiwan Stock Data to LINE Notify

on:
  schedule:
    - cron: '0 10 * * *' # 每天 UTC 10:00 觸發，可以根據需要調整時間
  workflow_dispatch: # 允許手動觸發工作流程

jobs:
  send_stock_data:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3 # 更新為最新版本

    - name: Set up Python
      uses: actions/setup-python@v3 # 更新為最新版本
      with:
        python-version: '3.x' # 使用 Python 3.x 版本

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install matplotlib pillow requests pandas beautifulsoup4 lxml html5lib

    - name: Install SimHei font
      run: |
        mkdir -p ~/.fonts
        wget -O ~/.fonts/SimHei.ttf https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf
        fc-cache -fv

    - name: Run script
      env:
        LINE_NOTIFY_TOKEN: ${{ secrets.LINE_NOTIFY_TOKEN }}
      run: |
        python taiwan_stock_foreign_investors.py
