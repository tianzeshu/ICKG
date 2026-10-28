#!/usr/bin/env python3
"""
ICKG 知识图谱数据采集系统 - Bing 搜索模块
基于 Selenium + 线程池的 Web 采集流程

功能：
1. 构建搜索关键词（产业链七层）
2. Selenium 调用 Bing 搜索
3. URL 过滤与正文抓取
4. 线程池并行采集
5. 结果存储为 JSONL
"""

import sys
import json
import time
import re
import random
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 1. 数据模型定义
# ============================================================================

@dataclass
class SearchResult:
    """搜索结果"""
    title: str
    url: str
    snippet: str
    keyword: str
    crawl_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class NewsArticle:
    """新闻文章"""
    url: str
    title: str
    content: str
    publish_time: Optional[str]
    source: str
    crawl_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    keyword: str = ""
    raw_html: str = ""


@dataclass
class LLMStructuredSummary:
    """LLM 结构化摘要"""
    summary: str
    time: Optional[str]
    location: Optional[str]
    main_entities: List[str]
    industry_layers: List[str]
    relations: List[str]
    importance_score: float


# ============================================================================
# 2. 关键词构造策略（面向七层产业链本体）
# ============================================================================

class KeywordGenerator:
    """根据产业链七层本体生成搜索关键词"""
    
    # 行业层模板
    INDUSTRY_TEMPLATES = [
        "{industry} 产业链 上游 企业 名单",
        "{industry} 产业链 中游 下游 分析 报告",
        "第三代 {industry} 上游 中游 下游 产业链",
        "{industry} 产业 市场规模 竞争格局",
    ]
    
    # 企业层模板
    COMPANY_TEMPLATES = [
        "{company} 供应商 列表",
        "{company} 战略 合作 新闻",
        "{company} 投资 收购 动态",
        "{company} 年报 PDF",
        "{company} 技术 产品 发布",
    ]
    
    # 产品层模板
    PRODUCT_TEMPLATES = [
        "{product} 生产 企业",
        "{product} 主要 供应商",
        "{product} 市场份额 排名",
        "{product} 竞品 对比 分析",
    ]
    
    # 政策层模板
    POLICY_TEMPLATES = [
        "{industry} 产业 政策 文件 PDF",
        "地方政府 {industry} 支持政策",
        "国家 {industry} 发展规划",
        "{industry} 补贴 税收 优惠",
    ]
    
    # 专利层模板
    PATENT_TEMPLATES = [
        "{company} 专利 {keyword}",
        "{company} 技术 创新 专利",
        "{industry} 核心技术 专利 分析",
    ]
    
    # 报告层模板
    REPORT_TEMPLATES = [
        "{industry} 产业 研究 报告 PDF",
        "券商 研报 {industry}",
        "{industry} 市场 分析 报告",
    ]
    
    def __init__(self, industry: str = "半导体"):
        self.industry = industry
    
    def generate_industry_keywords(self) -> List[str]:
        """生成行业层关键词"""
        return [t.format(industry=self.industry) for t in self.INDUSTRY_TEMPLATES]
    
    def generate_company_keywords(self, companies: List[str]) -> List[str]:
        """生成企业层关键词"""
        keywords = []
        for company in companies:
            for template in self.COMPANY_TEMPLATES:
                keywords.append(template.format(company=company))
        return keywords
    
    def generate_product_keywords(self, products: List[str]) -> List[str]:
        """生成产品层关键词"""
        keywords = []
        for product in products:
            for template in self.PRODUCT_TEMPLATES:
                keywords.append(template.format(product=product))
        return keywords
    
    def generate_policy_keywords(self) -> List[str]:
        """生成政策层关键词"""
        return [t.format(industry=self.industry) for t in self.POLICY_TEMPLATES]
    
    def generate_patent_keywords(self, companies: List[str], keyword: str = "芯片") -> List[str]:
        """生成专利层关键词"""
        keywords = []
        for company in companies:
            for template in self.PATENT_TEMPLATES:
                keywords.append(template.format(company=company, keyword=keyword, industry=self.industry))
        return keywords
    
    def generate_report_keywords(self) -> List[str]:
        """生成报告层关键词"""
        return [t.format(industry=self.industry) for t in self.REPORT_TEMPLATES]
    
    def generate_all_keywords(self, companies: List[str], products: List[str]) -> List[Dict]:
        """生成所有层级的关键词"""
        all_keywords = []
        
        # 行业层
        for kw in self.generate_industry_keywords():
            all_keywords.append({"keyword": kw, "layer": "industry"})
        
        # 企业层
        for kw in self.generate_company_keywords(companies):
            all_keywords.append({"keyword": kw, "layer": "company"})
        
        # 产品层
        for kw in self.generate_product_keywords(products):
            all_keywords.append({"keyword": kw, "layer": "product"})
        
        # 政策层
        for kw in self.generate_policy_keywords():
            all_keywords.append({"keyword": kw, "layer": "policy"})
        
        # 专利层
        for kw in self.generate_patent_keywords(companies):
            all_keywords.append({"keyword": kw, "layer": "patent"})
        
        # 报告层
        for kw in self.generate_report_keywords():
            all_keywords.append({"keyword": kw, "layer": "report"})
        
        return all_keywords


