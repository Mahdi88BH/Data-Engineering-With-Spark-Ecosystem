import streamlit as st
import pandas as pd
import plotly.express as px
import clickhouse_connect

# --- Config ---
CLICKHOUSE_HOST = "clickhouse"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = "clickhouse"

st.set_page_config(page_title="Flash Sale Performance Dashboard", layout="wide")

# --- Définition AVANT l'appel ---
@st.cache_resource
def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database="oneshop",
    )

# --- Appel APRÈS la définition, protégé par try/except ---
try:
    client = get_clickhouse_client()
except Exception as e:
    st.error(f"❌ Impossible de se connecter à ClickHouse : {e}")
    st.stop()

# --- En-tête ---
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("🛒 Flash Sale [FLASH2025] Performance")
with col_btn:
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# --- KPIs 24h ---
kpi_df = client.query_df("""
    SELECT
        count()                        AS purchases,
        sum(quantity)                  AS units_sold,
        sum(quantity * purchase_price) AS revenue,
        uniq(user_id)                  AS buyers
    FROM oneshop.purchases
    WHERE created_at >= now() - INTERVAL 24 HOUR
""")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Purchases (24h)", f"{int(kpi_df['purchases'][0]):,}")
c2.metric("Units sold",      f"{int(kpi_df['units_sold'][0]):,}")
c3.metric("Revenue",         f"${float(kpi_df['revenue'][0]):,.2f}")
c4.metric("Unique buyers",   f"{int(kpi_df['buyers'][0]):,}")

# --- Ventes par heure ---
st.header("Hourly Sales Volume (Last 24 Hours)")
hourly_df = client.query_df("""
    SELECT
        toStartOfHour(created_at) AS hour,
        SUM(quantity)             AS total_sales
    FROM oneshop.purchases
    WHERE created_at >= now() - INTERVAL 24 HOUR
    GROUP BY hour
    ORDER BY hour ASC
""")
if hourly_df.empty:
    st.info("Pas encore de données dans les dernières 24h.")
else:
    fig = px.bar(
        hourly_df, x="hour", y="total_sales",
        title="Hourly Sales Volume (Past 24 Hours)",
        labels={"hour": "Hour", "total_sales": "Quantity Sold"},
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Top 10 produits ---
st.header("Top 10 Selling Product IDs by Revenue")
top_df = client.query_df("""
    SELECT
        item_id,
        SUM(quantity)                  AS total_quantity,
        SUM(quantity * purchase_price) AS total_revenue
    FROM oneshop.purchases
    GROUP BY item_id
    ORDER BY total_revenue DESC
    LIMIT 10
""")
if top_df.empty:
    st.info("Pas encore de données.")
else:
    top_df["total_revenue"] = top_df["total_revenue"].map(lambda x: f"${x:,.2f}")
    st.dataframe(top_df, use_container_width=True, hide_index=True)

# --- Activité live ---
st.header("Real-time Activity (Last 15 min)")
live_df = client.query_df("""
    SELECT
        toStartOfMinute(_ingested_at) AS minute,
        SUM(quantity)                 AS total_sales
    FROM oneshop.purchases
    WHERE _ingested_at >= now() - INTERVAL 15 MINUTE
    GROUP BY minute
    ORDER BY minute ASC
""")
if live_df.empty:
    st.info("Aucune activité dans les 15 dernières minutes.")
else:
    fig_live = px.line(
        live_df, x="minute", y="total_sales", markers=True,
        title="Live sales per minute (based on ingestion time)",
    )
    st.plotly_chart(fig_live, use_container_width=True)

# --- Dernières transactions ---
st.header("Latest 20 Purchases")
latest_df = client.query_df("""
    SELECT id, user_id, item_id, campaign_id, quantity, purchase_price, created_at
    FROM oneshop.purchases
    ORDER BY _ingested_at DESC
    LIMIT 20
""")
if latest_df.empty:
    st.info("Aucune transaction enregistrée.")
else:
    st.dataframe(latest_df, use_container_width=True, hide_index=True)