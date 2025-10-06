# -*- coding: utf-8 -*-
"""
DDD PRD Agent - 領域驅動設計 PRD 生成器
當系統很複雜時使用，適合企業級應用、多領域整合、複雜業務系統
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

class DDDPRDAgent:
    """DDD 模式 PRD 生成器"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化 DDD PRD Agent

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

        # 創建 DDD PRD Agent
        self.agent = LlmAgent(
            model=self.model,
            name="DDD_PRD_Agent",
            description="領域驅動設計的 PRD 生成專家，專注於複雜業務領域建模",
            instruction=self._get_instruction()
        )

    def _get_instruction(self) -> str:
        """獲取 DDD 模式的指令"""
        return """您好，我是 DDD（領域驅動設計）模式的 PRD 生成專家！

【DDD 模式特色】
當系統很複雜時，我會為您生成領域驅動的 PRD，特別適合：
- 企業級應用和 ERP 系統
- 多領域整合的複雜系統
- 需要長期演進的大型系統
- 涉及複雜業務規則的場景

【DDD PRD 結構】

## 1. 領域模型設計
### 1.1 核心領域概念定義
- 領域專家識別
- 業務核心概念
- 領域知識萃取
- 業務規則定義

### 1.2 Bounded Context 劃分
- 子領域識別和邊界
- 上下文映射
- 領域間關係定義
- 整合模式選擇

### 1.3 聚合根和實體關係
- 聚合設計原則
- 實體生命週期
- 值對象定義
- 領域服務設計

### 1.4 領域事件設計
- 業務事件識別
- 事件驅動架構
- 事件溯源策略
- 事件處理機制

## 2. 領域語言字典
### 2.1 統一建模語言 (UML)
- 業務術語標準化
- 技術術語對照表
- 領域專有名詞定義
- 概念模型圖

### 2.2 業務規則定義
- 不變規則 (Invariants)
- 業務約束條件
- 驗證規則
- 業務流程規範

### 2.3 領域事件清單
- 領域事件分類
- 事件觸發條件
- 事件處理者
- 事件存儲策略

### 2.4 整合定義
- API 契約定義
- 數據交換格式
- 協議標準
- 版本兼容策略

## 3. 系統架構設計
### 3.1 微服務邊界設計
- 服務拆分原則
- 服務間通信
- 數據一致性策略
- 服務治理機制

### 3.2 分層架構設計
- 表現層設計
- 應用層服務
- 領域層實現
- 基礎設施層

### 3.3 數據一致性策略
- 強一致性場景
- 最終一致性設計
- 分散式事務處理
- 補償機制設計

### 3.4 整合模式選擇
- 同步 vs 異步整合
- 事件驅動整合
- RESTful API 設計
- 訊息佇列使用

## 4. 技術實現策略
### 4.1 架構模式選擇
- 六邊形架構
- CQRS 模式應用
- 事件溯源實現
- 微服務架構

### 4.2 持久化策略
- 聚合存儲設計
- 事件存儲機制
- 讀寫分離策略
- 數據庫選型

### 4.3 效能考量
- 查詢優化策略
- 快取設計
- 負載均衡
- 水平擴展設計

## 5. 實施和演進計劃
### 5.1 領域建模工作坊
- 利害關係人識別
- 領域專家訪談
- 建模會議規劃
- 知識萃取方法

### 5.2 開發迭代計劃
- 核心領域優先
- 支撐領域規劃
- 通用領域整合
- 演進策略定義

### 5.3 團隊組織架構
- 領域團隊組成
- 跨領域協作
- 技術決策機制
- 知識分享機制

【生成原則】
1. 領域驅動：以業務領域為核心進行設計
2. 模型導向：建立豐富的領域模型
3. 演進設計：支持長期演進和變化
4. 專家協作：重視領域專家的參與
5. 架構清晰：保持清晰的架構邊界

【輸出格式】
我會根據您提供的需求，生成結構化的 DDD 模式 PRD，包含詳細的領域模型、系統架構設計和實施策略。"""

    async def generate_prd(self, requirements: Dict[str, Any]) -> str:
        """
        根據需求生成 DDD 模式的 PRD

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
                parts=[types.Part(text=f"""請根據以下收集到的需求，生成 DDD 模式的 PRD：

