# ICKG 知识图谱采集系统 - LLM 客户端
# v5.0

"""
LLM 客户端模块

支持火山引擎 Doubao-Seed-1.6-lite 模型，支持联网搜索。
"""

import json
import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM 配置"""
    api_key: str = ""
    endpoint_id: str = "ep-20260129125122-87vdp"  # Doubao-Seed-1.6-lite
    api_endpoint: str = "https://ark.cn-beijing.volces.com/api/v3"
    max_retries: int = 3
    timeout: float = 120.0


class LLMClient:
    """LLM API 客户端"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.Client(timeout=httpx.Timeout(config.timeout))
        self.total_tokens = 0
        self.total_cost = 0.0
        self.api_calls = 0
    
    def close(self):
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def chat(
        self,
        messages: list,
        max_tokens: int = 65535,
        use_web_search: bool = False,
        temperature: float = 0.1
    ) -> Optional[str]:
        """发送对话请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            max_tokens: 最大输出 tokens
            use_web_search: 是否使用联网搜索
            temperature: 温度参数
            
        Returns:
            响应文本，失败返回 None
        """
        if not self.config.api_key:
            logger.error("API key 未配置")
            return None
        
        for retry in range(self.config.max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
                
                request_body = {
                    "model": self.config.endpoint_id,
                    "max_completion_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False,
                    "reasoning_effort": "medium",
                    "messages": messages
                }
                
                # 联网搜索
                if use_web_search:
                    request_body["tools"] = [{
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "description": "搜索互联网获取最新信息",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "搜索查询关键词"}
                                },
                                "required": ["query"]
                            }
                        }
                    }]
                
                response = self.client.post(
                    self.config.api_endpoint + "/chat/completions",
                    headers=headers,
                    json=request_body,
                    timeout=120.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 处理工具调用
                    output_text = self._handle_tool_response(result)
                    if output_text:
                        self._update_stats(messages, output_text)
                        return output_text
                        
                else:
                    logger.warning(f"API 错误: {response.status_code} - {response.text[:200]}")
                    if retry < self.config.max_retries - 1:
                        time.sleep(2 ** (retry + 1))
                        
            except Exception as e:
                logger.warning(f"请求异常: {e}")
                if retry < self.config.max_retries - 1:
                    time.sleep(2 ** (retry + 1))
        
        return None
    
    def _handle_tool_response(self, result: dict) -> Optional[str]:
        """处理工具调用响应"""
        try:
            if "choices" not in result or len(result["choices"]) == 0:
                return ""
            
            choice = result["choices"][0]
            
            # 情况1: message 是字典
            if "message" in choice:
                message = choice["message"]
                if isinstance(message, dict):
                    # 检查是否有工具调用
                    if "tool_calls" in message and message["tool_calls"]:
                        return self._execute_tool_calls(message["tool_calls"], result)
                    
                    # 直接返回 content
                    content = message.get("content", "")
                    if isinstance(content, str):
                        return content.strip()
            
            # 情况2: 直接返回 choices[0] 的内容
            content = choice.get("content", "")
            if isinstance(content, str):
                return content.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"处理响应失败: {e}")
            return ""
    
    def _execute_tool_calls(self, tool_calls: list, original_result: dict) -> str:
        """执行工具调用"""
        for tool_call in tool_calls:
            tool_call_id = tool_call.get("id", "")
            function = tool_call.get("function", {})
            function_name = function.get("name", "")
            arguments = function.get("arguments", "")
            
            logger.info(f"执行工具: {function_name}")
            
            # 执行搜索
            if function_name == "web_search":
                try:
                    import json as json_module
                    args = json_module.loads(arguments) if arguments else {}
                    query = args.get("query", str(args))
                    search_result = self._web_search(query)
                    
                    # 构建工具响应消息
                    tool_messages = [{
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": function_name,
                        "content": search_result
                    }]
                    
                    # 再次请求获取最终结果
                    final_result = self._continue_conversation(
                        original_result["choices"][0]["message"],
                        tool_messages
                    )
                    
                    if final_result:
                        return final_result
                        
                except Exception as e:
                    logger.error(f"工具执行失败: {e}")
        
        return ""
    
    def _continue_conversation(self, message: dict, tool_messages: list) -> Optional[str]:
        """继续对话"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            request_body = {
                "model": self.config.endpoint_id,
                "max_completion_tokens": 16000,
                "stream": False,
                "messages": [message] + tool_messages
            }
            
            response = self.client.post(
                self.config.api_endpoint + "/chat/completions",
                headers=headers,
                json=request_body,
                timeout=120.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._handle_tool_response(result)
        except Exception as e:
            logger.error(f"继续对话失败: {e}")
        
        return None
    
    def _web_search(self, query: str) -> str:
        """执行联网搜索"""
        try:
            search_response = self.client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1
                },
                timeout=30.0
            )
            
            if search_response.status_code == 200:
                data = search_response.json()
                return self._format_search_results(data, query)
            else:
                return f"搜索失败: HTTP {search_response.status_code}"
        except Exception as e:
            return f"搜索异常: {str(e)}"
    
    def _format_search_results(self, data: dict, query: str) -> str:
        """格式化搜索结果"""
        lines = [f"关于 {query} 的搜索结果："]
        
        if data.get("Abstract"):
            lines.append(f"摘要: {data['Abstract']}")
            if data.get("AbstractURL"):
                lines.append(f"来源: {data['AbstractURL']}")
            return "\n".join(lines)
        
        for item in data.get("RelatedTopics", [])[:5]:
            if isinstance(item, dict) and item.get("Text"):
                lines.append(f"- {item['Text']}")
                if item.get("FirstURL"):
                    lines.append(f"  来源: {item['FirstURL']}")
        
        if len(lines) == 1:
            lines.append("未找到相关信息。")
        
        return "\n".join(lines)
    
    def _update_stats(self, messages: list, response: str):
        """更新统计信息"""
        self.api_calls += 1
        input_tokens = sum(len(str(m.get("content", ""))) for m in messages) // 4
        output_tokens = len(response) // 4
        self.total_tokens += input_tokens + output_tokens
        self.total_cost += output_tokens * 16 / 1000000
    
    def __del__(self):
        self.close()
