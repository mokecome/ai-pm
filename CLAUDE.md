# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

AI-PRD 生成器是一個智能產品需求文檔生成工具，透過互動式問答收集需求，並根據不同開發模式（Sprint/TDD/BDD/DDD）自動生成專業 PRD。

**核心技術棧：**
- Streamlit (Web UI 框架)
- Google ADK (AI Agent 開發框架)
- LiteLLM (多模型 LLM 介面)
- OpenAI GPT-4 (核心語言模型)

## 常用指令

### 啟動應用
```bash
streamlit run prd_app.py
```

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 環境變數設置
需要在 `.env` 文件中設置：
- `OPENAI_API_KEY`: OpenAI API 密鑰
- `OPENAI_BASE_URL`: API 基礎 URL（可選，預設為 https://api.openai.com/v1）

## 代碼架構

### Agent 系統設計

專案採用模組化 Agent 架構，每個 Agent 負責特定職責：

1. **RequirementCoordinator** (`agents/requirement_coordinator.py`)
   - 負責結構化問答收集用戶需求
   - 三階段收集流程：核心問題 → 用戶輪廓 → 成功定義
   - 自動推薦開發模式（基於關鍵詞分析）

2. **TDD_PRD_Agent** (`agents/tdd_prd_agent.py`)
   - 測試驅動開發模式 PRD 生成
   - 適用場景：技術產品、API 開發、高品質要求
   - 輸出：測試情境設計、Given-When-Then 規格、CI/CD 流程

3. **BDD_PRD_Agent** (`agents/bdd_prd_agent.py`)
   - 行為驅動開發模式 PRD 生成
   - 適用場景：用戶導向產品、B2C 應用、跨部門協作
   - 輸出：用戶故事、業務價值分析、用戶體驗設計

4. **DDD_PRD_Agent** (`agents/ddd_prd_agent.py`)
   - 領域驅動設計模式 PRD 生成
   - 適用場景：企業級應用、複雜系統、多領域整合
   - 輸出：領域模型、統一語言、微服務架構

5. **SprintPRDAgent** (`agents/sprint_prd_agent.py`)
   - AI-DLC Sprint 快速開發模式 PRD 生成
   - 適用場景：48-72小時 MVP、單人開發者、快速原型驗證
   - 輸出：極簡 PRD、Day-by-Day 執行計劃（48小時）、明確非功能列表

### Agent 通用模式

所有 Agent 遵循統一的實現模式：
- 使用 Google ADK 的 `LlmAgent` 基礎類
- 透過 LiteLLM 與 OpenAI GPT-4 互動
- 非同步處理（`async/await`）
- InMemorySessionService 管理會話狀態
- Runner + RunConfig 控制執行流程

### 關鍵設計模式

**Agent 初始化模式：**
```python
def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
    self.api_key = api_key or os.getenv("OPENAI_API_KEY")
    self.api_base = api_base or os.getenv("OPENAI_BASE_URL")

    self.model = LiteLlm(model="gpt-4o", api_base=self.api_base, api_key=self.api_key)

    self.agent = LlmAgent(
        model=self.model,
        name="AgentName",
        description="Agent 描述",
        instruction=self._get_instruction()
    )
```

**非同步執行模式：**
```python
session_service = InMemorySessionService()
runner = Runner(agent=self.agent, app_name='app_name', session_service=session_service)
session = await session_service.create_session(...)

async for event in runner.run_async(...):
    if event.content and event.content.parts[0].text:
        if not event.partial:
            response_text = event.content.parts[0].text
```

### Streamlit 狀態管理

應用使用 `st.session_state` 管理所有狀態：
- `chat_history`: 對話記錄
- `current_step`: 當前收集階段（0-3）
- `requirements`: 結構化需求數據（stage_0/1/2）
- `current_prd`: 生成的 PRD 內容
- `selected_mode`: 選擇的開發模式
- `review_results`: PRD 檢查結果
- `version_comparison`: 多版本 PRD 比較

**重要：** 修改 session_state 後必須調用 `st.rerun()` 來刷新 UI。

## 專案規則遵循

專案包含詳細的代碼生成規則（見根目錄 `CLAUDE.md`），關鍵原則：

1. **最小改動原則：** 只修改明確要求的內容，不擅自優化無關代碼
2. **依賴管理：** 新增 import 必須同步更新 `requirements.txt`
3. **禁用占位符：** 不使用 "YOUR_API_KEY"、"TODO" 等佔位符
4. **環境變數優先：** 敏感信息必須使用環境變數，不可硬編碼
5. **模塊化設計：** 符合第一性原理、KISS 原則、SOLID 原則
6. **DRY 原則：** 寫代碼前先檢索可複用模組
7. **智能日誌：** 記錄關鍵決策點和數據轉換，避免過度/不足記錄

## 開發注意事項

### Agent 開發
- 每個新 Agent 必須在 `agents/__init__.py` 中導出
- instruction 文本應清晰定義 Agent 職責和輸出格式
- 使用 `logger` 記錄關鍵流程和錯誤（已配置 logging）

### Streamlit 開發
- 自定義 CSS 樣式統一在 `prd_app.py` 頂部 `st.markdown()` 中定義
- 三標籤頁架構：需求收集、PRD 預覽、改進建議
- 使用 `st.spinner()` 提供異步操作的用戶反饋

### 需求收集流程
三階段問題定義在 `RequirementCoordinator.questions` 字典：
- Stage 0 (核心問題): 3 個問題
- Stage 1 (用戶輪廓): 3 個問題
- Stage 2 (成功定義): 3 個問題

回答存儲在 `st.session_state.requirements['stage_X']` 中，key 對應各階段的固定字段名。

### 開發模式選擇邏輯
`RequirementCoordinator._recommend_development_mode()` 使用關鍵詞匹配計分：
- **Sprint 關鍵詞**（優先級最高）：mvp、快速、週末、單人、48/72小時、原型、poc 等 → Sprint
- **複雜系統關鍵詞**：企業、多部門、複雜、整合、大型 等 → DDD
- **技術關鍵詞**：api、sdk、開發者、技術、架構、效能 等 → TDD
- **業務關鍵詞**：用戶、客戶、體驗、界面、流程、業務 等 → BDD

**推薦優先級：** Sprint > DDD > TDD > BDD

可根據需要擴展關鍵詞列表或改進演算法。

## 文件結構說明

```
ai_pm/
├── prd_app.py              # Streamlit 主應用（UI 和流程控制）
├── agents/                 # AI Agent 模組
│   ├── requirement_coordinator.py  # 需求收集協調器
│   ├── sprint_prd_agent.py        # Sprint (AI-DLC) PRD 生成器
│   ├── tdd_prd_agent.py           # TDD PRD 生成器
│   ├── bdd_prd_agent.py           # BDD PRD 生成器
│   └── ddd_prd_agent.py           # DDD PRD 生成器
├── utils/                  # 工具模組（未完全實現）
├── requirements.txt        # Python 依賴清單
└── README.md              # 用戶文檔
```

**注意：** `app.py` 和 `travel_ws.py` 是舊版本遺留文件，當前主入口為 `prd_app.py`。
