# -*- coding: utf-8 -*-
"""
Multi-Version PRD Generator - 多版本 PRD 生成器
根據初版 PRD 生成三個版本：MVP版、標準版、理想版
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

class MultiVersionGenerator:
    """多版本 PRD 生成器"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化多版本 PRD 生成器

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

        # 創建多版本生成 Agent
        self.agent = LlmAgent(
            model=self.model,
            name="MultiVersionGenerator",
            description="根據初版 PRD 生成三個版本（MVP、標準版、理想版）的專家",
            instruction=self._get_instruction()
        )

    def _get_instruction(self) -> str:
        """獲取多版本生成的指令"""
        return """您好，我是多版本 PRD 生成專家！

【核心職責】
根據初版 PRD，我會為您生成三個不同規模的版本：

1. **MVP 版（7天內要上線）**
   - 只保留核心功能
   - 可以用現成工具組合
   - 允許手動操作的部分
   - 目標：快速驗證市場需求

2. **標準版（1個月開發期）**
   - 包含主要功能
   - 良好的使用者體驗
   - 基本的自動化
   - 目標：完整的產品體驗

3. **理想版（不限時間預算）**
   - 完整功能
   - 極致的用戶體驗
   - 全面自動化與智能化
   - 目標：行業領先的解決方案

【生成原則】

**MVP 版特點**：
- 功能範圍：僅保留核心功能（20-30%）
- 技術選型：使用現成工具和服務（Firebase、Supabase、Vercel 等）
- 開發方式：允許手動操作、簡化流程
- 開發成本：低（< 10萬台幣）
- 技術難度：簡單
- 開發時間：7天
- 預期效益：快速驗證需求、獲取早期用戶反饋
- 風險等級：低

**標準版特點**：
- 功能範圍：包含主要功能（60-70%）
- 技術選型：成熟的技術棧
- 開發方式：良好的用戶體驗、基本自動化
- 開發成本：中（10-50萬台幣）
- 技術難度：中等
- 開發時間：1個月
- 預期效益：商業化就緒、穩定運營
- 風險等級：中

**理想版特點**：
- 功能範圍：完整功能（100%）
- 技術選型：最佳技術方案
- 開發方式：極致體驗、全面自動化和智能化
- 開發成本：高（> 50萬台幣）
- 技術難度：複雜
- 開發時間：不限
- 預期效益：行業領先、極致用戶體驗
- 風險等級：高

【輸出格式】

請為每個版本生成完整的 PRD，並在最後提供版本比較表格。

**每個版本 PRD 結構**：
```markdown
# [版本名稱] PRD

## 1. 版本定位
[說明這個版本的核心目標和定位]

## 2. 功能清單
### 核心功能
- [功能1]
- [功能2]
...

### 排除功能
- [不包含的功能1]
- [不包含的功能2]
...

## 3. 技術方案
[具體的技術選型和實現方式]

## 4. 開發計劃
[時程規劃和里程碑]

## 5. 風險與限制
[可能的風險和限制]
```

**比較表格格式**：
| 比較項目 | MVP版 | 標準版 | 理想版 |
|---------|-------|--------|--------|
| 功能範圍 | [簡要描述] | [簡要描述] | [簡要描述] |
| 開發成本 | 低（< 10萬） | 中（10-50萬） | 高（> 50萬） |
| 技術難度 | 簡單 | 中等 | 複雜 |
| 開發時間 | 7天 | 1個月 | 不限 |
| 預期效益 | [描述] | [描述] | [描述] |
| 風險等級 | 低 | 中 | 高 |

請用繁體中文生成所有內容。"""

    async def generate_versions(self, initial_prd: str) -> Dict[str, Any]:
        """
        根據初版 PRD 生成三個版本

        Args:
            initial_prd: 初版 PRD 內容

        Returns:
            包含三個版本和比較表格的字典
        """
        try:
            # 創建對話內容
            content = types.Content(
                role='user',
                parts=[types.Part(text=f"""基於以下初版 PRD，請生成三個版本的 PRD：

## 初版 PRD
{initial_prd}

---

請生成：
1. MVP 版（7天內要上線）
2. 標準版（1個月開發期）
3. 理想版（不限時間預算）

並在最後提供版本比較表格，包含：
- 功能範圍
- 開發成本
- 技術難度
- 開發時間
- 預期效益
- 風險等級

請確保每個版本都是完整的 PRD，並且版本之間有明確的差異化。
請用繁體中文生成所有內容。"""
                )]
            )

            # 設置運行配置
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)

            # 創建 session service 和 runner
            session_service = InMemorySessionService()
            runner = Runner(
                agent=self.agent,
                app_name='multi_version_generation',
                session_service=session_service
            )

            # 創建會話
            session = await session_service.create_session(
                app_name='multi_version_generation',
                user_id='version_user',
                session_id=None
            )

            # 獲取回應
            response_text = ""
            async for event in runner.run_async(
                user_id='version_user',
                session_id=session.id,
                new_message=content,
                run_config=run_config
            ):
                if event.content and event.content.parts and event.content.parts[0].text:
                    if not event.partial:
                        response_text = event.content.parts[0].text
                        break

            # 解析回應，提取三個版本
            # 簡單的解析策略：假設 AI 會用標題分隔三個版本
            versions = self._parse_versions(response_text)

            return versions

        except Exception as e:
            logger.error(f"生成多版本 PRD 時發生錯誤: {str(e)}")
            return {
                "mvp": f"# MVP版 PRD\n\n生成失敗: {str(e)}",
                "standard": f"# 標準版 PRD\n\n生成失敗: {str(e)}",
                "ideal": f"# 理想版 PRD\n\n生成失敗: {str(e)}",
                "comparison": None
            }

    def _parse_versions(self, response_text: str) -> Dict[str, Any]:
        """
        解析 AI 回應，提取三個版本的 PRD

        Args:
            response_text: AI 生成的完整回應

        Returns:
            包含三個版本和比較數據的字典
        """
        result = {
            "mvp": "",
            "standard": "",
            "ideal": "",
            "comparison": None
        }

        # 簡單的解析策略：按照標題分割
        # 這裡使用基本的字符串分割，實際可以更智能
        sections = response_text.split("# ")

        mvp_found = False
        standard_found = False
        ideal_found = False

        current_section = ""
        for section in sections:
            if section.strip():
                # 判斷是哪個版本
                if "MVP" in section[:50] or "mvp" in section[:50].lower():
                    mvp_found = True
                    standard_found = False
                    ideal_found = False
                    result["mvp"] = "# " + section.strip()
                elif "標準版" in section[:50] or "standard" in section[:50].lower():
                    mvp_found = False
                    standard_found = True
                    ideal_found = False
                    result["standard"] = "# " + section.strip()
                elif "理想版" in section[:50] or "ideal" in section[:50].lower():
                    mvp_found = False
                    standard_found = False
                    ideal_found = True
                    result["ideal"] = "# " + section.strip()
                elif mvp_found:
                    result["mvp"] += "\n# " + section.strip()
                elif standard_found:
                    result["standard"] += "\n# " + section.strip()
                elif ideal_found:
                    result["ideal"] += "\n# " + section.strip()

        # 如果解析失敗，返回完整文本
        if not result["mvp"] and not result["standard"] and not result["ideal"]:
            # 嘗試更簡單的分割方式
            parts = response_text.split("\n\n")
            if len(parts) >= 3:
                result["mvp"] = "\n\n".join(parts[:len(parts)//3])
                result["standard"] = "\n\n".join(parts[len(parts)//3:2*len(parts)//3])
                result["ideal"] = "\n\n".join(parts[2*len(parts)//3:])
            else:
                # 最後的備用方案：全部返回相同內容
                result["mvp"] = response_text
                result["standard"] = response_text
                result["ideal"] = response_text

        # 嘗試提取比較表格（如果存在）
        if "|" in response_text and "比較項目" in response_text:
            # 找到表格部分
            table_start = response_text.find("| 比較項目")
            if table_start == -1:
                table_start = response_text.find("|比較項目")
            if table_start != -1:
                table_end = response_text.find("\n\n", table_start)
                if table_end == -1:
                    table_end = len(response_text)
                result["comparison"] = response_text[table_start:table_end].strip()

        return result