# ============================================================================
# 3. WebDriver 搜索模块
# ============================================================================

class BingSearcher:
    """使用 Selenium + undetected-chromedriver 进行 Bing 搜索"""
    
    # 要屏蔽的域名
    BLOCKED_DOMAINS = [
        'zhihu.com', 'xiaohongshu.com', 'bilibili.com',
        'weibo.com', 'tiktok.com', 'douyin.com',
        'linkedin.com', 'twitter.com', 'facebook.com',
        'youtube.com', 'instagram.com'
    ]
    
    # 要跳过的文件扩展名
    SKIP_EXTENSIONS = [
        '.pdf', '.pptx', '.docx', '.xlsx', '.xls',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.mp4', '.mp3', '.jpg', '.jpeg', '.png', '.gif', '.svg'
    ]
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
    
    def init_driver(self):
        """初始化 WebDriver"""
        try:
            # 尝试使用 undetected-chromedriver（反反爬）
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # 设置常规选项
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            
            # 设置User-Agent
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # 隐藏自动化特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            logger.info("WebDriver 初始化成功（undetected-chromedriver）")
            return True
            
        except ImportError:
            # 如果没有 undetected-chromedriver，使用普通 selenium
            logger.warning("未安装 undetected-chromedriver，使用普通 Selenium")
            return self._init_selenium_driver()
        except Exception as e:
            logger.error(f"WebDriver 初始化失败: {e}")
            return False
    
    def _init_selenium_driver(self):
        """初始化普通 Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = Options()
            
            if self.headless:
                options.add_argument('--headless=new')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 隐藏自动化特征
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            
            # 执行反检测脚本
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
            
            logger.info("WebDriver 初始化成功（普通 Selenium）")
            return True
            
        except Exception as e:
            logger.error(f"Selenium WebDriver 初始化失败: {e}")
            return False
    
    def search(self, keyword: str, max_results: int = 10) -> List[SearchResult]:
        """执行 Bing 搜索并返回结果"""
        results = []
        
        if not self.driver:
            if not self.init_driver():
                return results
        
        try:
            # 打开 Bing
            self.driver.get("https://www.bing.com")
            
            # 等待页面加载
            time.sleep(random.uniform(1, 2))
            
            # 找到搜索框并输入
            search_box = self.driver.find_element("name", "q")
            search_box.clear()
            search_box.send_keys(keyword)
            
            # 点击搜索按钮
            search_button = self.driver.find_element("id", "search_icon")
            search_button.click()
            
            # 等待结果加载
            time.sleep(random.uniform(2, 3))
            
            # 滚动页面以加载更多结果
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
            
            # 解析搜索结果
            from selenium.webdriver.common.by import By
            
            # Bing 结果容器
            result_cards = self.driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
            
            for card in result_cards[:max_results]:
                try:
                    # 提取标题
                    title_elem = card.find_element(By.CSS_SELECTOR, "h2 a")
                    title = title_elem.text.strip()
                    url = title_elem.get_attribute("href")
                    
                    # 提取摘要
                    try:
                        snippet = card.find_element(By.CSS_SELECTOR, ".b_caption p").text.strip()
                    except:
                        snippet = ""
                    
                    # 过滤
                    if self._should_include(url):
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            keyword=keyword
                        ))
                        
                except Exception as e:
                    continue
            
            logger.info(f"关键词 '{keyword}' 搜索到 {len(results)} 条结果")
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
        
        return results
    
    def _should_include(self, url: str) -> bool:
        """判断 URL 是否应该保留"""
        url_lower = url.lower()
        
        # 检查是否包含屏蔽域名
        for domain in self.BLOCKED_DOMAINS:
            if domain in url_lower:
                return False
        
        # 检查文件扩展名
        for ext in self.SKIP_EXTENSIONS:
            if url_lower.endswith(ext):
                return False
        
        # 只保留 HTTP/HTTPS 链接
        if not url_lower.startswith("http"):
            return False
        
        return True
    
    def close(self):
        """关闭 WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None


