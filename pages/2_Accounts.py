import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():

    accounts = pd.read_csv(
        "data/DimAccount.csv",
        parse_dates=["OpenDate", "ClosedDate"]
    )

    customers = pd.read_csv(
        "data/DimCustomer.csv",
        parse_dates=["DOB", "JoinDate"],
        dayfirst=True
    )

    return accounts, customers


accounts, customers = load_data()

# =========================
# MERGE
# =========================

df = accounts.merge(customers, on="CustomerID", how="left")

# Rename pour éviter confusion
df = df.rename(columns={
    "Status_x": "AccountStatus",
    "Status_y": "CustomerStatus"
})

# =========================
# FEATURE ENGINEERING
# =========================

today = pd.Timestamp.today()

df["AccountAgeDays"] = (
    df["ClosedDate"].fillna(today) - df["OpenDate"]
).dt.days

df["Age"] = ((today - df["DOB"]).dt.days / 365.25).astype(int)

df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=[0, 25, 35, 45, 55, 65, 120],
    labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
)

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.title("🔎 Filters")

account_types = sorted(df["AccountType"].dropna().unique())
regions = sorted(df["Region"].dropna().unique())
status = sorted(df["AccountStatus"].dropna().unique())

selected_types = st.sidebar.multiselect(
    "Account Type",
    account_types,
    default=account_types
)

selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

selected_status = st.sidebar.multiselect(
    "Account Status",
    status,
    default=status
)

df = df[
    (df["AccountType"].isin(selected_types)) &
    (df["Region"].isin(selected_regions)) &
    (df["AccountStatus"].isin(selected_status))
]

# =========================
# TITLE
# =========================

st.title("💳 Accounts")

# =========================
# KPI
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Accounts", df["AccountID"].nunique())
col2.metric("Active Accounts", (df["AccountStatus"] == "Open").sum())
col3.metric("Total Balance", f"€{df['Balance'].sum():,.0f}")
col4.metric("Avg Account Age (days)", int(df["AccountAgeDays"].mean()))

st.divider()

# =========================
# ACCOUNT TYPE DISTRIBUTION
# =========================

col1, col2 = st.columns(2)

with col1:

    fig = px.pie(
        df,
        names="AccountType",
        title="Account Type Distribution",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# ACCOUNT STATUS
# =========================

with col2:

    status_df = (
        df["AccountStatus"]
        .value_counts()
        .reset_index()
    )

    fig = px.bar(
        status_df,
        x="AccountStatus",
        y="count",
        title="Account Status Distribution",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# BALANCE vs AGE (IMPORTANT INSIGHT)
# =========================

col1, col2 = st.columns(2)

with col1:

    fig = px.scatter(
        df,
        x="AccountAgeDays",
        y="Balance",
        color="AccountType",
        opacity=0.5,
        title="Balance vs Account Age",
        hover_data=["CustomerID", "Region"],
        template="plotly"
    )

    fig.update_traces(marker=dict(size=7))

    st.plotly_chart(fig, use_container_width=True)

# =========================
# CUSTOMER SEGMENT VIEW
# =========================

with col2:

    region_balance = (
        df.groupby("Region")["Balance"]
        .mean()
        .reset_index()
        .sort_values("Balance", ascending=False)
    )

    fig = px.bar(
        region_balance,
        x="Region",
        y="Balance",
        title="Average Balance by Region",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# AGE IMPACT ON BALANCE
# =========================

age_balance = (
    df.groupby("AgeGroup")["Balance"]
    .mean()
    .reset_index()
)

fig = px.bar(
    age_balance,
    x="AgeGroup",
    y="Balance",
    title="Average Balance by Age Group",
    template="plotly"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# TABLE
# =========================

st.subheader("Detailed Accounts View")

st.dataframe(
    df[
        [
            "AccountID",
            "CustomerID",
            "AccountType",
            "AccountStatus",
            "Region",
            "Balance",
            "AccountAgeDays",
            "Age"
        ]
    ],
    use_container_width=True,
    hide_index=True
)