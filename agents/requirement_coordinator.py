# -*- coding: utf-8 -*-
"""
需求收集協調器 Agent
負責透過結構化問答收集用戶需求，並撰寫適合的開發模式
"""

import os
import asyncio
from typing import Dict, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class RequirementCoordinator:
    """需求收集協調器 - 純 Agent 模式"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化需求收集協調器

        Args:
            api_key: OpenAI API Key（可選）
            api_base: API 基礎 URL（可選）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        # 配置模型
        self.model = LiteLlm(
            model="gpt-4o",
            api_base=self.api_base,
            api_key=self.api_key
        )

        # 創建需求收集 Agent
        self.agent = LlmAgent(
            model=self.model,
            name="RequirementCoordinator",
            description="專業產品經理，透過結構化問答收集產品需求並撰寫PRD",
            instruction=self._get_instruction()
        )

        # Session 相關（持久化）
        self.session_service = None
        self.runner = None
        self.session = None
        self.is_initialized = False

    def _get_instruction(self) -> str:
        """獲取 Agent 指令 - 所有流程邏輯都在這裡"""
        return """您好，我是 AI-PM 的專業產品經理！

【核心職責】
我是智能需求收集器，負責：
- 🎯 透過結構化問答收集產品需求


【工作流程】

**第一階段：需求收集**

必須完成以下問題：
✓ 你想解決什麼問題？請詳細描述用戶遇到的具體痛點。
✓ 這個痛點有多痛？請用 1-10 分評分（1分是輕微不便，10分是極度痛苦），並說明理由。
✓ 如果不解決這個問題會造成什麼後果？對用戶或業務會有什麼影響？
✓ 誰會使用這個產品？請描述目標用戶的特徵（年齡、職業、行為習慣等）。
✓ 他們現在是如何解決這個問題的？使用什麼工具或方法？
✓ 他們願意為解決這個問題付多少錢？或者投入多少時間成本？
✓ 怎樣才算成功？請定義成功的具體標準和表現。
✓ 有什麼可以量化的指標嗎？比如使用率、滿意度、效率提升等。
✓ 最小可行產品（MVP）需要包含哪些核心功能才能解決基本痛點？

【互動規則】

**完成所有需求收集後：**
- 恭喜完成需求收集
- 總結收集到的關鍵信息（3-5 點）
- 明確告知：「✅ 需求收集完成！請在側邊欄選擇開發模式，然後在初版PRD頁面生成文檔。」



我是您的專業產品需求收集助手！讓我們開始吧。"""

    async def initialize(self):
        """初始化持久化 session（只需調用一次）"""
        if self.is_initialized:
            logger.info("Session 已經初始化，跳過重複初始化")
            return

        try:
            logger.info("正在初始化 RequirementCoordinator session...")

            # 創建 session service
            self.session_service = InMemorySessionService()

            # 創建 runner
            self.runner = Runner(
                agent=self.agent,
                app_name='prd_requirement_collection',
                session_service=self.session_service
            )

            # 創建 session
            self.session = await self.session_service.create_session(
                app_name='prd_requirement_collection',
                user_id='requirement_user',
                session_id=None
            )

            self.is_initialized = True
            logger.info(f"Session 初始化完成，session_id: {self.session.id}")

        except Exception as e:
            logger.error(f"初始化 session 時發生錯誤: {str(e)}")
            raise

    async def send_message(self, user_input: str) -> str:
        """
        發送消息並獲取回應

        Args:
            user_input: 用戶輸入的消息

        Returns:
            str: Agent 的回應
        """
        if not self.is_initialized:
            raise RuntimeError("請先調用 initialize() 方法初始化 session")

        try:
            # 創建對話內容
            content = types.Content(
                role='user',
                parts=[types.Part(text=user_input)]
            )

            # 設置運行配置
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)

            # 獲取回應
            response_text = ""
            async for event in self.runner.run_async(
                user_id='requirement_user',
                session_id=self.session.id,
                new_message=content,
                run_config=run_config
            ):
                if event.content and event.content.parts and event.content.parts[0].text:
                    if not event.partial:
                        response_text = event.content.parts[0].text
                        break

            return response_text

        except Exception as e:
            logger.error(f"發送消息時發生錯誤: {str(e)}")
            return f"處理過程中發生錯誤: {str(e)}"

    async def get_chat_history(self) -> list:
        """獲取當前對話歷史"""
        if not self.is_initialized:
            return []

        try:
            # 從 session 獲取對話歷史
            history = await self.session_service.get_session_history(
                app_name='prd_requirement_collection',
                user_id='requirement_user',
                session_id=self.session.id
            )
            return history
        except Exception as e:
            logger.error(f"獲取對話歷史時發生錯誤: {str(e)}")
            return []

    async def extract_requirements(self, chat_history: list) -> Dict[str, Any]:
        """
        從對話歷史中提取結構化需求數據

        Args:
            chat_history: 對話歷史列表 [{"role": "user/assistant", "content": "..."}]

        Returns:
            結構化的需求字典
        """
        try:
            # 構建完整對話文本
            conversation_text = ""
            for msg in chat_history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                conversation_text += f"{role}: {content}\n\n"

            logger.info("開始從對話歷史中提取結構化需求...")

            # 構建提取提示詞
            extract_prompt = f"""請從以下對話歷史中提取結構化的產品需求信息，並以 JSON 格式返回。

