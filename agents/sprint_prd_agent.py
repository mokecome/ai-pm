# -*- coding: utf-8 -*-
"""
Sprint PRD Agent - AI-DLC Sprint 快速開發 PRD 生成器
適合單人開發者在 48-72 小時內完成 MVP 的快速開發場景
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

class SprintPRDAgent:
    """AI-DLC Sprint 模式 PRD 生成器"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化 Sprint PRD Agent

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

        # 創建 Sprint PRD Agent
        self.agent = LlmAgent(
            model=self.model,
            name="Sprint_PRD_Agent",
            description="AI-DLC Sprint 快速開發的 PRD 生成專家，專注於 48-72 小時 MVP 開發",
            instruction=self._get_instruction()
        )

    def _get_instruction(self) -> str:
        """獲取 AI-DLC Sprint 模式的指令"""
        return """You are an expert Product Owner specialized in AI-DLC Sprint methodology - a rapid development framework designed for individual developers to complete MVPs in 48-72 hours. Unlike traditional AI-DLC which focuses on enterprise teams, AI-DLC Sprint prioritizes speed, practicality, and immediate results.

## Core Principles You Follow

1. **Speed First**: MVP completion in 48-72 hours is non-negotiable
2. **Spec-Driven**: Create minimal but sufficient documentation
3. **Solo Developer Friendly**: Everything must be executable by one person
4. **Immediate Value**: Every hour must produce visible progress
5. **AI-Powered**: Leverage AI for maximum acceleration

## Your Workflow

When a user provides a project idea, you will:

### Phase 1: Rapid Spec Generation (30 minutes maximum)

1. **Extract Core Intent** (5 minutes)
   - Focus exclusively on: What problem it solves, Who will use it, Why it matters
   - Completely ignore enterprise concerns (compliance, scalability, team coordination)

2. **Generate Minimal PRD** (15 minutes)

You will produce a PRD following this exact structure:

```markdown
# [Project Name] - AI-DLC Sprint Spec

## Core Intent (1 paragraph)
[What this solves in plain language - be specific and concise]

## Target User
[One sentence description of who will use this]

## MVP Features (Max 5)
- [ ] Feature 1 (Day 1) - [Brief description]
- [ ] Feature 2 (Day 1) - [Brief description]
- [ ] Feature 3 (Day 2) - [Brief description]
- [ ] Feature 4 (Day 2) - [Brief description]
- [ ] Feature 5 (Day 3) - [Brief description]

## Non-Features (What we're NOT building)
- [Explicitly exclude complex features that would delay MVP]
- [List tempting features that must wait for v2]
- [Identify scope creep risks]

## Success Criteria
- Can be demoed in 5 minutes
- Solves one problem well
- Deployable on Day 3
- [Add 1-2 project-specific criteria]

## Technical Constraints
- Single developer execution
- Use existing libraries/frameworks
- No custom infrastructure
- [Add any specific constraints mentioned by user]

## Day-by-Day Execution Plan

### Day 1 (Hours 1-16)
- Hours 1-2: Setup and scaffolding
- Hours 3-8: Feature 1 implementation
- Hours 9-14: Feature 2 implementation
- Hours 15-16: Integration and testing

### Day 2 (Hours 17-32)
- Hours 17-22: Feature 3 implementation
- Hours 23-28: Feature 4 implementation
- Hours 29-32: Bug fixes and polish

### Day 3 (Hours 33-48)
- Hours 33-38: Feature 5 implementation
- Hours 39-42: Final testing and fixes
- Hours 43-46: Deployment setup
- Hours 47-48: Demo preparation
```

## Key Behaviors

1. **Be Ruthlessly Minimal**: If a feature takes more than 8 hours, it's too complex for MVP
2. **Prioritize Demoability**: Every feature must contribute to a compelling 5-minute demo
3. **Embrace Constraints**: Limitations drive creativity and speed
4. **No Perfectionism**: "Good enough" is perfect for Sprint MVP
5. **Clear Exclusions**: Be explicit about what you're NOT building to prevent scope creep

## Decision Framework

When evaluating features:
- Can one developer build this in <8 hours? → Include
- Does it directly serve the core intent? → Include
- Is it necessary for the 5-minute demo? → Include
- Everything else → Exclude from MVP

## Output Quality Standards

- PRD must be readable in 2 minutes
- Every feature must have a clear Day assignment
- Success criteria must be measurable
- Technical constraints must be realistic
- Execution plan must account for all 48 hours

## Communication Style

- Be direct and actionable
- Use simple language, avoid jargon
- Focus on "what" and "when", not "how"
- Provide confidence through clarity, not complexity

Remember: Your goal is to transform vague ideas into executable 48-hour sprints. Every decision should optimize for speed of delivery while maintaining just enough quality to demonstrate value.

請用繁體中文生成 PRD 內容，但保持 Markdown 結構標題使用英文以確保格式一致性。"""

    async def generate_prd(self, requirements: Dict[str, Any]) -> str:
        """
        根據需求生成 AI-DLC Sprint 模式的 PRD

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
                parts=[types.Part(text=f"""請根據以下收集到的需求，生成 AI-DLC Sprint 模式的 PRD：

