import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from database import get_connection
from queries import *

st.set_page_config(page_title=" NoSQL MongoDB", layout="wide")
st.title(" Exploration de la base Films")

col = get_connection()

st.sidebar.title("Questions")
question = st.sidebar.radio("Choisir une question", [
    "Q1 - Année record",
    "Q2 - Films après 1999",
    "Q3 - Votes moyens 2007",
    "Q4 - Histogramme par année",
    "Q5 - Genres disponibles",
    "Q6 - Film le plus rentable",
    "Q7 - Réalisateurs prolifiques",
    "Q8 - Genre le plus rentable",
    "Q9 - Top 3 par décennie",
    "Q10 - Film le plus long par genre",
    "Q11 - Vue MongoDB",
    "Q12 - Corrélation Runtime/Revenue",
    "Q13 - Durée moyenne par décennie",
])

if question == "Q1 - Année record":
    st.header("Q1 - Année avec le plus de films")
    result = q1_year_most_films(col)
    st.metric("Année", result["_id"])
    st.metric("Nombre de films", result["count"])

elif question == "Q2 - Films après 1999":
    st.header("Q2 - Films sortis après 1999")
    count = q2_films_after_1999(col)
    st.metric("Nombre de films", count)

elif question == "Q3 - Votes moyens 2007":
    st.header("Q3 - Moyenne des votes en 2007")
    avg = q3_avg_votes_2007(col)
    st.metric("Moyenne des votes", f"{avg:,.0f}")

elif question == "Q4 - Histogramme par année":
    st.header("Q4 - Nombre de films par année")
    df = q4_films_per_year(col)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(df["Année"], df["Nombre de films"], color="steelblue")
    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de films")
    ax.set_title("Films par année")
    st.pyplot(fig)

elif question == "Q5 - Genres disponibles":
    st.header("Q5 - Genres disponibles")
    genres = q5_available_genres(col)
    st.write(f"**{len(genres)} genres trouvés :**")
    cols = st.columns(4)
    for i, g in enumerate(genres):
        cols[i % 4].write(f"- {g}")

