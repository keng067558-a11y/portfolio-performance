import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# --- 設定網頁 ---
st.set_page_config(page_title="全自動資產儀表板", layout="wide")
st.title("📈 專業自動化資產儀表板")
st.caption("數據來源：Yahoo Finance | 資料儲存：GitHub CSV")

# --- 讀取資料與抓取股價函數 ---
@st.cache_data(ttl=60)  # 設定快取 60 秒，避免重複一直抓
def load_data():
    # 1. 讀取 GitHub 上的 portfolio.csv
    try:
        # 這裡讀取的是你專案裡的 CSV 檔案
        df = pd.read_csv("portfolio.csv")
    except Exception as e:
        st.error("找不到 portfolio.csv 檔案，請確認 GitHub 上有建立此檔案。")
        return pd.DataFrame()

    # 2. 準備抓取即時股價
    current_prices = []
    market_values = []
    profits = []
    rois = []

    # 建立進度條
    progress_bar = st.progress(0)
    total_items = len(df)

    for index, row in df.iterrows():
        symbol = row['Symbol']
        cost = row['AvgCost']
        qty = row['Quantity']
        
        # 使用 yfinance 抓取價格
        try:
            ticker = yf.Ticker(symbol)
            # 抓取最新一日的資料
            history = ticker.history(period="1d")
            
            if not history.empty:
                # 取得最新收盤價
                price = history['Close'].iloc[-1]
            else:
                price = cost # 抓不到就用成本價暫代
                
        except Exception:
            price = cost # 發生錯誤也用成本價暫代

        # 計算數值
        m_value = price * qty
        profit = (price - cost) * qty
        roi = (profit / (cost * qty)) * 100 if cost > 0 else 0

        current_prices.append(price)
        market_values.append(m_value)
        profits.append(profit)
        rois.append(roi)
        
        # 更新進度條
        progress_bar.progress((index + 1) / total_items)

    # 清除進度條
    progress_bar.empty()

    # 將計算結果放回表格
    df['Current Price'] = current_prices
    df['Market Value'] = market_values
    df['Profit/Loss'] = profits
    df['ROI (%)'] = rois
    
    return df

# --- 主程式邏輯 ---

# 側邊欄說明
with st.sidebar:
    st.header("⚙️ 設定與說明")
    st.info("本系統會自動從 Yahoo Finance 抓取最新股價。")
    st.markdown("""
    **如何新增資產？**
    請直接在 GitHub 修改 `portfolio.csv` 檔案。
    
    **代號規則：**
    - 🇹🇼 台股：`2330.TW`
    - 🇺🇸 美股：`NVDA`, `AAPL`
    - 🪙 加密貨幣：`BTC-USD`, `ETH-USD`
    """)
    
    if st.button("🔄 立即更新股價"):
        st.cache_data.clear()
        st.rerun()

# 載入資料
df = load_data()

if not df.empty:
    # 1. 顯示總體指標
    total_cost = (df['Quantity'] * df['AvgCost']).sum()
    total_value = df['Market Value'].sum()
    total_pl = df['Profit/Loss'].sum()
    total_roi = (total_pl / total_cost * 100) if total_cost > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 總資產市值", f"${total_value:,.0f}")
    col2.metric("📦 總投入成本", f"${total_cost:,.0f}")
    col3.metric("💵 未實現損益", f"${total_pl:,.0f}", delta_color="normal" if total_pl >= 0 else "inverse")
    col4.metric("🚀 總報酬率", f"{total_roi:.2f}%", delta_color="normal" if total_roi >= 0 else "inverse")

    st.markdown("---")

    # 2. 圖表分析
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 資產配置 (依市值)")
        # 依照資產類型畫圓餅圖
        fig_pie = px.pie(df, values='Market Value', names='Type', hole=0.4, title="各類資產佔比")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.subheader("🏆 個股績效排行 (依損益)")
        # 依照賺錢金額排序
        df_sorted = df.sort_values(by='Profit/Loss', ascending=False)
        fig_bar = px.bar(df_sorted, x='Symbol', y='Profit/Loss', color='Profit/Loss', 
                         color_continuous_scale=['red', 'gray', 'green'], title="個股損益長條圖")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. 詳細報表
    st.subheader("📋 資產詳細清單 (即時更新)")
    
    # 格式化顯示
    st.dataframe(
        df.style.format({
            "AvgCost": "{:,.2f}",
            "Current Price": "{:,.2f}",
            "Market Value": "{:,.0f}",
            "Profit/Loss": "{:,.0f}",
            "ROI (%)": "{:.2f}%"
        }).background_gradient(subset=["ROI (%)"], cmap="RdYlGn", vmin=-20, vmax=20),
        use_container_width=True
    )

else:
    st.warning("目前沒有資料，請檢查 GitHub 上的 portfolio.csv 檔案。")
