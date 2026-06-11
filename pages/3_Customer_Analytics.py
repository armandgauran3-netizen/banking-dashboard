import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():

    transactions = pd.read_csv(
        "data/FactTransaction.csv",
        parse_dates=["TransactionDate"]
    )

    accounts = pd.read_csv(
        "data/DimAccount.csv",
        parse_dates=["OpenDate", "ClosedDate"]
    )

    customers = pd.read_csv(
        "data/DimCustomer.csv",
        parse_dates=["DOB", "JoinDate"],
        dayfirst=True
    )

    return transactions, accounts, customers


transactions, accounts, customers = load_data()

# =========================
# DATA PREPARATION
# =========================

df = (
    transactions
    .merge(accounts, on="AccountID", how="left")
    .merge(customers, on="CustomerID", how="left")
)

today = pd.Timestamp.today()

df["Age"] = (
    (today - df["DOB"]).dt.days / 365.25
).astype(int)

df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=[0, 25, 35, 45, 55, 65, 120],
    labels=[
        "18-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "65+"
    ]
)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("🔎 Filters")

regions = sorted(df["Region"].dropna().unique())
genders = sorted(df["Gender"].dropna().unique())
statuses = sorted(df["Status_y"].dropna().unique())

min_date = df["TransactionDate"].min()
max_date = df["TransactionDate"].max()
date_range = st.sidebar.date_input(
    "Transaction period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])

selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

selected_genders = st.sidebar.multiselect(
    "Gender",
    genders,
    default=genders
)

selected_status = st.sidebar.multiselect(
    "Customer Status",
    statuses,
    default=statuses
)

df = df[
    (df["Region"].isin(selected_regions))
    &
    (df["Gender"].isin(selected_genders))
    &
    (df["Status_y"].isin(selected_status))
    &
    (df["TransactionDate"] >= pd.to_datetime(date_range[0])) &
    (df["TransactionDate"] <= pd.to_datetime(date_range[1]))
]

# =========================
# TITLE
# =========================

st.title("👥 Customer Analytics")

# =========================
# KPI
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Customers",
    df["CustomerID"].nunique()
)

col2.metric(
    "Transactions",
    len(df)
)

col3.metric(
    "Avg Customer Age",
    round(df["Age"].mean(), 1)
)

col4.metric(
    "Avg Balance",
    f"${df['Balance'].mean():,.0f}"
)

st.divider()

# =========================
# SPENDING BY REGION
# =========================

col1, col2 = st.columns(2)

with col1:

    spending_region = (
        df[df["TransactionAmount"] < 0]
        .groupby("Region")["TransactionAmount"]
        .sum()
        .abs()
        .reset_index()
        .sort_values("TransactionAmount", ascending=False)
    )

    fig = px.bar(
        spending_region,
        x="Region",
        y="TransactionAmount",
        title="Total Spending by Region",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# SPENDING BY GENDER
# =========================

with col2:

    spending_gender = (
        df[df["TransactionAmount"] < 0]
        .groupby("Gender")["TransactionAmount"]
        .sum()
        .abs()
        .reset_index()
    )

    fig = px.pie(
        spending_gender,
        names="Gender",
        values="TransactionAmount",
        title="Spending by Gender",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# AGE DISTRIBUTION
# =========================

col1, col2 = st.columns(2)

with col1:

    fig = px.histogram(
        df.drop_duplicates("CustomerID"),
        x="Age",
        nbins=25,
        title="Customer Age Distribution",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# SPENDING BY AGE GROUP
# =========================

with col2:

    age_spending = (
        df[df["TransactionAmount"] < 0]
        .groupby("AgeGroup")["TransactionAmount"]
        .mean()
        .abs()
        .reset_index()
    )

    fig = px.bar(
        age_spending,
        x="AgeGroup",
        y="TransactionAmount",
        title="Average Spending by Age Group",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# CUSTOMER ACTIVITY
# =========================

customer_stats = (
    df.groupby(
        [
            "CustomerID",
            "Gender",
            "Region"
        ]
    )
    .agg(
        TotalSpent=(
            "TransactionAmount",
            lambda x: abs(x[x < 0].sum())
        ),
        TransactionCount=(
            "TransactionID",
            "count"
        )
    )
    .reset_index()
)

fig = px.scatter(
    customer_stats,
    x="TransactionCount",
    y="TotalSpent",
    color="Gender",
    hover_data=["Region"],
    title="Customer Spending vs Activity",
    opacity=0.6,
    template="plotly"
)

fig.update_traces(
    marker=dict(size=8)
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# CUSTOMER TABLE
# =========================

st.subheader("Customer Details")

customer_table = (
    df[
        [
            "CustomerID",
            "FullName",
            "Gender",
            "Age",
            "Region",
            "Balance"
        ]
    ]
    .drop_duplicates()
)

st.dataframe(
    customer_table,
    use_container_width=True,
    hide_index=True
)