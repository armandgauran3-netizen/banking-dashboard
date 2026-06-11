import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.sidebar.title("🔎 Filters")

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

    #Erreur de consistance des données : les transactions n'ont pas de type (crédit/débit)
    transactions["TransactionType"] = transactions.apply(
    lambda row: "Credit" if row["TransactionAmount"] > 0 else "Debit",
    axis=1
)
    transactions["TransactionAmount_Abs"] = transactions["TransactionAmount"].abs()

    return transactions, accounts

transactions, accounts = load_data()


#SIDE BAR - Date filter

transactions["TransactionDate"] = pd.to_datetime(transactions["TransactionDate"])

min_date = transactions["TransactionDate"].min()
max_date = transactions["TransactionDate"].max()

date_range = st.sidebar.date_input(
    "Transaction period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

transaction_types = transactions["TransactionType"].dropna().unique()

selected_types = st.sidebar.multiselect(
    "Transaction Type",
    options=transaction_types,
    default=transaction_types
)

min_amt = float(transactions["TransactionAmount"].min())
max_amt = float(transactions["TransactionAmount"].max())

amount_range = st.sidebar.slider(
    "Transaction Amount",
    min_value=min_amt,
    max_value=max_amt,
    value=(min_amt, max_amt)
)

#Aplication des filtres
filtered_transactions = transactions[
    (transactions["TransactionDate"] >= pd.to_datetime(date_range[0])) &
    (transactions["TransactionDate"] <= pd.to_datetime(date_range[1])) &
    (transactions["TransactionType"].isin(selected_types)) &
    (transactions["TransactionAmount"].between(amount_range[0], amount_range[1]))
]

#FIN SIDE BAR

st.title("📊 Banking Overview")

total_accounts = accounts["AccountID"].nunique()
open_accounts = (accounts["Status"] == "Open").sum()
total_balance = accounts["Balance"].sum()
total_transactions = len(filtered_transactions)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Accounts", f"{total_accounts:,}")
col2.metric("Open Accounts", f"{open_accounts:,}")
col3.metric("Total Balance", f"€{total_balance:,.0f}")
col4.metric("Transactions", f"{total_transactions:,}")

st.divider()

import plotly.graph_objects as go
import pandas as pd

# --- Month ---
transactions["Month"] = (
    transactions["TransactionDate"]
    .dt.to_period("M")
    .astype(str)
)
filtered_transactions["Month"] = (
    filtered_transactions["TransactionDate"]
    .dt.to_period("M")
    .astype(str)
)

# --- Aggregation ---
filtered_monthly = filtered_transactions.groupby("Month").agg(
    total_positive=("TransactionAmount", lambda x: x[x > 0].sum()),
    total_negative=("TransactionAmount", lambda x: x[x < 0].sum()),
    net=("TransactionAmount", "sum")
).reset_index()

monthly = transactions.groupby("Month").agg(
    total_positive=("TransactionAmount", lambda x: x[x > 0].sum()),
    total_negative=("TransactionAmount", lambda x: x[x < 0].sum()),
    net=("TransactionAmount", "sum")
).reset_index()

# --- Figure ---
fig = go.Figure()

# 🟢 Positive cash flow
fig.add_trace(go.Bar(
    x=filtered_monthly["Month"],
    y=filtered_monthly["total_positive"],
    name="Inflows (+)",
    marker_color="green"
))

# 🔴 Negative cash flow
fig.add_trace(go.Bar(
    x=filtered_monthly["Month"],
    y=filtered_monthly["total_negative"],
    name="Outflows (-)",
    marker_color="red"
))

# ⚫ Net line
fig.add_trace(go.Scatter(
    x=filtered_monthly["Month"],#On filtre en x pour avoir une ligne qui correspond à la période sélectionnée
    y=monthly["net"], #Mais on ne peut pas filtrer en y sinon le net perd son sens
    name="Net Flow",
    mode="lines",
    line=dict(color="black", width=2)
))

# --- Layout ---
fig.update_layout(
    title="Monthly Cash Flow (Inflows / Outflows / Net)",
    barmode="relative",
    template="plotly",
    yaxis_title="Amount",
    xaxis_title="Month"
)

# Zero line (important visuellement)
fig.add_hline(y=0, line_width=1, line_color="gray")

st.plotly_chart(fig, use_container_width=True)


st.divider()

col1, col2 = st.columns(2)

with col1:
    type_dist = (
        transactions.groupby("TransactionType")
        ["TransactionAmount_Abs"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        type_dist,
        names="TransactionType",
        values="TransactionAmount_Abs",
        title="Credit vs Debit",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    status_dist = (
        transactions["Status"]
        .value_counts()
        .reset_index()
    )

    fig = px.bar(
        status_dist,
        x="Status",
        y="count",
        title="Transaction Status",
        template="plotly"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

col1, col2 = st.columns(2)

with col1:

    channel = (
            filtered_transactions.groupby("TransactionChannel")
            ["TransactionAmount"]
            .sum()
            .reset_index()
        )

    fig = px.pie(
            channel,
            names="TransactionChannel",
            values="TransactionAmount",
            title="Volume by Channel",
            template="plotly"
        )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
    filtered_transactions,
    x="TransactionAmount",
    nbins=30,
    template="plotly",
    title="Transaction Amount Distribution"
    )



    st.plotly_chart(fig, use_container_width=True)

st.subheader("Transactions Detail")

st.dataframe(
    filtered_transactions,
    use_container_width=True,
    hide_index=True
)