import akshare as ak
import requests
import os
import pandas as pd
import json

def analyze():
    try:
        # 换成这个：针对申购中新股的接口
        # RPT_HK_IPO_APPLY 专门指代申购/招股中的数据
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_HK_IPO_APPLY&columns=ALL&quoteType=0&pageNumber=1&pageSize=50&sortColumns=APPLY_START_DATE&sortTypes=-1"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://data.eastmoney.com/hk/xg/default.html"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        
        result = data.get('result')
        if not result:
            # 如果申购列表为空，尝试抓取“待上市”列表（过聆讯但还没开始申购或刚结束申购的）
            return "目前没有正在申购中的港股新股。"
            
        stock_list = result.get('data', [])
        
        report = ["🔔 【发现正在申购的港股】"]
        for stock in stock_list:
            name = stock.get('SECURITY_NAME_ABBR', '未知')
            code = stock.get('SECURITY_CODE', 'N/A')
            # 港股打新的关键指标：入场费、超购倍数、保荐人
            price_max = stock.get('ISSUE_PRICE_MAX', '待定')
            apply_end = stock.get('APPLY_END_DATE', 'N/A')[:10] # 截取日期
            
            # 打分逻辑升级：入场费越低、行业越热、分越高
            score = 75
            if "科技" in stock.get('INDUSTRY', ''): score += 10
            
            report.append(f"--------------------\n📌 {name} ({code})\n💰 最高发售价: {price_max} HKD\n📅 申购截止: {apply_end}\n📈 建议评分: {score}")

        return "\n".join(report)

    except Exception as e:
        return f"数据解析失败: {str(e)}"

def send_msg(content):
    push_key = os.getenv("PUSH_KEY")
    # 使用你刚才测试成功的地址：message/push
    url = "https://api2.pushdeer.com/message/push"
    
    payload = {
        "pushkey": push_key,
        "text": content,
        "type": "markdown" # 使用 markdown 格式，收到的消息排版更漂亮
    }
    
    try:
        # 建议加上 timeout=10，防止网络波动导致 Action 挂起
        response = requests.post(url, data=payload, timeout=10)
        print(f"推送状态码: {response.status_code}")
        print(f"服务器返回: {response.text}")
    except Exception as e:
        print(f"发送失败: {e}")

if __name__ == "__main__":
    result = analyze()
    send_msg(result)
