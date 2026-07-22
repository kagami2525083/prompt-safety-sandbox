import os
import streamlit as st
import google.generativeai as genai

# StreamlitのSecrets（設定）または環境変数からAPIキーを取得
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーが設定されていません。StreamlitのSecretsに 'GEMINI_API_KEY' を設定してください。")
    st.stop()

genai.configure(api_key=api_key)

# タイトル
st.title("Prompt Safety Sandbox")
st.caption("〜ポジ・ネガ・温度計先生による泥臭いAIプロンプト判定道場〜")

# システムプロンプト（3人の基本設定）
BASE_PROMPT = """
あなたはAIモラルのアドバイザーです。
ユーザーから入力されたプロンプトに対して、以下の3つの役割（視点）で評価・回答を行ってください。

1. 🔵 ネガくん（低温度：リスク・欠点と冷徹な指摘）
   - プロンプトの甘さ、個人情報（PII）のリスク、社外秘漏洩の危険性などを厳しく指摘する。

2. 🟢 温度計先生（中温度：全体講評とバランス指導）
   - 実務に即した総合評価、改善点、および模範的なプロンプト案を提示する。

3. 🟡 ポジくん（高温度：アイデアの広がりと前向きな提案）
   - ビジネスでの活用可能性や、さらに表現を広げるアイデアをポジティブに提案する。
"""

# 入力フォーム
user_prompt = st.text_area(
    "判定したいプロンプトを入力してください：",
    max_chars=300,
    placeholder="例：自社の顧客データをAIに入力して傾向を分析したい。"
)

if st.button("道場で判定する"):
    if not user_prompt.strip():
        st.warning("プロンプトを入力してください。")
    else:
        with st.spinner("3人が判定中..."):
            try:
                # Gemini 1.5 Flashモデルで呼び出し
                model = genai.GenerativeModel("gemini-1.5-flash")
                full_input = f"{BASE_PROMPT}\n\n【評価対象のプロンプト】\n{user_prompt}"
                
                response = model.generate_content(full_input)
                
                # 判定結果の表示
                st.markdown("### 🥋 判定結果")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