{context}

請生成完整的 DDD 模式 PRD，包含：
1. 詳細的領域模型設計（核心概念、Bounded Context、聚合根、領域事件）
2. 完整的領域語言字典（UML、業務規則、事件清單、整合定義）
3. 系統架構設計（微服務邊界、分層架構、一致性策略、整合模式）
4. 技術實現策略（架構模式、持久化、效能考量）
5. 實施和演進計劃（建模工作坊、迭代計劃、團隊架構）

請確保 PRD 能夠支持複雜業務場景的長期演進和架構清晰度。"""
                )]
            )

            # 設置運行配置
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)

            # 創建 session service 和 runner
            session_service = InMemorySessionService()
            runner = Runner(
                agent=self.agent,
                app_name='ddd_prd_generation',
                session_service=session_service
            )

            # 創建會話
            session = await session_service.create_session(
                app_name='ddd_prd_generation',
                user_id='ddd_user',
                session_id=None
            )

            # 獲取回應
            response_text = ""
            async for event in runner.run_async(
                user_id='ddd_user',
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
            logger.error(f"DDD PRD 生成時發生錯誤: {str(e)}")
            return f"DDD PRD 生成失敗: {str(e)}"

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
        """獲取 DDD PRD 模板結構"""
        return {
            "title": "產品需求文檔 (PRD) - DDD 模式",
            "sections": {
                "1_overview": {
                    "title": "1. 產品概述",
                    "subsections": [
                        "1.1 業務願景",
                        "1.2 問題領域分析",
                        "1.3 核心價值主張",
                        "1.4 戰略目標"
                    ]
                },
                "2_domain_model": {
                    "title": "2. 領域模型設計",
                    "subsections": [
                        "2.1 核心領域概念定義",
                        "2.2 Bounded Context 劃分",
                        "2.3 聚合根和實體關係",
                        "2.4 領域事件設計"
                    ]
                },
                "3_ubiquitous_language": {
                    "title": "3. 領域語言字典",
                    "subsections": [
                        "3.1 統一建模語言 (UML)",
                        "3.2 業務規則定義",
                        "3.3 領域事件清單",
                        "3.4 整合定義"
                    ]
                },
                "4_system_architecture": {
                    "title": "4. 系統架構設計",
                    "subsections": [
                        "4.1 微服務邊界設計",
                        "4.2 分層架構設計",
                        "4.3 數據一致性策略",
                        "4.4 整合模式選擇"
                    ]
                },
                "5_technical_strategy": {
                    "title": "5. 技術實現策略",
                    "subsections": [
                        "5.1 架構模式選擇",
                        "5.2 持久化策略",
                        "5.3 效能考量"
                    ]
                },
                "6_implementation_plan": {
                    "title": "6. 實施和演進計劃",
                    "subsections": [
                        "6.1 領域建模工作坊",
                        "6.2 開發迭代計劃",
                        "6.3 團隊組織架構"
                    ]
                }
            }
        }

    def validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        驗證需求是否適合 DDD 模式

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

            # DDD 適合性指標
            complexity_indicators = [
                '企業', '複雜', '大型', '多部門', '整合', '系統性',
                '長期', '演進', '架構', '規模', '分散式'
            ]

            domain_indicators = [
                '業務', '領域', '規則', '流程', '政策', '法規',
                '專業', '知識', '專家', '建模', '領域'
            ]

            integration_indicators = [
                '整合', '系統', '平台', '介接', '交換', '同步',
                '協作', '互通', '連結', '橋接'
            ]

            # 計算適合性分數
            complexity_score = sum(1 for indicator in complexity_indicators if indicator in all_text)
            domain_score = sum(1 for indicator in domain_indicators if indicator in all_text)
            integration_score = sum(1 for indicator in integration_indicators if indicator in all_text)

            validation_result["score"] = complexity_score + domain_score + integration_score

            # 判斷是否適合
            if validation_result["score"] >= 4:
                validation_result["reasons"].append("需求具有高複雜度和領域特徵，適合 DDD 開發")
                if complexity_score >= 2:
                    validation_result["reasons"].append("系統複雜度高，DDD 能提供清晰的架構")
                if domain_score >= 2:
                    validation_result["reasons"].append("具有豐富的業務領域知識，適合領域建模")
                if integration_score >= 2:
                    validation_result["reasons"].append("涉及複雜整合，DDD 邊界設計能有效管理")
            else:
                validation_result["is_suitable"] = False
                if validation_result["score"] <= 2:
                    validation_result["reasons"].append("需求相對簡單，建議考慮 BDD 或 TDD 模式")
                else:
                    validation_result["reasons"].append("需求具有一定複雜度，但可能不需要完整的 DDD 方法")

            # 提供建議
            if validation_result["is_suitable"]:
                validation_result["suggestions"] = [
                    "組織領域建模工作坊，邀請業務專家參與",
                    "識別核心子領域，優先處理最重要的業務邏輯",
                    "建立統一的領域語言，確保團隊溝通一致",
                    "設計清晰的 Bounded Context，管理複雜度",
                    "考慮事件驅動架構，提高系統的響應性和可擴展性"
                ]
            else:
                validation_result["suggestions"] = [
                    "評估系統的實際複雜度，確認是否需要 DDD",
                    "如果業務邏輯相對簡單，考慮使用 BDD 模式",
                    "如果技術挑戰較大，考慮使用 TDD 模式",
                    "可以採用簡化的領域建模方法，不必使用完整 DDD"
                ]

        except Exception as e:
            logger.error(f"驗證需求時發生錯誤: {str(e)}")
            validation_result["is_suitable"] = False
            validation_result["reasons"] = [f"驗證過程發生錯誤: {str(e)}"]

        return validation_result

    def identify_bounded_contexts(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        識別 Bounded Context

        Args:
            requirements: 需求字典

        Returns:
            Bounded Context 列表
        """
        bounded_contexts = []

        try:
            # 從需求中識別可能的領域邊界
            mvp_features = ""
            if 'stage_2' in requirements:
                mvp_features = requirements['stage_2'].get('mvp_features', '')

            problem_description = ""
            if 'stage_0' in requirements:
                problem_description = requirements['stage_0'].get('problem_description', '')

            # 簡單的邊界識別邏輯（實際實現中可以更複雜）
            if mvp_features:
                # 基於功能描述識別可能的子領域
                features = mvp_features.split('、')
                for i, feature in enumerate(features):
                    bounded_contexts.append({
                        "name": f"子領域_{i+1}",
                        "description": feature.strip(),
                        "core_concepts": [],
                        "responsibilities": [feature.strip()],
                        "integration_points": []
                    })

        except Exception as e:
            logger.error(f"識別 Bounded Context 時發生錯誤: {str(e)}")

        return bounded_contexts

    def define_domain_events(self, requirements: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        定義領域事件

        Args:
            requirements: 需求字典

        Returns:
            領域事件列表
        """
        domain_events = []

        try:
            # 從需求中識別可能的業務事件
            success_criteria = ""
            if 'stage_2' in requirements:
                success_criteria = requirements['stage_2'].get('success_criteria', '')

            # 基於成功標準識別事件
            if success_criteria:
                domain_events.append({
                    "name": "業務目標達成事件",
                    "description": f"當 {success_criteria} 時觸發",
                    "trigger": success_criteria,
                    "data": "相關業務數據",
                    "handlers": "相關處理者"
                })

        except Exception as e:
            logger.error(f"定義領域事件時發生錯誤: {str(e)}")

        return domain_events