#!/usr/bin/env python3
# ICKG 知识图谱采集系统 - 启动脚本
# v5.0

"""
一键启动采集系统
"""

import json
from pathlib import Path
from src.collector import KGCollector
from src.llm_client import LLMClient, LLMConfig


def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def main():
    print("=" * 70)
    print("🚀 ICKG 知识图谱采集系统 v5.0")
    print("=" * 70)
    
    # 加载配置
    config = load_config()
    companies = config.get("companies", [
        "中芯国际", "华虹公司", "长江存储", "台积电", "三星电子",
        "高通", "联发科", "英飞凌", "恩智浦", "意法半导体"
    ])
    news_per_company = config.get("news_per_company", 6)
    output_dir = config.get("output_dir", "output")
    api_key = config.get("api_key", "")
    endpoint_id = config.get("endpoint_id", "")
    
    # 显示配置
    print(f"\n📋 采集配置:")
    print(f"   企业数: {len(companies)} 家")
    print(f"   每企业新闻数: {news_per_company} 条")
    print(f"   输出目录: {output_dir}/")
    print(f"   API密钥: {'✓ 已配置' if api_key else '✗ 未配置'}")
    
    print(f"\n📌 待采集企业 (前10个):")
    for i, company in enumerate(companies[:10], 1):
        print(f"   {i}. {company}")
    if len(companies) > 10:
        print(f"   ... 以及其他 {len(companies) - 10} 家企业")
    
    # 确认开始
    print(f"\n{'='*70}")
    confirm = input("确认开始采集? (y/n): ").strip().lower()
    print(f"{'='*70}")
    
    if confirm != 'y':
        print("已取消采集")
        return
    
    # 初始化 LLM 客户端
    llm_config = LLMConfig(
        api_key=api_key,
        endpoint_id=endpoint_id
    )
    
    # 运行采集
    with LLMClient(llm_config) as llm_client:
        collector = KGCollector(llm_client)
        collector.batch_collect(companies, news_per_company)


if __name__ == "__main__":
    main()

