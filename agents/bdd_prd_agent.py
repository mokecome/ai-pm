# -*- coding: utf-8 -*-
"""
BDD PRD Agent - 行為驅動開發 PRD 生成器
當要跟非技術人員溝通時使用，適合用戶產品、B2C 應用、跨部門協作
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class BDDPRDAgent:
    """BDD 模式 PRD 生成器"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化 BDD PRD Agent

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

        # 創建 BDD PRD Agent
        self.agent = LlmAgent(
            model=self.model,
            name="BDD_PRD_Agent",
            description="行為驅動開發的 PRD 生成專家，專注於用戶行為和業務價值",
            instruction=self._get_instruction()
        )

    def _get_instruction(self) -> str:
        """獲取 BDD 模式的指令"""
        return """您好，我是 BDD（行為驅動開發）模式的 PRD 生成專家！

【BDD 模式特色】
當需要跟非技術人員溝通時，我會為您生成行為驅動的 PRD，特別適合：
- 用戶導向的產品開發
- B2C 應用和消費性產品
- 需要跨部門協作的項目
- 重視用戶體驗的系統

【BDD PRD 結構】

## 1. 使用者故事場景
### 1.1 核心用戶故事
Feature: [功能名稱]
  As a [用戶角色]
  I want [期望功能]
  So that [業務價值]

### 1.2 場景描述
Scenario: [場景名稱]
  Given [前置條件]
  When [用戶操作]
  Then [預期結果]
  And [額外驗證]

### 1.3 用戶流程圖
- 主要使用流程
- 替代流程
- 異常處理流程

### 1.4 使用者體驗要求
- 介面設計原則
- 操作便利性
- 無障礙設計

## 2. 業務價值說明
### 2.1 為什麼用戶需要這個功能
- 解決的核心痛點
- 提供的價值主張
- 滿足的業務需求

### 2.2 商業價值量化
- 預期的業務指標提升
- ROI 投資回報率分析
- 市場機會評估

### 2.3 成功的用戶行為定義
- 關鍵操作指標
- 用戶參與度指標
- 滿意度指標

### 2.4 競爭優勢分析
- 與競品的差異化
- 獨特價值提案
- 市場定位策略

## 3. 用戶體驗設計
### 3.1 用戶介面要求
- 界面佈局原則
- 視覺設計規範
- 互動設計標準

### 3.2 用戶操作流程
- 操作步驟簡化
- 錯誤防範機制
- 幫助和引導設計

### 3.3 回饋機制設計
- 操作回饋方式
- 進度指示設計
- 錯誤訊息處理

## 4. 跨部門協作要求
### 4.1 產品團隊職責
- 產品經理職責
- UI/UX 設計師職責
- 使用者研究職責

### 4.2 技術團隊職責
- 前端開發職責
- 後端開發職責
- 測試團隊職責

### 4.3 營運團隊職責
- 客服支援準備
- 營運流程調整
- 數據分析設置

## 5. 驗收標準
### 5.1 用戶滿意度指標
- Net Promoter Score (NPS)
- 用戶滿意度調查
- 用戶留存率

### 5.2 業務指標達成
- 轉換率提升
- 使用頻率增加
- 收益指標改善

### 5.3 跨部門確認清單
- 產品功能確認
- 設計稿最終確認
- 技術實現確認
- 營運流程確認

【生成原則】
1. 用戶中心：所有功能都從用戶角度出發
2. 業務驅動：明確每個功能的業務價值
3. 溝通友善：使用非技術人員能理解的語言
4. 協作導向：考慮各部門的協作需求
5. 可驗證：設定明確的成功指標

【輸出格式】
我會根據您提供的需求，生成結構化的 BDD 模式 PRD，包含豐富的用戶故事、業務價值說明和跨部門協作指南。"""

    async def generate_prd(self, requirements: Dict[str, Any]) -> str:
        """
        根據需求生成 BDD 模式的 PRD

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
                parts=[types.Part(text=f"""請根據以下收集到的需求，生成 BDD 模式的 PRD：

{context}

請生成完整的 BDD 模式 PRD，包含：
1. 詳細的使用者故事場景（Feature、Scenario、用戶流程、UX 要求）
2. 明確的業務價值說明（痛點解決、商業價值、成功定義、競爭優勢）
3. 用戶體驗設計要求（UI 要求、操作流程、回饋機制）
4. 跨部門協作指南（各團隊職責分工）
5. 清晰的驗收標準（滿意度、業務指標、確認清單）

