import akshare as ak
import requests
import os

def analyze():
    try:
        # 1. 抓取港股待上市列表
        df = ak.stock_hk_ipo_wait_list()
        if df.empty:
            return "今日无待上市股票数据。"

        # 2. 简单的评分逻辑 (这里可以根据你的策略调整)
        report = ["【港股打新每日分析】"]
        for _, row in df.iterrows():
            name = row['股票名称']
            # 模拟评分：这里你可以根据发行价、中签率等字段写逻辑
            # 目前以演示为主，直接给一个基于随机和行业热度的模拟分
            score = 60 
            advice = "建议参与" if score > 75 else "观望"
            report.append(f"📌 {name} | 评分: {score} | 建议: {advice}")
        
        return "\n".join(report)
    except Exception as e:
        return f"分析出错: {str(e)}"

def send_msg(content):
    # 从环境变量读取 Key 保证安全
    push_key = os.getenv("PUSH_KEY")
    requests.get(f"https://api2.pushdeer.com/send?pushkey={push_key}&text={content}")

if __name__ == "__main__":
    result = analyze()
    send_msg(result)