# ============================================================================
# 4. URL 过滤策略
# ============================================================================

class URLFilter:
    """URL 过滤策略"""
    
    # 新闻来源白名单（只保留这些来源）
    NEWS_WHITELIST = [
        'finance.sina.com.cn', 'tech.sina.com.cn',
        'xueqiu.com', 'p.stcn.com',
        'finance.eastmoney.com', 'guba.eastmoney.com',
        '36kr.com', 'tech.36kr.com',
        'ifeng.com', 'news.ifeng.com',
        'qq.com', 'finance.qq.com',
        'jrj.com.cn', 'stock.jrj.com.cn',
        'stcn.com', 'tech.stcn.com',
        'thepaper.cn', 'news.thepaper.cn',
        'caixin.com', 'm.caixin.com',
        'jiemian.com', 'jiemian.com',
        'cctime.com.cn', 'cable.abc.net.cn'
    ]
    
    BLOCKED_DOMAINS = [
        'zhihu.com', 'xiaohongshu.com', 'bilibili.com',
        'weibo.com', 'tiktok.com', 'douyin.com',
        'linkedin.com', 'twitter.com', 'facebook.com',
        'youtube.com', 'instagram.com', 'pinduoduo.com'
    ]
    
    SKIP_EXTENSIONS = [
        '.pdf', '.pptx', '.docx', '.xlsx', '.xls',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.mp4', '.mp3', '.jpg', '.jpeg', '.png', 
        '.gif', '.svg', '.ico', '.css', '.js'
    ]
    
    def is_valid_news_url(self, url: str) -> bool:
        """判断是否为有效的新闻 URL"""
        url_lower = url.lower()
        
        # 检查协议
        if not url_lower.startswith("http"):
            return False
        
        # 检查扩展名
        for ext in self.SKIP_EXTENSIONS:
            if url_lower.endswith(ext):
                return False
        
        # 检查屏蔽域名
        for domain in self.BLOCKED_DOMAINS:
            if domain in url_lower:
                return False
        
        # 检查是否在白名单中（至少匹配一个）
        for source in self.NEWS_WHITELIST:
            if source in url_lower:
                return True
        
        # 如果不在白名单，检查是否为其他可接受的新闻网站
        if any(x in url_lower for x in ['news.', 'finance.', 'tech.', 'stock.']):
            return True
        
        return False


# ============================================================================
# 5. 正文抓取模块
# ============================================================================

