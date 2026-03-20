import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from database import get_connection
from database_neo4j import get_neo4j_connection
from queries import *
from neo4j_queries import *

st.set_page_config(page_title="NoSQL - MongoDB & Neo4j", layout="wide")
st.title("Exploration de la base Films")

col = get_connection()
driver = get_neo4j_connection()

st.sidebar.title("Questions")
section = st.sidebar.selectbox("Base de données", ["MongoDB (Q1-Q13)", "Neo4j (Q14-Q26)"])

if section == "MongoDB (Q1-Q13)":
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
else:
    question = st.sidebar.radio("Choisir une question", [
        "Q14 - Acteur avec le plus de films",
        "Q15 - Acteurs avec Anne Hathaway",
        "Q16 - Acteur avec le plus de revenus",
        "Q17 - Moyenne des votes",
        "Q18 - Genre le plus représenté",
        "Q19 - Films des membres du groupe",
        "Q20 - Réalisateur avec le plus d'acteurs",
        "Q21 - Films les plus connectés",
        "Q22 - Acteurs avec le plus de réalisateurs",
        "Q23 - Recommandation de film",
        "Q24 - Relations INFLUENCE_PAR",
        "Q25 - Chemin le plus court",
        "Q26 - Communautés d'acteurs",
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

elif question == "Q6 - Film le plus rentable":
    st.header("Q6 - Film avec le plus de revenus")
    film = q6_highest_revenue_film(col)
    st.metric("Film", film["title"])
    st.metric("Revenu", f"${film['Revenue (Millions)']:.2f}M")
    st.write(f"**Réalisateur :** {film['Director']} | **Année :** {film['year']}")

elif question == "Q7 - Réalisateurs prolifiques":
    st.header("Q7 - Réalisateurs avec plus de 5 films")
    df = q7_directors_more_than_5(col)
    if df.empty:
        st.warning("Aucun réalisateur avec plus de 5 films.")
    else:
        st.dataframe(df)
        fig, ax = plt.subplots()
        ax.barh(df["Réalisateur"], df["Nombre de films"], color="steelblue")
        st.pyplot(fig)

elif question == "Q8 - Genre le plus rentable":
    st.header("Q8 - Revenu moyen par genre")
    df = q8_genre_most_revenue(col)
    st.write(f"**Genre le plus rentable : {df.iloc[0]['Genre']}** (${df.iloc[0]['Revenu moyen (M$)']:.2f}M)")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df["Genre"], df["Revenu moyen (M$)"], color="steelblue")
    ax.set_xlabel("Revenu moyen (M$)")
    st.pyplot(fig)

elif question == "Q9 - Top 3 par décennie":
    st.header("Q9 - Top 3 films par décennie (Metascore)")
    df = q9_top3_per_decade(col)
    for decade in df["Décennie"].unique():
        st.subheader(f"Décennie {decade}")
        st.dataframe(df[df["Décennie"] == decade][["Titre", "Année", "Metascore"]].reset_index(drop=True))

elif question == "Q10 - Film le plus long par genre":
    st.header("Q10 - Film le plus long par genre")
    df = q10_longest_film_per_genre(col)
    st.dataframe(df)

elif question == "Q11 - Vue MongoDB":
    st.header("Q11 - Vue : Metascore > 80 ET Revenue > 50M")
    if st.button("Créer la vue"):
        q11_create_view(col)
        st.success("Vue créée !")
    df = q11_get_view(col)
    if not df.empty:
        st.dataframe(df)

elif question == "Q12 - Corrélation Runtime/Revenue":
    st.header("Q12 - Corrélation durée vs revenu")
    result = q12_correlation(col)
    df = result["df"]
    corr = result["corr"]
    st.metric("Coefficient de corrélation (Pearson)", corr)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df["runtime"], df["revenue"], alpha=0.6)
    slope, intercept, _, _, _ = stats.linregress(df["runtime"], df["revenue"])
    x = np.linspace(df["runtime"].min(), df["runtime"].max(), 100)
    ax.plot(x, slope * x + intercept, color="red", label=f"r = {corr}")
    ax.set_xlabel("Durée (min)")
    ax.set_ylabel("Revenu (M$)")
    ax.legend()
    st.pyplot(fig)

elif question == "Q13 - Durée moyenne par décennie":
    st.header("Q13 - Évolution durée moyenne par décennie")
    df = q13_avg_runtime_per_decade(col)
    st.dataframe(df)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Décennie"], df["Durée moyenne (min)"], marker="o", color="steelblue")
    ax.set_xlabel("Décennie")
    ax.set_ylabel("Durée moyenne (min)")
    st.pyplot(fig)

