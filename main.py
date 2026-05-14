import akshare as ak
import requests
import os
import pandas as pd
import json

def analyze():
    try:
        # 直接访问东方财富的港股新股数据接口（这是一个公开的 JSON 接口）
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_HK_IPO_LIST&columns=ALL&quoteType=0&pageNumber=1&pageSize=50&sortColumns=LISTING_DATE&sortTypes=-1"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # 提取股票列表
        stock_list = data.get('result', {}).get('data', [])
        
        if not stock_list:
            return "目前没有查询到待上市的港股数据。"

        report = ["📊 【港股打新每日分析】"]
        
        for stock in stock_list:
            name = stock.get('SECURITY_NAME_ABBR', '未知股票')
            # 过滤掉已经上市的（根据你的需求，可以判断上市日期）
            # 这里简单抓取前 5 个即将上市或刚上市的
            code = stock.get('SECURITY_CODE', 'N/A')
            industry = stock.get('INDUSTRY', '未知行业')
            
            # 你的核心打分逻辑
            score = 70 # 默认分
            if "医疗" in industry or "科技" in industry: score += 10
            
            report.append(f"--------------------\n📌 {name} ({code})\n行业: {industry}\n📈 评分: {score}")
            
            if len(report) >= 6: break # 每天只看前 5 个最热的

        return "\n".join(report)

    except Exception as e:
        return f"接口抓取失败: {str(e)}"

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
