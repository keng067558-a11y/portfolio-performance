import streamlit as st
import pandas as pd
import plotly.express as px

# --- 設定網頁標題與版面 ---
st.set_page_config(page_title="專業投資資產儀表板", layout="wide")

st.title("💰 年度投資績效儀表板")
st.markdown("### 追蹤您的台股、美股與加密貨幣資產")

# --- 初始化 Session State (暫存資料) ---
if 'assets' not in st.session_state:
    st.session_state.assets = []

# --- 側邊欄：新增資產 ---
with st.sidebar:
    st.header("➕ 新增資產")
    
    asset_type = st.selectbox("資產類別", ["🇹🇼 台股", "🇺🇸 美股", "🪙 加密貨幣"])
    symbol = st.text_input("代號 (例如: 2330, NVDA, BTC)").upper()
    quantity = st.number_input("持有股數/顆數", min_value=0.0, step=0.01, format="%.2f")
    avg_cost = st.number_input("平均成本 (單價)", min_value=0.0, step=0.1, format="%.2f")
    current_price = st.number_input("目前市價 (單價)", min_value=0.0, step=0.1, format="%.2f")
    
    if st.button("新增資產"):
        if symbol and quantity > 0:
            new_asset = {
                "Type": asset_type,
                "Symbol": symbol,
                "Quantity": quantity,
                "Avg Cost": avg_cost,
                "Current Price": current_price,
                "Total Cost": quantity * avg_cost,
                "Market Value": quantity * current_price,
                "Profit/Loss": (current_price - avg_cost) * quantity,
                "ROI (%)": ((current_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0
            }
            st.session_state.assets.append(new_asset)
            st.success(f"已新增 {symbol}")
        else:
            st.error("請輸入正確的代號與數量")

    if st.button("🗑️ 清除所有資料"):
        st.session_state.assets = []
        st.rerun()

# --- 主畫面：數據展示 ---
if len(st.session_state.assets) > 0:
    df = pd.DataFrame(st.session_state.assets)
    
    # 1. 關鍵指標
    total_cost = df["Total Cost"].sum()
    total_value = df["Market Value"].sum()
    total_pl = df["Profit/Loss"].sum()
    total_roi = (total_pl / total_cost * 100) if total_cost > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總資產市值", f"${total_value:,.0f}")
    col2.metric("總投入成本", f"${total_cost:,.0f}")
    col3.metric("未實現損益", f"${total_pl:,.0f}", delta_color="normal" if total_pl >= 0 else "inverse")
    col4.metric("總報酬率 ROI", f"{total_roi:.2f}%", delta_color="normal" if total_roi >= 0 else "inverse")
    
    st.markdown("---")

    # 2. 圖表
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("📊 資產配置")
        fig_pie = px.pie(df, values='Market Value', names='Type', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_chart2:
        st.subheader("📈 個股佔比")
        fig_bar = px.bar(df, x='Symbol', y='Market Value', color='Type', text_auto='.2s')
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. 清單
    st.subheader("📋 詳細清單")
    st.dataframe(df.style.format({"Quantity": "{:.2f}", "Avg Cost": "{:,.2f}", "Current Price": "{:,.2f}", "Total Cost": "{:,.0f}", "Market Value": "{:,.0f}", "Profit/Loss": "{:,.0f}", "ROI (%)": "{:.2f}%"}), use_container_width=True)
else:
    st.info("👈 請從左側新增您的第一筆資產")
