import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="Olist Shipping Delay & Customer Satisfaction", layout="wide")

sns.set(style="whitegrid")

DATA_DIR = Path(__file__).resolve().parent / "datasets"


@st.cache_data(show_spinner=False)
def load_data() -> dict:
    orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
    reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")
    customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")

    date_cols = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    orders["delivery_delay_days"] = (
        orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
    ).dt.days

    orders["is_late"] = np.where(
        orders["delivery_delay_days"].notna(),
        (orders["delivery_delay_days"] > 0).astype(int),
        np.nan,
    )

    data = (
        orders.merge(reviews, on="order_id", how="left").merge(
            customers, on="customer_id", how="left"
        )
    )

    # Keep rows with review_score for satisfaction analysis
    data = data.dropna(subset=["review_score"]).copy()

    # Convenience slices
    valid_delay = data["delivery_delay_days"].replace([np.inf, -np.inf], np.nan).dropna()
    valid_is_late = data.dropna(subset=["is_late"]).copy()

    return {
        "orders": orders,
        "reviews": reviews,
        "customers": customers,
        "data": data,
        "valid_delay": valid_delay,
        "valid_is_late": valid_is_late,
    }


st.title("Analisis Keterlambatan Pengiriman & Dampaknya terhadap Kepuasan Pelanggan")

st.markdown(
    """
Dashboard ini merangkum insight utama dari dataset Olist terkait keterlambatan pengiriman dan hubungannya dengan kepuasan pelanggan (diukur melalui `review_score`).

Definisi singkat:
- `delivery_delay_days` = tanggal sampai ke pelanggan − tanggal estimasi (positif = terlambat, negatif = lebih cepat)
- `is_late` = 1 jika `delivery_delay_days` > 0, 0 jika tidak (NaN bila tanggal tidak lengkap)
"""
)

with st.spinner("Memuat data..."):
    d = load_data()

data = d["data"]
valid_delay = d["valid_delay"]
valid_is_late = d["valid_is_late"]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total order (dengan review)", f"{len(data):,}")

with col2:
    late_rate = valid_is_late["is_late"].mean() if len(valid_is_late) else np.nan
    st.metric("Rasio terlambat", f"{late_rate * 100:.1f}%" if pd.notna(late_rate) else "-")

with col3:
    avg_delay_late = (
        valid_is_late.loc[valid_is_late["is_late"] == 1, "delivery_delay_days"].mean()
        if len(valid_is_late)
        else np.nan
    )
    st.metric(
        "Rata-rata keterlambatan (hari)",
        f"{avg_delay_late:.1f}" if pd.notna(avg_delay_late) else "-",
    )

with col4:
    st.metric("Rata-rata review score", f"{data['review_score'].mean():.2f}")

st.divider()

# --- Main visuals ---
left, right = st.columns(2)

with left:
    st.subheader("Pengaruh keterlambatan terhadap review score")
    fig, ax = plt.subplots(figsize=(6, 4))
    if len(valid_is_late) == 0:
        st.info("Data tidak cukup untuk menampilkan perbandingan tepat waktu vs terlambat.")
    else:
        sns.boxplot(x="is_late", y="review_score", data=valid_is_late, ax=ax)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Tepat Waktu", "Terlambat"])
        ax.set_xlabel("")
        ax.set_title("Review Score: Tepat Waktu vs Terlambat")
    st.pyplot(fig, clear_figure=True)

with right:
    st.subheader("Distribusi hari keterlambatan")
    fig, ax = plt.subplots(figsize=(6, 4))
    if len(valid_delay) == 0:
        st.info("Data tidak cukup untuk menampilkan distribusi keterlambatan.")
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning, module="seaborn")
            sns.histplot(valid_delay, bins=30, kde=True, ax=ax)
        ax.set_title("Distribusi Delivery Delay (hari)")
        ax.set_xlabel("Hari (positif = terlambat)")
    st.pyplot(fig, clear_figure=True)

left2, right2 = st.columns(2)

with left2:
    st.subheader("Distribusi skor ulasan")
    fig, ax = plt.subplots(figsize=(6, 4))
    order_scores = sorted(data["review_score"].dropna().unique())
    sns.countplot(x="review_score", data=data, ax=ax, order=order_scores)
    ax.set_title("Distribusi Review Score")
    ax.set_xlabel("Review Score")
    st.pyplot(fig, clear_figure=True)

with right2:
    st.subheader("Rasio keterlambatan per provinsi (Top 10)")
    if len(valid_is_late) == 0:
        st.info("Data tidak cukup untuk menghitung rasio keterlambatan per provinsi.")
    else:
        late_by_state = (
            valid_is_late.groupby("customer_state")["is_late"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
        )
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=late_by_state.values, y=late_by_state.index, ax=ax)
        ax.set_xlabel("Rasio Terlambat")
        ax.set_ylabel("Provinsi")
        ax.set_title("Top 10 Provinsi dengan Rasio Terlambat Tertinggi")
        st.pyplot(fig, clear_figure=True)

st.divider()

# --- Insights summary ---
st.subheader("Ringkasan Insight")

st.markdown(
    """
1. **Keterlambatan pengiriman berkorelasi dengan penurunan kepuasan pelanggan.** Pesanan yang terlambat cenderung memiliki `review_score` lebih rendah dibanding pesanan yang tepat waktu.
2. **Mayoritas pesanan berada dekat 0 hari keterlambatan**, namun terdapat sebagian kecil pesanan dengan keterlambatan yang cukup ekstrem (ekor distribusi).
3. **Rasio keterlambatan berbeda antar provinsi**, sehingga bisa menjadi titik awal investigasi operasional/logistik di wilayah tertentu.
"""
)

st.caption("Catatan: dashboard ini fokus pada insight analitik; optimasi model ML tidak menjadi fokus utama.")