對話歷史：
{conversation_text}

請提取以下信息（如果對話中有提到）：

**Stage 0 - 核心問題：**
- problem_description: 要解決的具體問題
- pain_level: 痛點程度（1-10分）
- consequences: 不解決的後果

**Stage 1 - 用戶輪廓：**
- target_users: 目標用戶描述
- current_solution: 現有解決方案
- willingness_to_pay: 付費意願或時間成本

**Stage 2 - 成功定義：**
- success_criteria: 成功標準
- measurable_metrics: 可量化的指標
- mvp_features: MVP 核心功能

請以以下 JSON 格式返回（如果某個信息未提及，該字段填空字串）：

```json
{{
  "stage_0": {{
    "problem_description": "...",
    "pain_level": "...",
    "consequences": "..."
  }},
  "stage_1": {{
    "target_users": "...",
    "current_solution": "...",
    "willingness_to_pay": "..."
  }},
  "stage_2": {{
    "success_criteria": "...",
    "measurable_metrics": "...",
    "mvp_features": "..."
  }}
}}
```

只返回 JSON，不要其他說明文字。"""

            # 使用模型提取數據
            content = types.Content(
                role='user',
                parts=[types.Part(text=extract_prompt)]
            )

            response = self.model.generate_content(contents=[content])
            response_text = response.text.strip()

            # 解析 JSON
            import re
            import json

            # 嘗試提取 JSON（可能被包在 ```json...``` 中）
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 嘗試直接匹配 JSON 對象
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    json_str = json_match.group()
                else:
                    json_str = response_text

            requirements = json.loads(json_str)
            logger.info("結構化需求提取成功")

            return requirements

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {str(e)}")
            logger.error(f"回應內容: {response_text}")
            # 返回空結構
            return {
                "stage_0": {},
                "stage_1": {},
                "stage_2": {}
            }
        except Exception as e:
            logger.error(f"提取結構化需求時發生錯誤: {str(e)}")
            return {
                "stage_0": {},
                "stage_1": {},
                "stage_2": {}
            }

    def is_requirements_complete(self, requirements: Dict[str, Any]) -> bool:
        """
        檢查需求收集是否完成（至少有4個必填字段）

        必填字段：
        - problem_description
        - target_users
        - measurable_metrics
        - mvp_features

        Args:
            requirements: 結構化需求字典

        Returns:
            True 如果需求足夠完整，False 否則
        """
        try:
            required_fields = [
                ('stage_0', 'problem_description'),
                ('stage_1', 'target_users'),
                ('stage_2', 'measurable_metrics'),
                ('stage_2', 'mvp_features')
            ]

            filled_count = 0
            for stage, field in required_fields:
                value = requirements.get(stage, {}).get(field, "")
                if value and value.strip():
                    filled_count += 1

            logger.info(f"必填字段完成度: {filled_count}/4")
            return filled_count >= 4

        except Exception as e:
            logger.error(f"檢查需求完成度時發生錯誤: {str(e)}")
            return False