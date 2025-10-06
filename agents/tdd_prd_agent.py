# -*- coding: utf-8 -*-
"""
TDD PRD Agent - 測試驅動開發 PRD 生成器
當品質是第一優先時使用，適合技術產品、API、對品質要求極高的場景
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

class TDDPRDAgent:
    """TDD 模式 PRD 生成器"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化 TDD PRD Agent

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

        # 創建 TDD PRD Agent
        self.agent = LlmAgent(
            model=self.model,
            name="TDD_PRD_Agent",
            description="測試驅動開發的 PRD 生成專家，專注於品質優先的技術規格",
            instruction=self._get_instruction()
        )

    def _get_instruction(self) -> str:
        """獲取 TDD 模式的指令"""
        return """您好，我是 TDD（測試驅動開發）模式的 PRD 生成專家！

【TDD 模式特色】
當品質是第一優先時，我會為您生成測試驅動的 PRD，特別適合：
- 技術產品和 API 開發
- 對穩定性要求極高的系統
- 需要持續整合和部署的項目
- 開發者工具和平台

【TDD PRD 結構】

## 1. 測試情境設計
### 1.1 Happy Path 測試案例
- 正常流程的端到端測試場景
- 用戶預期操作的測試步驟
- 成功完成任務的驗證點

### 1.2 Edge Cases 列表
- 邊界值測試場景
- 異常輸入處理
- 極限情況下的系統行為

### 1.3 錯誤處理場景
- 各種失敗情況的測試
- 錯誤訊息的準確性
- 系統恢復機制驗證

### 1.4 效能測試標準
- 回應時間要求
- 併發處理能力
- 資源使用限制

## 2. 預期行為定義
### 2.1 Given-When-Then 格式
- 前置條件（Given）
- 操作行為（When）
- 預期結果（Then）

### 2.2 測試資料集規格
- 測試資料的結構定義
- 資料生成規則
- 資料清理策略

### 2.3 Mock 資料定義
- 外部依賴的模擬
- 假資料的生成規則
- 測試環境配置

### 2.4 API 合約測試
- 介面規格驗證
- 資料格式檢查
- 版本相容性測試

## 3. 技術實現規格
### 3.1 系統架構要求
- 模組化設計原則
- 依賴注入策略
- 可測試性設計

### 3.2 程式碼品質標準
- 程式碼覆蓋率要求（≥ 90%）
- 程式碼複雜度限制
- 程式碼審查標準

### 3.3 持續整合流程
- 自動化測試管道
- 部署前驗證流程
- 回滾策略

## 4. 驗收標準
### 4.1 功能驗收
- 所有功能測試通過率 100%
- 回歸測試通過率 100%
- 使用者驗收測試通過

### 4.2 效能驗收
- 回應時間 < 指定閾值
- 併發使用者數達標
- 系統穩定性指標

### 4.3 品質驗收
- 程式碼覆蓋率 ≥ 90%
- 安全性測試通過
- 可維護性評分達標

【生成原則】
1. 測試先行：所有功能都從測試案例開始定義
2. 具體明確：每個測試都有清晰的驗收標準
3. 可自動化：所有測試都能自動執行
4. 可重複：測試結果具有一致性
5. 快速反饋：測試能快速發現問題

【輸出格式】
我會根據您提供的需求，生成結構化的 TDD 模式 PRD，包含詳細的測試規格、技術實現要求和品質標準。"""

    async def generate_prd(self, requirements: Dict[str, Any]) -> str:
        """
        根據需求生成 TDD 模式的 PRD

        Args:
            requirements: 收集到的需求字典

        Returns:
            生成的 PRD 內容
        """
        try:
            # 構建需求上下文
            context = self._build_requirements_context(requirements)

            # 創建對話內容
            content = types.Content(
                role='user',
                parts=[types.Part(text=f"""請根據以下收集到的需求，生成 TDD 模式的 PRD：

{context}

請生成完整的 TDD 模式 PRD，包含：
1. 詳細的測試情境設計（Happy Path、Edge Cases、錯誤處理、效能測試）
2. 結構化的預期行為定義（Given-When-Then、測試資料、Mock 定義）
3. 技術實現規格（系統架構、程式碼品質、CI/CD）
4. 明確的驗收標準（功能、效能、品質）

請確保 PRD 具備高度的可測試性和技術可行性。"""
                )]
            )

            # 設置運行配置
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)

            # 創建 session service 和 runner
            session_service = InMemorySessionService()
            runner = Runner(
                agent=self.agent,
                app_name='tdd_prd_generation',
                session_service=session_service
            )

            # 創建會話
            session = await session_service.create_session(
                app_name='tdd_prd_generation',
                user_id='tdd_user',
                session_id=None
            )

            # 獲取回應
            response_text = ""
            async for event in runner.run_async(
                user_id='tdd_user',
                session_id=session.id,
                new_message=content,
                run_config=run_config
            ):
                if event.content and event.content.parts and event.content.parts[0].text:
                    if not event.partial:
                        response_text = event.content.parts[0].text
                        break

            return response_text

        except Exception as e:
            logger.error(f"TDD PRD 生成時發生錯誤: {str(e)}")
            return f"TDD PRD 生成失敗: {str(e)}"

    def _build_requirements_context(self, requirements: Dict[str, Any]) -> str:
        """構建需求上下文"""
        context = "收集到的需求信息：\n\n"

        # 核心問題
        if 'stage_0' in requirements:
            context += "【核心問題】\n"
            stage_0 = requirements['stage_0']
            context += f"問題描述：{stage_0.get('problem_description', '未定義')}\n"
            context += f"痛點程度：{stage_0.get('pain_level', '未定義')}/10\n"
            context += f"不解決的後果：{stage_0.get('consequences', '未定義')}\n\n"

        # 用戶輪廓
        if 'stage_1' in requirements:
            context += "【用戶輪廓】\n"
            stage_1 = requirements['stage_1']
            context += f"目標用戶：{stage_1.get('target_users', '未定義')}\n"
            context += f"現有解決方案：{stage_1.get('current_solution', '未定義')}\n"
            context += f"付費意願：{stage_1.get('willingness_to_pay', '未定義')}\n\n"

        # 成功定義
        if 'stage_2' in requirements:
            context += "【成功定義】\n"
            stage_2 = requirements['stage_2']
            context += f"成功標準：{stage_2.get('success_criteria', '未定義')}\n"
            context += f"量化指標：{stage_2.get('measurable_metrics', '未定義')}\n"
            context += f"MVP 功能：{stage_2.get('mvp_features', '未定義')}\n\n"

        return context

    def get_template_structure(self) -> Dict[str, Any]:
        """獲取 TDD PRD 模板結構"""
        return {
            "title": "產品需求文檔 (PRD) - TDD 模式",
            "sections": {
                "1_overview": {
                    "title": "1. 產品概述",
                    "subsections": [
                        "1.1 問題陳述",
                        "1.2 目標用戶",
                        "1.3 成功指標",
                        "1.4 技術要求"
                    ]
                },
                "2_test_scenarios": {
                    "title": "2. 測試情境設計",
                    "subsections": [
                        "2.1 Happy Path 測試案例",
                        "2.2 Edge Cases 列表",
                        "2.3 錯誤處理場景",
                        "2.4 效能測試標準"
                    ]
                },
                "3_expected_behavior": {
                    "title": "3. 預期行為定義",
                    "subsections": [
                        "3.1 Given-When-Then 格式",
                        "3.2 測試資料集規格",
                        "3.3 Mock 資料定義",
                        "3.4 API 合約測試"
                    ]
                },
                "4_technical_specs": {
                    "title": "4. 技術實現規格",
                    "subsections": [
                        "4.1 系統架構要求",
                        "4.2 程式碼品質標準",
                        "4.3 持續整合流程"
                    ]
                },
                "5_acceptance_criteria": {
                    "title": "5. 驗收標準",
                    "subsections": [
                        "5.1 功能驗收",
                        "5.2 效能驗收",
                        "5.3 品質驗收"
                    ]
                },
                "6_implementation_plan": {
                    "title": "6. 實施計劃",
                    "subsections": [
                        "6.1 開發里程碑",
                        "6.2 測試階段",
                        "6.3 風險管理"
                    ]
                }
            }
        }

    def validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        驗證需求是否適合 TDD 模式

        Args:
            requirements: 需求字典

        Returns:
            驗證結果和建議
        """
        validation_result = {
            "is_suitable": True,
            "score": 0,
            "reasons": [],
            "suggestions": []
        }

        try:
            # 分析需求文本
            all_text = ""
            for stage_data in requirements.values():
                if isinstance(stage_data, dict):
                    all_text += " ".join(str(v) for v in stage_data.values())

            all_text = all_text.lower()

            # TDD 適合性指標
            technical_indicators = [
                'api', 'sdk', '開發者', '技術', '系統', '架構',
                '效能', '安全', '穩定', '品質', '測試'
            ]

            complexity_indicators = [
                '複雜', '高併發', '大量', '分散式', '微服務',
                '高可用', '容錯', '可擴展'
            ]

            # 計算適合性分數
            technical_score = sum(1 for indicator in technical_indicators if indicator in all_text)
            complexity_score = sum(1 for indicator in complexity_indicators if indicator in all_text)

            validation_result["score"] = technical_score + complexity_score

            # 判斷是否適合
            if validation_result["score"] >= 3:
                validation_result["reasons"].append("需求具有明顯的技術特徵，適合 TDD 開發")
                if complexity_score >= 2:
                    validation_result["reasons"].append("系統複雜度高，TDD 能確保品質")
            else:
                validation_result["is_suitable"] = False
                validation_result["reasons"].append("需求偏向業務和用戶體驗，建議考慮 BDD 模式")

            # 提供建議
            if validation_result["is_suitable"]:
                validation_result["suggestions"] = [
                    "重點關注 API 設計和測試覆蓋率",
                    "建立完整的自動化測試流程",
                    "制定明確的效能和品質標準",
                    "考慮持續整合和部署策略"
                ]
            else:
                validation_result["suggestions"] = [
                    "考慮使用 BDD 模式來更好地描述用戶行為",
                    "如果確實需要 TDD，建議增加技術細節需求",
                    "可以結合 BDD 和 TDD 的優點"
                ]

        except Exception as e:
            logger.error(f"驗證需求時發生錯誤: {str(e)}")
            validation_result["is_suitable"] = False
            validation_result["reasons"] = [f"驗證過程發生錯誤: {str(e)}"]

        return validation_result