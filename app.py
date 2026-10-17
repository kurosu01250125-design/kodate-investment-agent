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

# スタイリッシュなデザインのためのCSS（オプション）
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
    st.markdown("2. 不動産ポータルサイト等の**物件URL**を貼り付ける")
    st.markdown("3. **「AI分析を実行する」**ボタンを押す")

# メインコンテンツ
st.markdown('<p class="main-header">🏠 中古戸建投資 AI分析エージェント</p>', unsafe_allow_html=True)
st.write("物件のURLを入力するだけで、AIが自動でページを読み込み、投資判断のレポートをブラウザ上に生成します。")

# 入力フォーム
url_input = st.text_input("🔍 物件詳細ページのURLを入力してください", placeholder="https://suumo.jp/jj/bukken/shousai/...", key="url")

def fetch_url_content(url):
    """Webページからテキストを抽出する関数"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 不要なタグを削除してテキストをスッキリさせる
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return text[:15000] # トークン節約のため文字数制限
    except Exception as e:
        return f"エラー: URLの読み込みに失敗しました ({e})"

if st.button("🚀 AI分析を実行する", type="primary"):
    if not api_key_input:
        st.error("⚠️ 左側のサイドバーに Gemini APIキーを入力してください。")
    elif not url_input:
        st.warning("⚠️ 物件のURLを入力してください。")
    else:
        # プログレス表示
        with st.status("🤖 AIエージェントが稼働中...", expanded=True) as status:
            st.write("1. 物件ページへアクセスし、情報を抽出しています...")
            scraped_text = fetch_url_content(url_input)
            
            if "エラー" in scraped_text:
                status.update(label="情報の取得に失敗しました", state="error")
                st.error(scraped_text)
            else:
                st.write("2. 抽出したデータを元に、収支やリスクをAIが多角的に分析しています...")
                try:
                    client = genai.Client(api_key=api_key_input)
                    
                    prompt = f"""
                    あなたはプロの不動産投資コンサルタント（中古戸建専門）です。
                    以下のWebページから取得した物件情報を基に、投資判断の参考になる詳細な分析レポートをブラウザ向けにわかりやすく作成してください。

                    【分析出力項目】
                    - **【物件概要】**（所在地、価格、築年数、構造、土地/建物面積）
                    - **【収支・利回り試算】**（表面利回りの確認、想定賃料に対する妥当性）
                    - **【想定リフォーム・修繕ポイント】**（築年数や状態から推測されるリフォーム箇所と大まかな予測）
                    - **【主要なリスク・懸念点】**（再建築不可、接道、残置物、遠隔地管理など）
                    - **【総合投資判断】**（「即買い推奨」「条件交渉次第」「見送り推奨」のいずれかとその理由）

                    【対象物件の生データ】
                    {scraped_text}
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    
                    status.update(label="分析が完了しました！", state="complete")
                    
                    # 結果を表示するボックス
                    st.markdown("### 📊 投資分析レポート")
                    st.markdown(f'<div class="result-box">{response.text}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    status.update(label="AI処理エラー", state="error")
                    st.error(f"AIの処理中にエラーが発生しました: {e}")
