import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ページ設定
st.set_page_config(
    page_title="子供のおこづかい帳",
    page_icon="💰",
    layout="wide"
)

# セッション状態の初期化
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

if 'savings_goal' not in st.session_state:
    st.session_state.savings_goal = 1000

if 'child_name' not in st.session_state:
    st.session_state.child_name = "太郎"

# タイトル
st.title("💰 子供のおこづかい帳")

# サイドバー：設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    child_name = st.text_input(
        "お子さんの名前",
        value=st.session_state.child_name,
        help="お子さんの名前を入力してください"
    )
    st.session_state.child_name = child_name
    
    savings_goal = st.number_input(
        "🎯 貯金目標（円）",
        min_value=0,
        value=st.session_state.savings_goal,
        step=100,
        help="いくら貯めたいか目標を設定"
    )
    st.session_state.savings_goal = savings_goal
    
    st.markdown("---")
    
    # データリセット
    if st.button("🗑️ 全データをリセット", use_container_width=True):
        st.session_state.transactions = []
        st.success("✅ データをリセットしました")
        st.rerun()

# 現在の残高を計算
total_income = sum([t['金額'] for t in st.session_state.transactions if t['種類'] == '収入'])
total_expense = sum([t['金額'] for t in st.session_state.transactions if t['種類'] == '支出'])
balance = total_income - total_expense

# メインエリア
st.subheader(f"👦 {child_name}くん/さんのおこづかい")

# 残高表示
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 現在の残高", f"{balance:,}円", delta=None)

with col2:
    st.metric("📥 もらった合計", f"{total_income:,}円", delta=None)

with col3:
    st.metric("📤 使った合計", f"{total_expense:,}円", delta=None)

with col4:
    if savings_goal > 0:
        progress = min((balance / savings_goal) * 100, 100)
        st.metric("🎯 目標達成率", f"{progress:.0f}%", delta=None)
    else:
        st.metric("🎯 目標達成率", "未設定", delta=None)

# 目標までの進捗バー
if savings_goal > 0:
    progress_percent = min(balance / savings_goal, 1.0)
    st.progress(progress_percent)
    
    remaining = savings_goal - balance
    if remaining > 0:
        st.info(f"💡 目標まであと **{remaining:,}円** です！")
    else:
        st.success(f"🎉 目標達成おめでとう！ {balance - savings_goal:,}円も多く貯まってるよ！")
        st.balloons()

st.markdown("---")

# 入力エリア
col_left, col_right = st.columns([1, 2])

# 左側：入力フォーム
with col_left:
    st.subheader("📝 記録を追加")
    
    with st.form("add_transaction", clear_on_submit=True):
        transaction_type = st.radio(
            "種類",
            ["収入", "支出"],
            horizontal=True,
            help="お小遣いをもらったら「収入」、使ったら「支出」"
        )
        
        amount = st.number_input(
            "💴 金額（円）",
            min_value=0,
            value=100,
            step=50
        )
        
        if transaction_type == "収入":
            category = st.selectbox(
                "カテゴリー",
                ["お小遣い", "お年玉", "お手伝い", "プレゼント", "その他"]
            )
        else:
            category = st.selectbox(
                "カテゴリー",
                ["お菓子", "おもちゃ", "本・漫画", "ゲーム", "文房具", "貯金", "その他"]
            )
        
        memo = st.text_input(
            "メモ",
            placeholder="例：おばあちゃんからもらった、ガチャガチャ",
            help="何のお金か簡単にメモ"
        )
        
        submit = st.form_submit_button(
            "➕ 記録する",
            use_container_width=True,
            type="primary"
        )
        
        if submit:
            transaction = {
                "日付": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "種類": transaction_type,
                "カテゴリー": category,
                "金額": amount if transaction_type == "収入" else -amount,
                "メモ": memo if memo else "-"
            }
            
            st.session_state.transactions.insert(0, transaction)
            
            if transaction_type == "収入":
                st.success(f"✅ {amount:,}円の収入を記録しました！")
            else:
                st.success(f"✅ {amount:,}円の支出を記録しました！")
            
            st.rerun()

# 右側：履歴とグラフ
with col_right:
    tab1, tab2 = st.tabs(["📋 履歴", "📊 グラフ"])
    
    # タブ1：履歴
    with tab1:
        st.subheader("📋 おこづかいの履歴")
        
        if len(st.session_state.transactions) == 0:
            st.info("📭 まだ記録がありません。左側から記録を追加してください。")
        else:
            for idx, transaction in enumerate(st.session_state.transactions):
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 2, 1])
                    
                    with col_a:
                        if transaction['種類'] == '収入':
                            st.markdown(f"**📥 {transaction['カテゴリー']}**")
                            st.caption(f"💴 +{abs(transaction['金額']):,}円")
                        else:
                            st.markdown(f"**📤 {transaction['カテゴリー']}**")
                            st.caption(f"💸 -{abs(transaction['金額']):,}円")
                    
                    with col_b:
                        st.caption(f"📅 {transaction['日付']}")
                        if transaction['メモ'] != "-":
                            st.caption(f"📝 {transaction['メモ']}")
                    
                    with col_c:
                        if st.button("🗑️", key=f"del_{idx}"):
                            st.session_state.transactions.pop(idx)
                            st.rerun()
                    
                    st.divider()
    
    # タブ2：グラフ
    with tab2:
        st.subheader("📊 お金の使い方グラフ")
        
        if len(st.session_state.transactions) == 0:
            st.info("📭 記録がないのでグラフを表示できません。")
        else:
            # 支出のみ抽出
            expenses = [t for t in st.session_state.transactions if t['種類'] == '支出']
            
            if len(expenses) == 0:
                st.info("💡 まだ支出の記録がありません。")
            else:
                # カテゴリー別集計
                df = pd.DataFrame(expenses)
                df['金額_abs'] = df['金額'].abs()
                
                category_sum = df.groupby('カテゴリー')['金額_abs'].sum().reset_index()
                category_sum = category_sum.sort_values('金額_abs', ascending=False)
                
                # 円グラフ
                fig = px.pie(
                    category_sum,
                    values='金額_abs',
                    names='カテゴリー',
                    title='何に使ったか（カテゴリー別）',
                    hole=0.3
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
                
                # 棒グラフ
                fig2 = px.bar(
                    category_sum,
                    x='カテゴリー',
                    y='金額_abs',
                    title='カテゴリー別の支出金額',
                    labels={'金額_abs': '金額（円）', 'カテゴリー': 'カテゴリー'}
                )
                st.plotly_chart(fig2, use_container_width=True)

# 下部：CSV出力
st.markdown("---")

if len(st.session_state.transactions) > 0:
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        df_export = pd.DataFrame(st.session_state.transactions)
        csv = df_export.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📥 CSVでダウンロード",
            data=csv,
            file_name=f"{child_name}_おこづかい帳.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        total_count = len(st.session_state.transactions)
        st.info(f"📊 記録数: {total_count}件")

# フッター
st.markdown("---")
st.caption("💡 ヒント: お小遣いをもらったり使ったりしたら、すぐに記録する習慣をつけよう！")
st.caption(f"Created with ❤️ for {child_name}")