請確保 PRD 使用非技術人員也能理解的語言，並著重說明業務價值和用戶體驗。"""
                )]
            )

            # 設置運行配置
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)

            # 創建 session service 和 runner
            session_service = InMemorySessionService()
            runner = Runner(
                agent=self.agent,
                app_name='bdd_prd_generation',
                session_service=session_service
            )

            # 創建會話
            session = await session_service.create_session(
                app_name='bdd_prd_generation',
                user_id='bdd_user',
                session_id=None
            )

            # 獲取回應
            response_text = ""
            async for event in runner.run_async(
                user_id='bdd_user',
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
            logger.error(f"BDD PRD 生成時發生錯誤: {str(e)}")
            return f"BDD PRD 生成失敗: {str(e)}"

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
        """獲取 BDD PRD 模板結構"""
        return {
            "title": "產品需求文檔 (PRD) - BDD 模式",
            "sections": {
                "1_overview": {
                    "title": "1. 產品概述",
                    "subsections": [
                        "1.1 產品願景",
                        "1.2 目標用戶",
                        "1.3 核心價值主張",
                        "1.4 成功指標"
                    ]
                },
                "2_user_stories": {
                    "title": "2. 使用者故事場景",
                    "subsections": [
                        "2.1 核心用戶故事",
                        "2.2 場景描述 (Given-When-Then)",
                        "2.3 用戶流程圖",
                        "2.4 使用者體驗要求"
                    ]
                },
                "3_business_value": {
                    "title": "3. 業務價值說明",
                    "subsections": [
                        "3.1 用戶需求分析",
                        "3.2 商業價值量化",
                        "3.3 成功用戶行為",
                        "3.4 競爭優勢分析"
                    ]
                },
                "4_ux_design": {
                    "title": "4. 用戶體驗設計",
                    "subsections": [
                        "4.1 用戶介面要求",
                        "4.2 用戶操作流程",
                        "4.3 回饋機制設計"
                    ]
                },
                "5_collaboration": {
                    "title": "5. 跨部門協作",
                    "subsections": [
                        "5.1 產品團隊職責",
                        "5.2 技術團隊職責",
                        "5.3 營運團隊職責"
                    ]
                },
                "6_acceptance": {
                    "title": "6. 驗收標準",
                    "subsections": [
                        "6.1 用戶滿意度指標",
                        "6.2 業務指標達成",
                        "6.3 跨部門確認清單"
                    ]
                }
            }
        }

    def validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        驗證需求是否適合 BDD 模式

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

            # BDD 適合性指標
            user_indicators = [
                '用戶', '客戶', '使用者', '體驗', '界面', '操作',
                '方便', '簡單', '直觀', '友善', '滿意'
            ]

            business_indicators = [
                '業務', '商業', '營收', '轉換', '銷售', '市場',
                '競爭', '客戶', '服務', '流程', '效率'
            ]

            collaboration_indicators = [
                '團隊', '協作', '溝通', '部門', '配合', '整合',
                '跨部門', '合作', '協調'
            ]

            # 計算適合性分數
            user_score = sum(1 for indicator in user_indicators if indicator in all_text)
            business_score = sum(1 for indicator in business_indicators if indicator in all_text)
            collaboration_score = sum(1 for indicator in collaboration_indicators if indicator in all_text)

            validation_result["score"] = user_score + business_score + collaboration_score

            # 判斷是否適合
            if validation_result["score"] >= 3:
                validation_result["reasons"].append("需求具有明顯的用戶和業務特徵，適合 BDD 開發")
                if user_score >= 2:
                    validation_result["reasons"].append("重視用戶體驗，BDD 能更好地描述用戶行為")
                if business_score >= 2:
                    validation_result["reasons"].append("具有明確的業務價值，適合跨部門協作")
            else:
                validation_result["is_suitable"] = False
                validation_result["reasons"].append("需求偏向技術實現，建議考慮 TDD 模式")

            # 提供建議
            if validation_result["is_suitable"]:
                validation_result["suggestions"] = [
                    "重點關注用戶故事的詳細描述",
                    "明確定義各部門的協作方式",
                    "設定用戶滿意度和業務指標",
                    "考慮用戶體驗的持續優化"
                ]
            else:
                validation_result["suggestions"] = [
                    "如果涉及複雜技術實現，考慮使用 TDD 模式",
                    "如果確實需要 BDD，建議增加用戶體驗相關需求",
                    "可以結合 TDD 和 BDD 的優點"
                ]

        except Exception as e:
            logger.error(f"驗證需求時發生錯誤: {str(e)}")
            validation_result["is_suitable"] = False
            validation_result["reasons"] = [f"驗證過程發生錯誤: {str(e)}"]

        return validation_result

    def generate_user_stories(self, requirements: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        根據需求生成用戶故事

        Args:
            requirements: 需求字典

        Returns:
            用戶故事列表
        """
        user_stories = []

        try:
            # 從需求中提取核心功能
            mvp_features = ""
            if 'stage_2' in requirements:
                mvp_features = requirements['stage_2'].get('mvp_features', '')

            target_users = ""
            if 'stage_1' in requirements:
                target_users = requirements['stage_1'].get('target_users', '')

            problem_description = ""
            if 'stage_0' in requirements:
                problem_description = requirements['stage_0'].get('problem_description', '')

            # 生成基礎用戶故事
            if mvp_features and target_users:
                user_stories.append({
                    "feature": "核心功能",
                    "as_a": target_users,
                    "i_want": mvp_features,
                    "so_that": f"能夠解決 {problem_description} 的問題"
                })

            # 可以根據需要添加更多用戶故事...

        except Exception as e:
            logger.error(f"生成用戶故事時發生錯誤: {str(e)}")

        return user_stories