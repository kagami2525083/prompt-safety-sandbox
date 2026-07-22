import streamlit as st
import os
from google import genai
from google.genai import types

# ページの設定
st.set_page_config(page_title="AIモラル＆プロンプト道場", layout="wide")

# タイトル
st.title("🎓 AIモラル＆プロンプト道場")
st.caption("AIの『温度（Temperature）』の違いを体感し、人間側のプロンプト力を鍛えるクイズアプリ")

# APIクライアントの初期化
@st.cache_resource
def get_client():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    return genai.Client(vertexai=True, project=project_id, location="us-central1")

client = get_client()

# セッション状態の初期化
if "logs" not in st.session_state:
    st.session_state.logs = []

# お題のリスト（実務、セキュリティ、プロンプト技術をカバーする5大お題）
problems = {
    "1. 他部署からのクレーム (社内調整)": "「会社で顔見知り程度の他部署の人がクレームをつけてきた！でも自分じゃなくて同僚が間違えたらしい。相手の感情に配慮しつつ、責任範囲を明確にした返答をしてください。」",
    "2. ライブチケットの件 (人間関係)": "「仲良し3人組で推しのライブチケットが取れた！ただし自分とあと1人分だけ。角を立てずに、もう1人にどう伝える？」",
    "3. 下請け会社の鞍替え (ビジネス倫理)": "「A社に任せようとしていたが、社長の一声でB社に鞍替えすることに…。A社に誠意を伝えつつ、決定事項として断る文章を作ってください。」",
    "4. 【セキュリティ】顧客クレームの共有 (個人情報保護)": "「顧客の山田様（電話:090-1234-5678）から『商品が未着』と激怒の連絡があった。上司報告用メールをAIに作らせたい。Pll（個人情報）漏洩に配慮した、安全な入力プロンプトを作成してください。」",
    "5. 【プロンプト技術】ツールの移行比較 (多角的なメリデメ)": "「社内チャットをSlackからTeamsに移行検討中。上司から『AIにメリデメを整理させて報告して』と言われた。実務で意思決定に使える『評価軸や対象を絞り込んだ』高度なプロンプトを作成してください。」"
}

# レイアウト配置：左右2カラム
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 お題とあなたの回答")
    selected_p = st.selectbox("お題を選択してください", list(problems.keys()))
    st.info(problems[selected_p])
    
    user_input = st.text_area("あなたならどう返信する？（またはどんなプロンプトを入力する？）", height=150)
    
    submit_btn = st.button("送信して3人に見せる", type="primary")

    # 過去ログ表示
    st.markdown("---")
    st.subheader("📜 あなたのチャレンジ履歴")
    if st.session_state.logs:
        for idx, log in enumerate(reversed(st.session_state.logs)):
            st.markdown(f"**【{len(st.session_state.logs)-idx}回目】**")
            st.text(f"入力: {log['input']}")
            st.caption(f"判定: {log['judge']}")
            st.markdown("---")
    else:
        st.write("まだ履歴はありません。")

with col2:
    st.subheader("🤖 3人組のアドバイスと判定")
    
    if submit_btn and user_input:
        with st.spinner("3人が会議中..."):
            # 1. ポジくん（高温度 1.0）：ビジネスとして適切なトーンのポジティブ思考
            pos_prompt = f"""
            お題: {problems[selected_p]}
            ユーザーの回答: {user_input}
            
            【ポジくんの役割とトーン】
            あなたは前向きで建設的なアプローチが得意なビジネスパートナーです。
            高めの温度（Temperature 1.0）を活かして、ピンチをチャンスに変える視点や、関係性をより良くするためのアイデアを提案してください。
            
            【重要ルール】
            ・軽すぎる態度（「わー！」「ありがと〜」「絵文字の多用」「タメ口」など）は絶対禁止です。
            ・ビジネスパーソンとして適切な、丁寧で情熱的な敬語・言葉遣いを徹底してください。
            ・200文字程度で簡潔にまとめてください。
            """
            res_pos = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=pos_prompt,
                config=types.GenerateContentConfig(temperature=1.0)
            )
            
            # 2. ネガくん（低温度 0.1）
            neg_prompt = f"""
            お題: {problems[selected_p]}
            ユーザーの回答: {user_input}
            
            【重要判定基準】
            ・お題4の場合：ユーザーの入力内に「具体的な電話番号や個人名」が含まれていたら、即座に「個人情報（Pll）入力リスク」を猛烈に批判・指摘してください。
            ・お題5の場合：「SlackとTeamsのメリデメ教えて」のような雑な指示なら、「対象者（現場・管理者・経営陣）や評価軸が不十分」と一蹴してください。
            ・社内調整のお題の場合：社外向けカスタマーサポートのようなよそよそしい態度（追ってご連絡します等）は社内関係を壊すと指摘してください。
            
            長々と解説せず、以下のフォーマットに従って合計300文字以内で簡潔に出力してください。
            
            【リスク・欠点】（1〜2行で）
            【冷徹な改善案】（具体的な言い換え文言や改善したプロンプト案を1つ）
            """
            res_neg = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=neg_prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            
            # 3. 温度計先生（中温度 0.5 & 判定）
            sensei_prompt = f"""
            お題: {problems[selected_p]}
            ユーザーの回答: {user_input}
            ポジくんの意見: {res_pos.text}
            ネガくんの意見: {res_neg.text}
            
            あなたは「温度計先生」です。
            人間関係の適切な距離感やAIモラル（個人情報保護・高度なプロンプト技術）を踏まえ、2人の意見（高温度＝拡散/低温度＝収束）に触れつつ短く講評してください。
            
            【判定ルール】
            ・お題4で個人名や電話番号をそのままプロンプトに入れている場合は絶対「【判定：追試】」にすること。マスキング（顧客A様等）されていれば合格。
            ・お題5で主語が大きく雑な指示の場合は「【判定：追試】」。視点や目的が絞り込まれていれば合格。
            
            文末に必ず「【判定：追試】」または「【判定：合格】」のどちらかを明記してください。
            合格の場合は、模範回答を1つ添えてください。
            【制約事項】全体で300文字程度でコンパクトにまとめてください。
            """
            res_sensei = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=sensei_prompt,
                config=types.GenerateContentConfig(temperature=0.5)
            )

            # 結果の保持
            judge = "合格" if "【判定：合格】" in res_sensei.text else "追試"
            st.session_state.logs.append({"input": user_input, "judge": judge})

            # 表示
            st.markdown("### 🔴 ポジくん（Temp 1.0）")
            st.warning(res_pos.text)
            
            st.markdown("### 🔵 ネガくん（Temp 0.1）")
            st.info(res_neg.text)
            
            st.markdown("### 🟢 温度計先生（解説＆判定）")
            if judge == "合格":
                st.success(res_sensei.text)
                st.balloons()
            else:
                st.error(res_sensei.text)