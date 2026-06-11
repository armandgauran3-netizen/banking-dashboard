import streamlit as st

st.set_page_config(
    page_title="Banking Analytics",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Banking Analytics Dashboard")

st.markdown("""

Ce projet est un dashboard analytique développé avec Streamlit et Plotly, simulant un environnement bancaire complet. Il permet d’explorer les transactions, comptes et clients afin d’analyser les flux financiers, la performance des comptes et les comportements clients.

Le dashboard est structuré en trois modules : une vue globale des transactions (cash flow, volumes, répartition des opérations), une analyse des comptes (solde, type de compte, ancienneté, segmentation géographique) et une analyse client (profil démographique, dépenses, activité et segmentation).

Les données sont issues de trois tables simulées (transactions, comptes, clients) et modélisées selon une structure en étoile simplifiée. Des jointures permettent de relier les dimensions pour obtenir une analyse complète client–compte–transaction.

Le projet intègre des filtres interactifs (période, région, type de compte, statut, sexe), des KPI dynamiques et des visualisations avancées (bar charts, scatter plots, histogrammes, pie charts) afin de faciliter l’exploration des données.

Ce projet met en avant des compétences en data analysis, data visualization, data modeling et construction de dashboard interactif avec Python.

Source : https://www.kaggle.com/datasets/saidaminsaidaxmadov/financial-transactions/data
            
___

Utilisez le menu de gauche pour naviguer entre :

- 📊 Overview
- 💳 Accounts
- 👥 Customer Analytics

""")