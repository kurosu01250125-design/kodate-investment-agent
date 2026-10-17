import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai

# ページのレイアウト設定
st.set_page_config(
    page_title="中古戸建投資AIエージェント",
    page_icon="🏠",
    layout="wide"
)

# スタイリッシュなデザインのためのCSS
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1E3A8A; }
    .result-box { background-color: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

# サイドバー（設定・使い方）
with st.sidebar:
    st.header("⚙️ 設定 & ガイド")
    api_key_input = st.text_input("Gemini APIキー", type="password", help="Google AI Studioで無料で取得できます")
    st.markdown("[🔗 Google AI Studio (無料)](https://aistudio.google.com/)")
    
    st.markdown("---")
    st.markdown("### 📋 使い方")
    st.markdown("1. **APIキー**を入力する")
    st.markdown("2. 「URL入力」または「テキスト貼り付け」を選ぶ")
    st.markdown("3. **「AI分析を実行する」**ボタンを押す")

# メインコンテンツ
st.markdown('<p class="main-header">🏠 中古戸建投資 AI分析エージェント</p>', unsafe_allow_html=True)
st.write("物件のURL、または紹介文やマイソクのテキストを読み込ませて、投資判断のレポートを自動生成します。")

# 入力方法の切り替えタブ
input_tab1, input_tab2 = st.tabs(["🔗 URLで自動取得", "📋 チラシ・テキスト直接貼り付け"])

scraped_text = ""

with input_tab1:
    url_input = st.text_input("物件詳細ページのURLを入力してください", placeholder="https://suumo.jp/jj/bukken/shousai/...", key="url")
    if url_input:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url_input, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.extract()
            scraped_text = soup.get_text(separator=' ', strip=True)[:15000]
        except Exception as e:
            st.error(f"URLからの読み込みに失敗しました: {e}")

with input_tab2:
    text_input = st.text_area("物件の紹介文やマイソクの文章をここに貼り付けてください", placeholder="ここにポータルサイトのテキストや図面の文字をコピー＆ペースト...", height=150, key="text")
    if text_input:
        scraped_text = text_input[:15000]

# 分析実行ボタン
if st.button("🚀 AI分析を実行する", type="primary"):
    if not api_key_input:
        st.error("⚠️ 左側のサイドバーに Gemini APIキーを入力してください。")
    elif not scraped_text:
        st.warning("⚠️ 物件のURLを入力するか、テキストを貼り付けてください。")
    else:
        with st.status("🤖 AIエージェントが稼働中...", expanded=True) as status:
            st.write("データを元に、収支やリスクをAIが多角的に分析しています...")
            try:
                client = genai.Client(api_key=api_key_input)
                
                prompt = f"""
                あなたはプロの不動産投資コンサルタント（中古戸建専門）です。
                以下の物件情報を基に、投資判断の参考になる詳細な分析レポートをわかりやすく作成してください。

                【分析出力項目】
                - **【物件概要】**（所在地、価格、築年数、構造、土地/建物面積）
                - **【収支・利回り試算】**（表面利回りの確認、想定賃料に対する妥当性）
                - **【想定リフォーム・修繕ポイント】**（築年数や状態から推測されるリフォーム箇所と大まかな予測）
                - **【主要なリスク・懸念点】**（再建築不可、接道、残置物、遠隔地管理など）
                - **【総合投資判断】**（「即買い推奨」「条件交渉次第」「見送り推奨」のいずれかとその理由）

                【対象物件データ】
                {scraped_text}
                """

                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                )
                
                status.update(label="分析が完了しました！", state="complete")
                
                st.markdown("### 📊 投資分析レポート")
                st.markdown(f'<div class="result-box">{response.text}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                status.update(label="AI処理エラー", state="error")
                st.error(f"AIの処理中にエラーが発生しました: {e}")
