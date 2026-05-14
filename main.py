import akshare as ak
import requests
import os
import pandas as pd
import json

def analyze():
    try:
        # 1. 东方财富港股数据接口
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_HK_IPO_LIST&columns=ALL&quoteType=0&pageNumber=1&pageSize=50&sortColumns=LISTING_DATE&sortTypes=-1"
        
        # 2. 强化请求头，模拟真实浏览器访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://data.eastmoney.com/hk/xg/default.html", # 告诉服务器我从哪来
            "Accept": "application/json, text/plain, */*"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        # 增加状态码检查
        if response.status_code != 200:
            return f"接口返回异常，状态码: {response.status_code}"
            
        data = response.json()
        
        # 3. 防御性获取数据 (避免 NoneType 报错)
        result = data.get('result')
        if not result:
            # 打印出返回的原始数据片段，方便调试
            return f"接口逻辑改变，未找到 result 字段。原始返回: {str(data)[:100]}"
            
        stock_list = result.get('data', [])
        
        if not stock_list:
            return "目前没有查询到待上市的港股数据（列表为空）。"

        # 4. 构建报告
        report = ["📊 【港股打新每日分析】"]
        for stock in stock_list:
            name = stock.get('SECURITY_NAME_ABBR', '未知股票')
            code = stock.get('SECURITY_CODE', 'N/A')
            industry = stock.get('INDUSTRY', '未知行业')
            
            # 简单的打分逻辑：医疗/科技/人工智能加分
            score = 60
            if any(k in industry for k in ["医疗", "科技", "生物", "软件", "智能"]):
                score += 20
            
            # 只有评分大于 50 的才推送（或者你可以保留全部）
            report.append(f"--------------------\n📌 {name} ({code})\n行业: {industry}\n📈 评分: {score}")
            
            if len(report) >= 6: break # 最多取前 5 条

        return "\n".join(report)

    except Exception as e:
        return f"脚本执行发生异常: {str(e)}"

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