{context}

請生成完整的 AI-DLC Sprint PRD，包含：
1. Core Intent：用一段話說明要解決的核心問題
2. Target User：一句話描述目標用戶
3. MVP Features：最多 5 個核心功能，分配到 Day 1-3
4. Non-Features：明確列出不會在 MVP 中實現的功能（防止範圍蔓延）
5. Success Criteria：可在 5 分鐘內展示、Day 3 可部署等標準
6. Technical Constraints：單人開發、使用現有工具、無需自建基礎設施
7. Day-by-Day Execution Plan：詳細的 48 小時執行計劃（每日 16 小時工作）

重點：
- 每個功能必須在 8 小時內完成
- 專注於可展示的核心價值
- 明確排除複雜功能
- 提供具體的時程規劃

請用繁體中文生成內容，Markdown 標題保持英文。"""
                )]
            )

            # 設置運行配置
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)

            # 創建 session service 和 runner
            session_service = InMemorySessionService()
            runner = Runner(
                agent=self.agent,
                app_name='sprint_prd_generation',
                session_service=session_service
            )

            # 創建會話
            session = await session_service.create_session(
                app_name='sprint_prd_generation',
                user_id='sprint_user',
                session_id=None
            )

            # 獲取回應
            response_text = ""
            async for event in runner.run_async(
                user_id='sprint_user',
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
            logger.error(f"Sprint PRD 生成時發生錯誤: {str(e)}")
            return f"Sprint PRD 生成失敗: {str(e)}"

    def _build_requirements_context(self, requirements: Dict[str, Any]) -> str:
        """構建需求上下文"""
        context = "收集到的需求信息：\n\n"

        # 核心問題
        if 'stage_0' in requirements or 'core_problem' in requirements:
            context += "【核心問題】\n"
            stage_0 = requirements.get('stage_0', requirements.get('core_problem', {}))
            context += f"問題描述：{stage_0.get('problem_description', '未定義')}\n"
            context += f"痛點程度：{stage_0.get('pain_level', '未定義')}/10\n"
            context += f"不解決的後果：{stage_0.get('consequences', '未定義')}\n\n"

        # 用戶輪廓
        if 'stage_1' in requirements or 'user_profile' in requirements:
            context += "【用戶輪廓】\n"
            stage_1 = requirements.get('stage_1', requirements.get('user_profile', {}))
            context += f"目標用戶：{stage_1.get('target_users', '未定義')}\n"
            context += f"現有解決方案：{stage_1.get('current_solution', '未定義')}\n"
            context += f"付費意願：{stage_1.get('willingness_to_pay', '未定義')}\n\n"

        # 成功定義
        if 'stage_2' in requirements or 'success_criteria' in requirements:
            context += "【成功定義】\n"
            stage_2 = requirements.get('stage_2', requirements.get('success_criteria', {}))
            context += f"成功標準：{stage_2.get('success_criteria', '未定義')}\n"
            context += f"量化指標：{stage_2.get('measurable_metrics', '未定義')}\n"
            context += f"MVP 功能：{stage_2.get('mvp_features', '未定義')}\n\n"

        return context

    def get_template_structure(self) -> Dict[str, Any]:
        """獲取 AI-DLC Sprint PRD 模板結構"""
        return {
            "title": "產品需求文檔 (PRD) - AI-DLC Sprint 模式",
            "sections": {
                "1_core_intent": {
                    "title": "Core Intent",
                    "description": "用一段話說明要解決的核心問題"
                },
                "2_target_user": {
                    "title": "Target User",
                    "description": "一句話描述目標用戶"
                },
                "3_mvp_features": {
                    "title": "MVP Features (Max 5)",
                    "description": "核心功能清單，每個功能分配到具體天數"
                },
                "4_non_features": {
                    "title": "Non-Features",
                    "description": "明確排除的功能，防止範圍蔓延"
                },
                "5_success_criteria": {
                    "title": "Success Criteria",
                    "description": "可測量的成功標準"
                },
                "6_technical_constraints": {
                    "title": "Technical Constraints",
                    "description": "技術限制和約束條件"
                },
                "7_execution_plan": {
                    "title": "Day-by-Day Execution Plan",
                    "subsections": [
                        "Day 1 (Hours 1-16)",
                        "Day 2 (Hours 17-32)",
                        "Day 3 (Hours 33-48)"
                    ]
                }
            }
        }

    def validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        驗證需求是否適合 AI-DLC Sprint 模式

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

            # Sprint 適合性指標
            sprint_indicators = [
                'mvp', '快速', '週末', '單人', '個人', 'solo',
                '48小時', '72小時', '兩天', '三天', '原型',
                '驗證', 'poc', '概念驗證', '最小', '簡單'
            ]

            anti_sprint_indicators = [
                '企業級', '大型', '複雜系統', '多部門', '團隊',
                '長期', '完整', '全面', '企業'
            ]

            # 計算適合性分數
            sprint_score = sum(1 for indicator in sprint_indicators if indicator in all_text)
            anti_sprint_score = sum(1 for indicator in anti_sprint_indicators if indicator in all_text)

            validation_result["score"] = sprint_score - anti_sprint_score

            # 判斷是否適合
            if validation_result["score"] >= 2:
                validation_result["reasons"].append("需求明確強調快速開發和 MVP，非常適合 Sprint 模式")
                validation_result["suggestions"] = [
                    "專注於最核心的 3-5 個功能",
                    "明確定義 Non-Features 防止範圍蔓延",
                    "確保每個功能可在 8 小時內完成",
                    "準備 5 分鐘的展示 Demo"
                ]
            elif validation_result["score"] >= 0:
                validation_result["reasons"].append("需求適合快速開發，可以使用 Sprint 模式")
                validation_result["suggestions"] = [
                    "建議進一步簡化功能範圍",
                    "考慮使用現有框架和工具加速開發",
                    "設定清晰的 48-72 小時時程目標"
                ]
            else:
                validation_result["is_suitable"] = False
                validation_result["reasons"].append("需求複雜度較高，可能不適合 48-72 小時 Sprint")
                validation_result["suggestions"] = [
                    "考慮使用 TDD 模式確保品質",
                    "或使用 DDD 模式處理複雜領域邏輯",
                    "如果堅持 Sprint，需要大幅簡化需求範圍"
                ]

        except Exception as e:
            logger.error(f"驗證需求時發生錯誤: {str(e)}")
            validation_result["is_suitable"] = True  # 預設為適合，讓用戶自行判斷
            validation_result["reasons"] = [f"驗證過程發生錯誤: {str(e)}"]

        return validation_result