# ── NEO4J ─────────────────────────────────────────────────────────────────────

elif question == "Q14 - Acteur avec le plus de films":
    st.header("Q14 - Acteur ayant joué dans le plus de films")
    r = q14_actor_most_films(driver)
    if r:
        st.metric("Acteur", r["acteur"])
        st.metric("Nombre de films", r["nb_films"])

elif question == "Q15 - Acteurs avec Anne Hathaway":
    st.header("Q15 - Acteurs ayant joué avec Anne Hathaway")
    acteurs = q15_actors_with_anne_hathaway(driver)
    if acteurs:
        st.write(f"**{len(acteurs)} acteur(s) trouvé(s) :**")
        for a in acteurs:
            st.write(f"- {a}")
    else:
        st.warning("Anne Hathaway n'est pas dans la base ou n'a joué avec personne.")

elif question == "Q16 - Acteur avec le plus de revenus":
    st.header("Q16 - Acteur dont les films totalisent le plus de revenus")
    r = q16_actor_most_revenue(driver)
    if r:
        st.metric("Acteur", r["acteur"])
        st.metric("Revenus cumulés", f"${r['total_revenus']:,.0f}M")

elif question == "Q17 - Moyenne des votes":
    st.header("Q17 - Moyenne des votes (Neo4j)")
    r = q17_avg_votes(driver)
    if r:
        st.metric("Moyenne des votes", f"{r['moyenne_votes']:,.0f}")

elif question == "Q18 - Genre le plus représenté":
    st.header("Q18 - Genre le plus représenté dans Neo4j")
    r = q18_most_common_genre(driver)
    if r:
        st.metric("Genre", r["genre"])
        st.metric("Nombre de films", r["nb_films"])

elif question == "Q19 - Films des membres du groupe":
    st.header("Q19 - Films où les membres du groupe ont joué")
    df = q19_group_member_films(driver)
    if df.empty:
        st.warning("Les membres du groupe ne sont liés à aucun film.")
    else:
        st.dataframe(df)

elif question == "Q20 - Réalisateur avec le plus d'acteurs":
    st.header("Q20 - Réalisateur ayant travaillé avec le plus d'acteurs distincts")
    r = q20_director_most_actors(driver)
    if r:
        st.metric("Réalisateur", r["realisateur"])
        st.metric("Nombre d'acteurs distincts", r["nb_acteurs"])

elif question == "Q21 - Films les plus connectés":
    st.header("Q21 - Films les plus connectés (acteurs en commun)")
    df = q21_most_connected_films(driver)
    if not df.empty:
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(df["Film"], df["Films connectés"], color="steelblue")
        ax.set_xlabel("Nombre de films connectés")
        st.pyplot(fig)

elif question == "Q22 - Acteurs avec le plus de réalisateurs":
    st.header("Q22 - 5 acteurs ayant joué avec le plus de réalisateurs différents")
    df = q22_actors_most_directors(driver)
    if not df.empty:
        st.dataframe(df)

elif question == "Q23 - Recommandation de film":
    st.header("Q23 - Recommander un film à un acteur")
    actor_name = st.text_input("Nom de l'acteur", value="Tom Hanks")
    if actor_name:
        df = q23_recommend_film(driver, actor_name)
        if df.empty:
            st.warning(f"Aucune recommandation trouvée pour {actor_name}.")
        else:
            st.write(f"Films recommandés pour **{actor_name}** :")
            st.dataframe(df)

elif question == "Q24 - Relations INFLUENCE_PAR":
    st.header("Q24 - Créer les relations INFLUENCE_PAR entre réalisateurs")
    if st.button("Créer les relations"):
        r = q24_create_influence_relations(driver)
        st.success(f"Relations INFLUENCE_PAR créées !")

elif question == "Q25 - Chemin le plus court":
    st.header("Q25 - Chemin le plus court entre deux acteurs")
    actor1 = st.text_input("Acteur 1", value="Tom Hanks")
    actor2 = st.text_input("Acteur 2", value="Scarlett Johansson")
    if actor1 and actor2:
        r = q25_shortest_path(driver, actor1, actor2)
        if r:
            st.metric("Distance", r["distance"])
            st.write("**Chemin :**")
            st.write(" → ".join(r["chemin"]))
        else:
            st.warning("Aucun chemin trouvé entre ces deux acteurs.")

elif question == "Q26 - Communautés d'acteurs":
    st.header("Q26 - Paires d'acteurs qui collaborent le plus")
    df = q26_actor_communities(driver)
    if not df.empty:
        st.dataframe(df)