class NewsCrawler:
    """新闻正文抓取器"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        
        # 初始化 session 和重试适配器
        import httpx
        from urllib3.util.retry import Retry
        from urllib3.util import Retry
        
        self.session = httpx.Client(timeout=timeout)
    
    def fetch_article(self, url: str, keyword: str = "") -> Optional[NewsArticle]:
        """抓取文章正文"""
        try:
            response = self.session.get(url, follow_redirects=True)
            
            if response.status_code != 200:
                logger.warning(f"请求失败 [{response.status_code}]: {url}")
                return None
            
            # 检测编码
            response.encoding = response.apparent_encoding or 'utf-8'
            html = response.text
            
            # 使用 BeautifulSoup 解析
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 移除干扰元素
            for tag in soup(["script", "style", "nav", "header", "footer", 
                           "aside", "iframe", "noscript", "form"]):
                tag.decompose()
            
            # 提取标题
            title = ""
            if soup.title:
                title = soup.title.string or ""
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "") or title
            
            # 提取正文
            text_parts = []
            
            # 方法1: article 标签
            article = soup.find("article")
            if article:
                for p in article.find_all("p"):
                    t = p.get_text(strip=True)
                    if len(t) > 50:
                        text_parts.append(t)
            
            # 方法2: class 包含 content/text/article/main
            if not text_parts:
                for div in soup.find_all("div", class_=re.compile(
                    r'content|text|article|main|body|detail|news', re.I)):
                    for p in div.find_all("p"):
                        t = p.get_text(strip=True)
                        if len(t) > 50:
                            text_parts.append(t)
                    if len(text_parts) > 5:
                        break
            
            # 方法3: body 中找段落
            if not text_parts:
                body = soup.find("body")
                if body:
                    for p in body.find_all("p"):
                        t = p.get_text(strip=True)
                        if len(t) > 100:
                            text_parts.append(t)
            
            # 清理文本
            text = "\n".join(text_parts)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            if len(text) < 200:
                logger.warning(f"正文太短 ({len(text)} 字符): {url}")
                return None
            
            # 提取发布时间
            publish_time = self._extract_publish_time(soup)
            
            return NewsArticle(
                url=url,
                title=title[:200],
                content=text,
                publish_time=publish_time,
                source=url,
                keyword=keyword,
                raw_html=html[:5000]
            )
            
        except Exception as e:
            logger.error(f"抓取失败: {url} - {e}")
            return None
    
    def _extract_publish_time(self, soup) -> Optional[str]:
        """提取发布时间"""
        # 尝试多种方式
        time_selectors = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "publishdate"}),
            ("meta", {"name": "date"}),
            ("time", {}),
        ]
        
        for selector in time_selectors:
            tag = soup.find(selector[0], attrs=selector[1])
            if tag:
                time_str = tag.get("content") or tag.get("datetime") or tag.get("class")
                if time_str:
                    # 尝试解析时间
                    try:
                        # 常见格式: 2024-01-15 或 2024-01-15T10:30:00
                        match = re.search(r'(\d{4}-\d{2}-\d{2})', str(time_str))
                        if match:
                            return match.group(1)
                    except:
                        pass
        
        return None
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()


# ============================================================================
# 6. 主采集流程
# ============================================================================

class ICKGCollector:
    """ICKG 知识图谱数据采集器"""
    
    def __init__(self, output_dir: str = "data", max_workers: int = 10):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_workers = max_workers
        self.searcher = BingSearcher(headless=True)
        self.crawler = NewsCrawler()
        self.filter = URLFilter()
        
        # 统计
        self.stats = {
            "keywords_searched": 0,
            "urls_found": 0,
            "articles_crawled": 0,
            "start_time": None,
            "end_time": None
        }
    
    def run(self, companies: List[str], products: List[str], industry: str = "半导体"):
        """执行完整采集流程"""
        self.stats["start_time"] = datetime.now()
        
        logger.info("=" * 60)
        logger.info("ICKG 数据采集开始")
        logger.info("=" * 60)
        
        # 1. 生成关键词
        generator = KeywordGenerator(industry=industry)
        all_keywords = generator.generate_all_keywords(companies, products)
        
        logger.info(f"生成 {len(all_keywords)} 个搜索关键词")
        
        # 2. Bing 搜索（使用 Selenium）
        logger.info("\n=== 阶段 1: Bing 搜索 ===")
        all_results = []
        
        # 初始化 WebDriver
        if not self.searcher.init_driver():
            logger.error("WebDriver 初始化失败，退出")
            return
        
        try:
            for kw_info in all_keywords:
                keyword = kw_info["keyword"]
                layer = kw_info["layer"]
                
                logger.info(f"搜索 [{layer}]: {keyword}")
                
                results = self.searcher.search(keyword, max_results=10)
                
                for r in results:
                    r.keyword = keyword
                    all_results.append(r)
                
                self.stats["keywords_searched"] += 1
                
                # 随机延迟，避免被封
                time.sleep(random.uniform(1, 3))
                
        finally:
            self.searcher.close()
        
        logger.info(f"搜索完成，共找到 {len(all_results)} 条结果")
        self.stats["urls_found"] = len(all_results)
        
        # 3. URL 过滤
        logger.info("\n=== 阶段 2: URL 过滤 ===")
        filtered_results = [r for r in all_results if self.filter.is_valid_news_url(r.url)]
        logger.info(f"过滤后剩余 {len(filtered_results)} 条有效URL")
        
        # 4. 并行抓取正文
        logger.info(f"\n=== 阶段 3: 并行抓取 (线程数: {self.max_workers}) ===")
        
        articles = []
        url_list = [(r.url, r.keyword) for r in filtered_results]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.crawler.fetch_article, url, kw): url 
                for url, kw in url_list
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    article = future.result()
                    if article:
                        articles.append(article)
                        self.stats["articles_crawled"] += 1
                        logger.info(f"✅ 抓取成功: {article.title[:40]}...")
                    else:
                        logger.debug(f"❌ 抓取失败: {url}")
                except Exception as e:
                    logger.error(f"❌ 异常: {url} - {e}")
        
        logger.info(f"抓取完成，成功 {len(articles)} 篇")
        
        # 5. 保存结果
        logger.info("\n=== 阶段 4: 保存结果 ===")
        self._save_results(articles)
        
        self.stats["end_time"] = datetime.now()
        self._save_stats()
        
        logger.info("\n" + "=" * 60)
        logger.info("采集完成!")
        logger.info(f"耗时: {self.stats['end_time'] - self.stats['start_time']}")
        logger.info(f"关键词: {self.stats['keywords_searched']}")
        logger.info(f"URL: {self.stats['urls_found']} -> {self.stats['articles_crawled']}")
        logger.info("=" * 60)
        
        return articles
    
    def _save_results(self, articles: List[NewsArticle]):
        """保存采集结果"""
        # 保存为 JSONL
        jsonl_path = self.output_dir / "collected_articles.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for article in articles:
                f.write(json.dumps(asdict(article), ensure_ascii=False) + '\n')
        logger.info(f"已保存 JSONL: {jsonl_path}")
        
        # 保存为 CSV
        import pandas as pd
        csv_path = self.output_dir / "collected_articles.csv"
        df = pd.DataFrame([{
            'url': a.url,
            'title': a.title,
            'content': a.content[:500] + '...' if len(a.content) > 500 else a.content,
            'publish_time': a.publish_time,
            'keyword': a.keyword,
            'crawl_time': a.crawl_time
        } for a in articles])
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"已保存 CSV: {csv_path}")
    
    def _save_stats(self):
        """保存统计信息"""
        stats_path = self.output_dir / "collection_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存统计: {stats_path}")


# ============================================================================
# 7. 主入口
# ============================================================================

def main():
    """主函数 - 测试采集流程"""
    
    print("=" * 60)
    print("ICKG 知识图谱数据采集系统 - Bing 搜索模块")
    print("=" * 60)
    
    # 配置参数
    industry = "半导体"
    
    # 示例公司列表
    companies = [
        "中芯国际", "华虹半导体", "北方华创", "中微公司",
        "韦尔股份", "兆易创新", "卓胜微", "士兰微"
    ]
    
    # 示例产品列表
    products = [
        "芯片", "晶圆", "光刻胶", "硅片",
        "IGBT", "MCU", "AI芯片", "第三代半导体"
    ]
    
    # 创建采集器
    collector = ICKGCollector(
        output_dir="data/collected",
        max_workers=10
    )
    
    # 执行采集
    articles = collector.run(
        companies=companies,
        products=products,
        industry=industry
    )
    
    print(f"\n采集完成，共获取 {len(articles)} 篇文章")


if __name__ == "__main__":
    main()
