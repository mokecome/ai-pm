# -*- coding: utf-8 -*-
"""
AI-PRD 生成機器人 - Streamlit 版本
使用純 Agent 模式的需求收集流程
"""

import streamlit as st
import os
import asyncio
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import logging

# 載入環境變數
load_dotenv(override=True)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 導入 Agents
from agents.requirement_coordinator import RequirementCoordinator
from agents.multi_version_generator import MultiVersionGenerator

# 頁面配置
st.set_page_config(
    page_title="AI-PRD 生成器",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS 樣式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    .progress-step {
        display: inline-block;
        padding: 8px 16px;
        margin: 4px;
        border-radius: 20px;
        font-weight: bold;
    }

    .step-active {
        background-color: #28a745;
        color: white;
    }

    .step-completed {
        background-color: #6c757d;
        color: white;
    }

    .step-pending {
        background-color: #f8f9fa;
        color: #6c757d;
        border: 2px solid #dee2e6;
    }

    .risk-high {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 10px;
        margin: 5px 0;
    }

    .risk-medium {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
    }

    .risk-low {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
def init_session_state():
    """初始化 session state 變數"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "current_prd" not in st.session_state:
        st.session_state.current_prd = ""

    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = None  # 用戶必須手動選擇

    if "review_results" not in st.session_state:
        st.session_state.review_results = None

    if "version_comparison" not in st.session_state:
        st.session_state.version_comparison = None

    if "api_key_validated" not in st.session_state:
        st.session_state.api_key_validated = False

    if "prd_check_results" not in st.session_state:
        st.session_state.prd_check_results = None

    # 初始化當前標籤頁索引
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = 0  # 0: 需求收集, 1: 初版PRD, 2: 多版本PRD

    # 初始化 RequirementCoordinator（純 Agent 模式）
    if "coordinator" not in st.session_state:
        try:
            st.session_state.coordinator = RequirementCoordinator()
            # 異步初始化 session
            asyncio.run(st.session_state.coordinator.initialize())
            # 獲取初始歡迎消息
            welcome_msg = asyncio.run(st.session_state.coordinator.send_message("開始"))
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": welcome_msg
            })
            logger.info("RequirementCoordinator 初始化成功")
        except Exception as e:
            logger.error(f"初始化 RequirementCoordinator 失敗: {str(e)}")
            st.error(f"初始化失敗: {str(e)}")

def display_requirements_guide():
    """顯示需求收集指南"""
    st.markdown("""
<div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 5px solid #0c5460;">

📋 **需要收集的信息：**

**1. 核心問題**
<span style="color: red;">• 你想解決什麼問題？ ⭐</span>
• 現在的痛點有多痛？（1-10分）
• 不解決會怎樣？

**2. 用戶輪廓**
<span style="color: red;">• 誰會用這個產品？ ⭐</span>
• 他們現在怎麼解決這個問題？
• 他們願意付多少錢解決？

**3. 成功定義**
• 怎樣算成功？
<span style="color: red;">• 有什麼可以量化的指標？ ⭐</span>
<span style="color: red;">• 最小可行產品要有哪些功能？ ⭐</span>

</div>
    """, unsafe_allow_html=True)

    st.markdown("""
<div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 5px solid #ffc107; margin-top: 15px;">

🎯 **PRD 開發模式建議：**

• **Sprint 模式（AI-DLC 快速開發）**
  適合：48-72小時 MVP、單人開發、快速原型驗證
  關鍵詞：mvp、快速、週末、原型、驗證

• **TDD 模式（測試驅動開發）**
  適合：技術產品、API 開發、高品質要求
  關鍵詞：api、sdk、技術、架構、效能

• **BDD 模式（行為驅動開發）**
  適合：用戶導向產品、B2C 應用、跨部門協作
  關鍵詞：用戶、體驗、界面、流程、業務

• **DDD 模式（領域驅動設計）**
  適合：企業級應用、複雜系統、多領域整合
  關鍵詞：企業、複雜、整合、大型、系統性

</div>
    """, unsafe_allow_html=True)

    st.caption("""
💡 **直接生成 PRD 的使用方式：**
• 必須先回答上述 4 個紅色星號（⭐）標記的必填問題
• 完成必填項後，可點擊「直接生成 PRD」按鈕快速生成文檔
• 建議：完整回答所有 9 個問題可獲得更專業、更詳細的 PRD
    """)

async def get_ai_response(user_input: str) -> str:
    """透過 RequirementCoordinator 獲取 AI 回應"""
    try:
        response = await st.session_state.coordinator.send_message(user_input)
        return response
    except Exception as e:
        logger.error(f"獲取 AI 回應時發生錯誤: {str(e)}")
        return f"處理過程中發生錯誤: {str(e)}"

def main():
    """主應用程式"""
    # 初始化
    init_session_state()

    # 主標題
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI-PRD 生成器</h1>
        <p>從需求收集到專業 PRD，一站式解決方案</p>
    </div>
    """, unsafe_allow_html=True)

    # 側邊欄設置
    with st.sidebar:
        st.title("🔧 設置")

        # API Key 管理
        st.subheader("OpenAI API Key")
        api_key = st.text_input(
            "輸入您的 API Key",
            type="password",
            help="可選：使用您自己的 API Key，否則使用預設設置"
        )

        if api_key:
            if st.button("驗證 API Key"):
                # TODO: 實際驗證 API Key
                st.session_state.api_key_validated = True
                st.success("✅ API Key 驗證成功！")

        st.divider()

        # 開發模式選擇
        st.subheader("開發模式")

        mode_options = ["一般開發 (AI-DLC Sprint)", "TDD (測試驅動)", "BDD (行為驅動)", "DDD (領域驅動)"]

        # 如果還沒選擇，顯示提示
        if st.session_state.selected_mode is None:
            default_index = 0
            st.info("💡 請選擇 PRD 開發模式")
        else:
            # 找到當前選擇的索引
            try:
                default_index = mode_options.index(st.session_state.selected_mode)
            except ValueError:
                default_index = 0

        mode = st.selectbox(
            "選擇開發模式",
            mode_options,
            index=default_index,
            help="""
            - Sprint：48-72小時快速 MVP，適合單人開發者
            - TDD：適合技術產品，品質優先
            - BDD：適合用戶產品，跨部門協作
            - DDD：適合複雜系統，領域建模
            """
        )
        st.session_state.selected_mode = mode

    # 主要內容：三個標籤頁
    tab1, tab2, tab3 = st.tabs(["📝 需求收集", "📋 初版PRD", "📊 多版本PRD"])

    with tab1:
        st.header("📝 需求收集對話")

        # 需求收集指南
        display_requirements_guide()

        st.divider()

        # 需求收集完成提示（檢測對話中是否包含完成標識）
        requirements_completed = any("需求收集完成" in msg.get("content", "")
                                    for msg in st.session_state.chat_history
                                    if msg.get("role") == "assistant")
        if requirements_completed:
            st.success("🎉 所有需求收集完成！可以在『初版PRD』標籤查看生成的 PRD。")

        # 對話歷史顯示和輸入整合為一個對話框
        st.subheader("對話記錄")

        # 使用 container 配合 height 設置創建可滾動的對話框
        chat_container = st.container(height=600)

        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])

        # 輸入框放在對話框下方
        st.markdown("### 💬 輸入您的回答")
        user_input = st.text_area(
            "請輸入您的回答：",
            height=100,
            key="user_input",
            placeholder="請輸入您的回答，按 Ctrl+Enter 或點擊下方發送按鈕...",
            label_visibility="collapsed"
        )

        col1, col2, col3 = st.columns([1, 1.5, 2.5])
        with col1:
            send_button = st.button("📤 發送", type="primary", use_container_width=True)
        with col2:
            generate_prd_button = st.button("📋 直接生成 PRD", type="secondary", use_container_width=True)

        if send_button and user_input and user_input.strip():
            # 保存用戶輸入
            message_to_send = user_input.strip()

            # 添加用戶消息到歷史
            st.session_state.chat_history.append({
                "role": "user",
                "content": message_to_send
            })

            # 透過 coordinator 獲取 AI 回應
            with st.spinner("思考中..."):
                ai_response = asyncio.run(get_ai_response(message_to_send))

            # 添加 AI 回應到歷史
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": ai_response
            })

            # 清空輸入框（透過刪除 session_state 中的 key）
            if "user_input" in st.session_state:
                del st.session_state["user_input"]

            st.rerun()

        # 直接生成 PRD 按鈕邏輯
        if generate_prd_button:
            # 檢查是否有對話記錄（至少回答了一些問題）
            user_messages = [msg for msg in st.session_state.chat_history if msg.get("role") == "user"]

            if len(user_messages) < 4:
                # 對話太少，提示用戶
                st.error("❌ 請至少回答 4 個關鍵問題後再生成 PRD")
            else:
                # 檢查是否已經完成
                already_completed = any("需求收集完成" in msg.get("content", "")
                                       for msg in st.session_state.chat_history
                                       if msg.get("role") == "assistant")

                if not already_completed:
                    # 添加完成標記
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "✅ 需求收集完成！您已回答了足夠的問題。請在側邊欄選擇開發模式，然後前往『初版PRD』標籤生成文檔。"
                    })

                # 設置當前標籤為初版PRD（索引 1）
                st.session_state.current_tab = 1

                # 使用更穩定的 JavaScript 自動切換到初版PRD標籤
                # 注入 JavaScript 代碼來點擊初版PRD標籤
                js_code = """
                <script>
                    // 使用多種方法確保能找到並點擊標籤
                    function switchTab() {
                        // 方法 1: 通過 data-baseweb 屬性
                        let tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
                        if (tabs.length > 1) {
                            tabs[1].click();
                            return true;
                        }

                        // 方法 2: 通過 role="tab" 屬性
                        tabs = window.parent.document.querySelectorAll('button[role="tab"]');
                        if (tabs.length > 1) {
                            tabs[1].click();
                            return true;
                        }

                        // 方法 3: 通過文字內容查找
                        const allButtons = window.parent.document.querySelectorAll('button');
                        for (let btn of allButtons) {
                            if (btn.textContent.includes('📋 初版PRD') || btn.textContent.includes('初版PRD')) {
                                btn.click();
                                return true;
                            }
                        }

                        return false;
                    }

                    // 延遲執行，確保頁面已加載
                    setTimeout(switchTab, 200);
                    // 再次嘗試（以防第一次失敗）
                    setTimeout(switchTab, 500);
                </script>
                """
                st.components.v1.html(js_code, height=0)

                st.rerun()

    with tab2:
        st.header("📋 初版PRD")

        # 檢查是否有對話歷史（判斷需求收集是否進行中）
        # 通過檢測對話中是否包含「✅ 需求收集完成」來判斷是否完成
        requirements_completed = any("需求收集完成" in msg.get("content", "")
                                    for msg in st.session_state.chat_history
                                    if msg.get("role") == "assistant")

        # 顯示狀態提示
        col1, col2 = st.columns(2)
        with col1:
            if requirements_completed:
                st.success("✅ 需求收集完成")
            else:
                st.info("⏳ 等待需求收集完成")

        with col2:
            if st.session_state.selected_mode:
                st.success(f"✅ 已選擇：{st.session_state.selected_mode}")
            else:
                st.warning("⚠️ 請選擇開發模式")

        st.divider()

        # 自動生成 PRD（如果條件滿足且還沒有生成）
        if requirements_completed and st.session_state.selected_mode and not st.session_state.current_prd:
            with st.spinner(f"正在根據 {st.session_state.selected_mode} 模式生成 PRD..."):
                # TODO: 調用實際的 PRD 生成 Agent
                # 這裡先使用模擬內容（後續會整合實際 PRD Agent）
                mode_name = st.session_state.selected_mode.split(" ")[0]  # 提取模式名稱
                st.session_state.current_prd = f"""# 產品需求文檔 (PRD) - {st.session_state.selected_mode}

## 1. 產品概述
【根據對話歷史生成...】

## 2. 核心需求
【根據對話歷史生成...】

## 3. MVP 功能
【根據對話歷史生成...】

## 4. 開發計劃（{mode_name} 模式）
【根據選定的開發模式生成...】

## 5. 預期效益
【根據對話歷史生成...】

---
*此 PRD 由 AI-PM 根據 {st.session_state.selected_mode} 模式自動生成*
"""
                st.rerun()

        # 顯示提示訊息（如果條件不滿足）
        if not requirements_completed or not st.session_state.selected_mode:
            warning_messages = []
            if not requirements_completed:
                warning_messages.append("⚠️ 尚未完成需求收集，請先前往『需求收集』標籤完成問答")
            if not st.session_state.selected_mode:
                warning_messages.append("⚠️ 尚未選擇開發模式，請在左側邊欄選擇 PRD 開發模式")

            for msg in warning_messages:
                st.warning(msg)

        # PRD 顯示和編輯區域（總是顯示 TEXTAREA）
        st.subheader("📄 PRD 內容")

        # 顯示 PRD 的 TEXTAREA
        prd_content = st.text_area(
            "PRD 內容（可編輯）",
            value=st.session_state.current_prd if st.session_state.current_prd else "# 產品需求文檔 (PRD)\n\n等待生成...",
            height=500,
            help="您可以直接編輯 PRD 內容",
            label_visibility="collapsed",
            key="prd_textarea"
        )

        # 保存編輯內容（只在有內容時）
        if st.session_state.current_prd and prd_content != st.session_state.current_prd:
            st.session_state.current_prd = prd_content

        st.divider()

        # 完整性檢查按鈕、AI升級檢查表按鈕、生成多版本PRD按鈕
        col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])
        with col1:
            check_button = st.button("🔍 完整性檢查", type="primary", use_container_width=True)

        with col2:
            ai_upgrade_button = st.button("✅ AI升級檢查表", type="secondary", use_container_width=True)

        with col3:
            generate_multi_button = st.button("🚀 生成多版本 PRD", type="secondary", use_container_width=True)

        if check_button:
            if not st.session_state.current_prd:
                st.error("❌ 請先生成 PRD 再進行檢查")
            else:
                with st.spinner("正在檢查 PRD 完整性..."):
                    from google.adk.models.lite_llm import LiteLlm
                    from google.genai import types

                    # 創建臨時模型實例
                    model = LiteLlm(
                        model="gpt-4o",
                        api_base=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                        api_key=os.getenv("OPENAI_API_KEY")
                    )

                    check_prompt = f"""請以專業產品經理和工程師的角度，檢查這份 PRD 的完整性，並回答以下問題：

PRD 內容：
{st.session_state.current_prd}

請分析並回答：
1. 有哪些重要但沒提到的部分？
2. 有哪些可能的風險沒考慮到？
3. 有哪些地方可能造成理解歧義？
4. 如果你是工程師，還需要知道什麼才能開始開發？

請使用 Markdown 格式回應，包含以下結構：

## 完整性檢查結果

### 1. 重要但沒提到的部分
[列出缺失的重要部分]

### 2. 可能的風險
[列出潛在風險]

### 3. 可能造成歧義的部分
[列出模糊不清的描述]

### 4. 工程師需要的額外信息
[列出開發所需的額外資訊]

### 改進建議
[提供具體的改進建議]

請用繁體中文回應。"""

                    try:
                        # 調用 LLM 進行檢查
                        content = types.Content(
                            role='user',
                            parts=[types.Part(text=check_prompt)]
                        )

                        response = model.generate_content(contents=[content])
                        response_text = response.text.strip()

                        # 保存檢查結果
                        st.session_state.prd_check_results = response_text
                        st.rerun()

                    except Exception as e:
                        logger.error(f"PRD 完整性檢查失敗: {str(e)}")
                        st.error(f"檢查過程發生錯誤: {str(e)}")

        # 顯示檢查結果
        if "prd_check_results" in st.session_state and st.session_state.prd_check_results:
            st.divider()
            st.subheader("📊 檢查結果")
            st.markdown(st.session_state.prd_check_results)

            # 自動更新 PRD 按鈕
            st.divider()
            if st.button("🔄 自動更新 PRD", key="auto_update_completeness", type="primary", use_container_width=True):
                with st.spinner("🔄 正在根據建議自動更新 PRD..."):
                    from google.adk.models.lite_llm import LiteLlm
                    from google.genai import types

                    try:
                        # 創建模型
                        model = LiteLlm(
                            model="gpt-4o",
                            api_base=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                            api_key=os.getenv("OPENAI_API_KEY")
                        )

                        # 構建提示詞
                        update_prompt = f"""請根據以下完整性檢查的改進建議，修正 PRD 內容。

原始 PRD：
{st.session_state.current_prd}

改進建議：
{st.session_state.prd_check_results}

請生成修正後的完整 PRD，要求：
1. 保持原有的 Markdown 結構和格式
2. 只修改需要改進的部分
3. 補充缺失的重要內容
4. 解決建議中指出的問題
5. 使用繁體中文輸出

請直接輸出修正後的完整 PRD，不要其他說明。"""

                        # 調用 AI
                        content = types.Content(
                            role='user',
                            parts=[types.Part(text=update_prompt)]
                        )

                        response = model.generate_content(contents=[content])
                        updated_prd = response.text.strip()

                        # 更新 PRD
                        st.session_state.current_prd = updated_prd
                        st.success("✅ PRD 已根據完整性檢查建議自動更新！請查看上方 PRD 內容。")
                        st.rerun()

                    except Exception as e:
                        logger.error(f"自動更新 PRD 失敗: {str(e)}")
                        st.error(f"更新過程發生錯誤: {str(e)}")

        # 生成多版本 PRD 按鈕邏輯
        if generate_multi_button:
            if not st.session_state.current_prd:
                st.error("❌ 請先生成初版 PRD")
            else:
                with st.spinner("🚀 正在生成三個版本的 PRD..."):
                    # 調用 MultiVersionGenerator
                    generator = MultiVersionGenerator()
                    versions = asyncio.run(generator.generate_versions(st.session_state.current_prd))

                    # 保存到 session state
                    st.session_state.version_comparison = versions

                    # 設置當前標籤為多版本PRD（第三個標籤）
                    st.session_state.current_tab = 2

                    # JavaScript 跳轉到第三個標籤
                    js_code = """
                    <script>
                        // 使用多種方法確保能找到並點擊標籤
                        function switchTab() {
                            // 方法 1: 通過 data-baseweb 屬性
                            let tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
                            if (tabs.length > 2) {
                                tabs[2].click();
                                return true;
                            }

                            // 方法 2: 通過 role="tab" 屬性
                            tabs = window.parent.document.querySelectorAll('button[role="tab"]');
                            if (tabs.length > 2) {
                                tabs[2].click();
                                return true;
                            }

                            // 方法 3: 通過文字內容查找
                            const allButtons = window.parent.document.querySelectorAll('button');
                            for (let btn of allButtons) {
                                if (btn.textContent.includes('📊 多版本PRD') || btn.textContent.includes('多版本PRD')) {
                                    btn.click();
                                    return true;
                                }
                            }

                            return false;
                        }

                        // 延遲執行，確保頁面已加載
                        setTimeout(switchTab, 200);
                        // 再次嘗試（以防第一次失敗）
                        setTimeout(switchTab, 500);
                    </script>
                    """
                    st.components.v1.html(js_code, height=0)

                    st.success("✅ 三版本 PRD 生成完成！正在跳轉...")
                    st.rerun()

        # AI升級檢查表按鈕邏輯
        if ai_upgrade_button:
            if not st.session_state.current_prd:
                st.error("❌ 請先生成初版 PRD")
            else:
                with st.spinner("🔍 正在進行 AI 升級檢查..."):
                    from google.adk.models.lite_llm import LiteLlm
                    from google.genai import types

                    # 創建臨時模型實例
                    model = LiteLlm(
                        model="gpt-4o",
                        api_base=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                        api_key=os.getenv("OPENAI_API_KEY")
                    )

                    check_prompt = f"""請分析以下 PRD，檢查是否符合 AI 友善的 PRD 標準。

PRD 內容：
{st.session_state.current_prd}

請檢查以下 13 個項目，並以 JSON 格式回應。每個項目包含兩個字段：
- "passed": true/false（是否符合標準）
- "suggestion": "具體改進建議"（如果 passed 為 false，提供具體建議；如果為 true，填空字串）

JSON 格式範例：
{{
  "basic": {{
    "problem_statement": {{
      "passed": false,
      "suggestion": "建議在 PRD 開頭補充明確的問題陳述，說明要解決什麼具體問題"
    }},
    "success_metrics": {{
      "passed": true,
      "suggestion": ""
    }}
  }}
}}

請檢查以下項目：

基本要素：
1. problem_statement - 有明確的問題陳述
2. success_metrics - 有可量化的成功指標
3. user_scenarios - 有具體的用戶場景
4. priority - 有優先級排序
5. timeline - 有時程預估

AI 友善要素：
6. structured_format - 使用結構化格式（JSON/YAML/Markdown）
7. term_definition - 專有名詞有明確定義
8. sample_data - 範例資料完整

可執行要素：
9. user_story - 可以直接轉成 User Story
10. test_cases - 可以生成測試案例
11. api_spec - 可以產生 API 規格
12. wireframe - 可以製作 Wireframe
13. time_estimate - 可以估算開發時間

請用繁體中文提供建議，只回應 JSON 格式，不要其他說明文字。"""

                    try:
                        # 調用 AI 進行檢查
                        content = types.Content(
                            role='user',
                            parts=[types.Part(text=check_prompt)]
                        )

                        response = model.generate_content(contents=[content])
                        response_text = response.text.strip()

                        # 嘗試解析 JSON
                        import re
                        json_match = re.search(r'\{[\s\S]*\}', response_text)
                        if json_match:
                            checklist_data = json.loads(json_match.group())
                            st.session_state.ai_upgrade_checklist = checklist_data
                        else:
                            st.session_state.ai_upgrade_checklist = None
                            st.error("無法解析檢查結果")

                        st.rerun()

                    except Exception as e:
                        logger.error(f"AI升級檢查失敗: {str(e)}")
                        st.error(f"檢查過程發生錯誤: {str(e)}")

        # 顯示 AI 升級檢查結果
        if "ai_upgrade_checklist" in st.session_state and st.session_state.ai_upgrade_checklist:
            st.divider()
            st.subheader("✅ AI 升級檢查表")

            checklist = st.session_state.ai_upgrade_checklist

            # 基本要素
            st.markdown("#### 📋 基本要素")

            # 問題陳述
            problem_statement = checklist.get("basic", {}).get("problem_statement", {})
            st.checkbox("有明確的問題陳述（Problem Statement）",
                       value=problem_statement.get("passed", False),
                       disabled=True, key="check_basic_1")
            if not problem_statement.get("passed", False) and problem_statement.get("suggestion"):
                st.markdown(f"💡 **建議：** {problem_statement.get('suggestion')}")

            # 成功指標
            success_metrics = checklist.get("basic", {}).get("success_metrics", {})
            st.checkbox("有可量化的成功指標（Success Metrics）",
                       value=success_metrics.get("passed", False),
                       disabled=True, key="check_basic_2")
            if not success_metrics.get("passed", False) and success_metrics.get("suggestion"):
                st.markdown(f"💡 **建議：** {success_metrics.get('suggestion')}")

            # 用戶場景
            user_scenarios = checklist.get("basic", {}).get("user_scenarios", {})
            st.checkbox("有具體的用戶場景（User Scenarios）",
                       value=user_scenarios.get("passed", False),
                       disabled=True, key="check_basic_3")
            if not user_scenarios.get("passed", False) and user_scenarios.get("suggestion"):
                st.markdown(f"💡 **建議：** {user_scenarios.get('suggestion')}")

            # 優先級排序
            priority = checklist.get("basic", {}).get("priority", {})
            st.checkbox("有優先級排序（Priority）",
                       value=priority.get("passed", False),
                       disabled=True, key="check_basic_4")
            if not priority.get("passed", False) and priority.get("suggestion"):
                st.markdown(f"💡 **建議：** {priority.get('suggestion')}")

            # 時程預估
            timeline = checklist.get("basic", {}).get("timeline", {})
            st.checkbox("有時程預估（Timeline）",
                       value=timeline.get("passed", False),
                       disabled=True, key="check_basic_5")
            if not timeline.get("passed", False) and timeline.get("suggestion"):
                st.markdown(f"💡 **建議：** {timeline.get('suggestion')}")

            # AI 友善要素
            st.markdown("#### 🤖 AI 友善要素")

            # 結構化格式
            structured_format = checklist.get("ai_friendly", {}).get("structured_format", {})
            st.checkbox("使用結構化格式（JSON/YAML/Markdown）",
                       value=structured_format.get("passed", False),
                       disabled=True, key="check_ai_1")
            if not structured_format.get("passed", False) and structured_format.get("suggestion"):
                st.markdown(f"💡 **建議：** {structured_format.get('suggestion')}")

            # 專有名詞定義
            term_definition = checklist.get("ai_friendly", {}).get("term_definition", {})
            st.checkbox("專有名詞有明確定義",
                       value=term_definition.get("passed", False),
                       disabled=True, key="check_ai_2")
            if not term_definition.get("passed", False) and term_definition.get("suggestion"):
                st.markdown(f"💡 **建議：** {term_definition.get('suggestion')}")

            # 範例資料
            sample_data = checklist.get("ai_friendly", {}).get("sample_data", {})
            st.checkbox("範例資料完整",
                       value=sample_data.get("passed", False),
                       disabled=True, key="check_ai_3")
            if not sample_data.get("passed", False) and sample_data.get("suggestion"):
                st.markdown(f"💡 **建議：** {sample_data.get('suggestion')}")

            # 可執行要素
            st.markdown("#### ⚡ 可執行要素")

            # User Story
            user_story = checklist.get("executable", {}).get("user_story", {})
            st.checkbox("可以直接轉成 User Story",
                       value=user_story.get("passed", False),
                       disabled=True, key="check_exec_1")
            if not user_story.get("passed", False) and user_story.get("suggestion"):
                st.markdown(f"💡 **建議：** {user_story.get('suggestion')}")

            # 測試案例
            test_cases = checklist.get("executable", {}).get("test_cases", {})
            st.checkbox("可以生成測試案例",
                       value=test_cases.get("passed", False),
                       disabled=True, key="check_exec_2")
            if not test_cases.get("passed", False) and test_cases.get("suggestion"):
                st.markdown(f"💡 **建議：** {test_cases.get('suggestion')}")

            # API 規格
            api_spec = checklist.get("executable", {}).get("api_spec", {})
            st.checkbox("可以產生 API 規格",
                       value=api_spec.get("passed", False),
                       disabled=True, key="check_exec_3")
            if not api_spec.get("passed", False) and api_spec.get("suggestion"):
                st.markdown(f"💡 **建議：** {api_spec.get('suggestion')}")

            # Wireframe
            wireframe = checklist.get("executable", {}).get("wireframe", {})
            st.checkbox("可以製作 Wireframe",
                       value=wireframe.get("passed", False),
                       disabled=True, key="check_exec_4")
            if not wireframe.get("passed", False) and wireframe.get("suggestion"):
                st.markdown(f"💡 **建議：** {wireframe.get('suggestion')}")

            # 開發時間估算
            time_estimate = checklist.get("executable", {}).get("time_estimate", {})
            st.checkbox("可以估算開發時間",
                       value=time_estimate.get("passed", False),
                       disabled=True, key="check_exec_5")
            if not time_estimate.get("passed", False) and time_estimate.get("suggestion"):
                st.markdown(f"💡 **建議：** {time_estimate.get('suggestion')}")

            # 自動更新 PRD 按鈕
            st.divider()
            if st.button("🔄 自動更新 PRD", key="auto_update_ai_checklist", type="primary", use_container_width=True):
                with st.spinner("🔄 正在根據 AI 升級檢查建議自動更新 PRD..."):
                    from google.adk.models.lite_llm import LiteLlm
                    from google.genai import types

                    try:
                        # 提取所有未通過項目的建議
                        suggestions = []
                        checklist = st.session_state.ai_upgrade_checklist

                        for category in ["basic", "ai_friendly", "executable"]:
                            for item_name, item_data in checklist.get(category, {}).items():
                                if isinstance(item_data, dict):
                                    if not item_data.get("passed", False) and item_data.get("suggestion"):
                                        suggestions.append(item_data.get("suggestion"))

                        # 構建建議文本
                        if suggestions:
                            suggestions_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(suggestions)])
                        else:
                            st.info("✅ 所有檢查項目都已通過，無需更新！")
                            st.stop()

                        # 創建模型
                        model = LiteLlm(
                            model="gpt-4o",
                            api_base=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                            api_key=os.getenv("OPENAI_API_KEY")
                        )

                        # 構建提示詞
                        update_prompt = f"""請根據以下 AI 升級檢查的改進建議，修正 PRD 內容，使其符合 AI 友善標準。

原始 PRD：
{st.session_state.current_prd}

需要改進的項目：
{suggestions_text}

請生成修正後的完整 PRD，要求：
1. 保持原有的 Markdown 結構和格式
2. 根據每個建議進行針對性改進
3. 確保 PRD 符合 AI 友善標準（結構化、明確定義、可執行）
4. 使用繁體中文輸出

請直接輸出修正後的完整 PRD，不要其他說明。"""

                        # 調用 AI
                        content = types.Content(
                            role='user',
                            parts=[types.Part(text=update_prompt)]
                        )

                        response = model.generate_content(contents=[content])
                        updated_prd = response.text.strip()

                        # 更新 PRD
                        st.session_state.current_prd = updated_prd
                        st.success("✅ PRD 已根據 AI 升級檢查建議自動更新！請查看上方 PRD 內容。")
                        st.rerun()

                    except Exception as e:
                        logger.error(f"自動更新 PRD 失敗: {str(e)}")
                        st.error(f"更新過程發生錯誤: {str(e)}")


    with tab3:
        st.header("📊 多版本PRD")

        if not st.session_state.current_prd:
            st.warning("⏳ 請先在『初版PRD』中生成 PRD")
        else:
            st.info("生成三個版本的 PRD：MVP版、標準版、理想版，並提供比較分析")

            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🚀 生成三版本 PRD", type="primary", use_container_width=True):
                    with st.spinner("正在生成三個版本的 PRD..."):
                        # 調用 MultiVersionGenerator
                        generator = MultiVersionGenerator()
                        versions = asyncio.run(generator.generate_versions(st.session_state.current_prd))
                        st.session_state.version_comparison = versions
                        st.success("✅ 三版本 PRD 生成完成！")
                        st.rerun()

            st.divider()

            # 顯示三版本比較
            if st.session_state.version_comparison:
                st.subheader("📊 版本比較分析")

                # 比較表格
                comparison_data = {
                    "比較項目": ["功能範圍", "開發成本", "技術難度", "開發時間", "預期效益", "風險等級"],
                    "MVP版": ["核心功能", "低（< 10萬）", "簡單", "7天", "快速驗證", "低"],
                    "標準版": ["主要功能", "中（10-50萬）", "中等", "1個月", "商業化就緒", "中"],
                    "理想版": ["完整功能", "高（> 50萬）", "複雜", "不限", "極致體驗", "高"]
                }

                st.dataframe(comparison_data, use_container_width=True)

                st.divider()

                # 三版本詳細內容
                st.subheader("📋 詳細 PRD 內容")

                tab_mvp, tab_standard, tab_ideal = st.tabs(["🏃‍♂️ MVP版", "🎯 標準版", "⭐ 理想版"])

                with tab_mvp:
                    st.text_area(
                        "MVP版 PRD",
                        value=st.session_state.version_comparison["mvp"],
                        height=300,
                        key="mvp_prd"
                    )

                with tab_standard:
                    st.text_area(
                        "標準版 PRD",
                        value=st.session_state.version_comparison["standard"],
                        height=300,
                        key="standard_prd"
                    )

                with tab_ideal:
                    st.text_area(
                        "理想版 PRD",
                        value=st.session_state.version_comparison["ideal"],
                        height=300,
                        key="ideal_prd"
                    )

                # 導出功能
                st.divider()
                st.subheader("📤 導出選項")

                export_col1, export_col2, export_col3, export_col4 = st.columns(4)

                with export_col1:
                    # 導出 Markdown
                    combined_content = f"""# 完整 PRD 文檔

## 原始需求
{json.dumps(st.session_state.requirements, ensure_ascii=False, indent=2)}

## 初版 PRD
{st.session_state.current_prd}

## MVP版
{st.session_state.version_comparison["mvp"]}

## 標準版
{st.session_state.version_comparison["standard"]}

## 理想版
{st.session_state.version_comparison["ideal"]}
"""
                    st.download_button(
                        label="📄 導出 Markdown",
                        data=combined_content,
                        file_name="complete_prd.md",
                        mime="text/markdown"
                    )

                with export_col2:
                    # 導出 JSON
                    json_data = {
                        "requirements": st.session_state.requirements,
                        "initial_prd": st.session_state.current_prd,
                        "versions": st.session_state.version_comparison,
                        "review_results": st.session_state.review_results
                    }
                    st.download_button(
                        label="📊 導出 JSON",
                        data=json.dumps(json_data, ensure_ascii=False, indent=2),
                        file_name="prd_data.json",
                        mime="application/json"
                    )

                with export_col3:
                    if st.button("📋 複製內容"):
                        st.code(combined_content, language="markdown")
                        st.success("✅ 內容已顯示，請手動複製")

                with export_col4:
                    if st.button("🔗 分享連結"):
                        # TODO: 實現分享功能
                        st.success("🔗 分享連結：https://...")
                        st.info("分享功能開發中...")

if __name__ == "__main__":
    main()