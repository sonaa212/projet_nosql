import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import json, ast
import pandas as pd
from scipy import stats
import streamlit.components.v1 as components
import tempfile, os
from pyvis.network import Network
from database import get_connection
from database_neo4j import get_neo4j_connection
from queries import *
from neo4j_queries import *

def render_pyvis(net, height=500):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
        net.save_graph(f.name)
        tmp_path = f.name
    with open(tmp_path, "r", encoding="utf-8") as f:
        html = f.read() 
    os.unlink(tmp_path)
    components.html(html, height=height, scrolling=True)

st.set_page_config(page_title="NoSQL - MongoDB & Neo4j", layout="wide")
st.title("Exploration de la base Films")

@st.cache_resource
def get_mongo():
    return get_connection()

@st.cache_resource
def get_neo4j():
    return get_neo4j_connection()

col = get_mongo()
driver = get_neo4j()

st.sidebar.title("Questions")
section = st.sidebar.selectbox("Base de données", [
    "MongoDB (Q1-Q13)",
    "Neo4j (Q14-Q26)",
    "Transversales (Q27-Q30)",
    "Requête libre (MongoDB)"
])

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
elif section == "Neo4j (Q14-Q26)":
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
elif section == "Transversales (Q27-Q30)":
    question = st.sidebar.radio("Choisir une question", [
        "Q27 - Films genres communs, réalisateurs différents",
        "Q28 - Recommandation par acteur",
        "Q29 - Relations CONCURRENT",
        "Q30 - Collaborations réalisateur-acteur",
    ])
else:
    question = None

@st.cache_data
def cached_q1(): return q1_year_most_films(get_mongo())
@st.cache_data
def cached_q2(): return q2_films_after_1999(get_mongo())
@st.cache_data
def cached_q3(): return q3_avg_votes_2007(get_mongo())
@st.cache_data
def cached_q4(): return q4_films_per_year(get_mongo())
@st.cache_data
def cached_q5(): return q5_available_genres(get_mongo())
@st.cache_data
def cached_q6(): return q6_highest_revenue_film(get_mongo())
@st.cache_data
def cached_q7(): return q7_directors_more_than_5(get_mongo())
@st.cache_data
def cached_q8(): return q8_genre_most_revenue(get_mongo())
@st.cache_data
def cached_q9(): return q9_top3_per_decade(get_mongo())
@st.cache_data
def cached_q10(): return q10_longest_film_per_genre(get_mongo())
@st.cache_data
def cached_q11(): return q11_get_view(get_mongo())
@st.cache_data
def cached_q12(): return q12_correlation(get_mongo())
@st.cache_data
def cached_q13(): return q13_avg_runtime_per_decade(get_mongo())

if question == "Q1 - Année record":
    st.header("Q1 - Année avec le plus de films")
    result = cached_q1()
    st.metric("Année", result["_id"])
    st.metric("Nombre de films", result["count"])

elif question == "Q2 - Films après 1999":
    st.header("Q2 - Films sortis après 1999")
    count = cached_q2()
    st.metric("Nombre de films", count)

elif question == "Q3 - Votes moyens 2007":
    st.header("Q3 - Moyenne des votes en 2007")
    avg = cached_q3()
    st.metric("Moyenne des votes", f"{avg:,.0f}")

elif question == "Q4 - Histogramme par année":
    st.header("Q4 - Nombre de films par année")
    df = cached_q4()
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(df["Année"], df["Nombre de films"], color="steelblue")
    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de films")
    ax.set_title("Films par année")
    st.pyplot(fig)

elif question == "Q5 - Genres disponibles":
    st.header("Q5 - Genres disponibles")
    genres = cached_q5()
    st.write(f"**{len(genres)} genres trouvés :**")
    cols = st.columns(4)
    for i, g in enumerate(genres):
        cols[i % 4].write(f"- {g}")

elif question == "Q6 - Film le plus rentable":
    st.header("Q6 - Film avec le plus de revenus")
    film = cached_q6()
    st.metric("Film", film["title"])
    st.metric("Revenu", f"${film['Revenue (Millions)']:.2f}M")
    st.write(f"**Réalisateur :** {film['Director']} | **Année :** {film['year']}")

elif question == "Q7 - Réalisateurs prolifiques":
    st.header("Q7 - Réalisateurs avec plus de 5 films")
    df = cached_q7()
    if df.empty:
        st.warning("Aucun réalisateur avec plus de 5 films.")
    else:
        st.dataframe(df)
        fig, ax = plt.subplots()
        ax.barh(df["Réalisateur"], df["Nombre de films"], color="steelblue")
        st.pyplot(fig)

elif question == "Q8 - Genre le plus rentable":
    st.header("Q8 - Revenu moyen par genre")
    df = cached_q8()
    st.write(f"**Genre le plus rentable : {df.iloc[0]['Genre']}** (${df.iloc[0]['Revenu moyen (M$)']:.2f}M)")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df["Genre"], df["Revenu moyen (M$)"], color="steelblue")
    ax.set_xlabel("Revenu moyen (M$)")
    st.pyplot(fig)

elif question == "Q9 - Top 3 par décennie":
    st.header("Q9 - Top 3 films par décennie (Metascore)")
    df = cached_q9()
    for decade in df["Décennie"].unique():
        st.subheader(f"Décennie {decade}")
        st.dataframe(df[df["Décennie"] == decade][["Titre", "Année", "Metascore"]].reset_index(drop=True))

elif question == "Q10 - Film le plus long par genre":
    st.header("Q10 - Film le plus long par genre")
    st.dataframe(cached_q10())

elif question == "Q11 - Vue MongoDB":
    st.header("Q11 - Vue : Metascore > 80 ET Revenue > 50M")
    if st.button("Créer la vue"):
        q11_create_view(col)
        st.success("Vue créée !")
    df = cached_q11()
    if not df.empty:
        st.dataframe(df)

elif question == "Q12 - Corrélation Runtime/Revenue":
    st.header("Q12 - Corrélation durée vs revenu")
    result = cached_q12()
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
    df = cached_q13()
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
        data = q15_network_data(driver)
        if data:
            net = Network(height="480px", width="100%", bgcolor="#1a1a2e", font_color="white", directed=False)
            net.add_node("Anne Hathaway", color="#e94560", size=35, title="Anne Hathaway")
            films_seen, actors_seen = set(), set()
            for row in data:
                if row["film"] not in films_seen:
                    net.add_node(row["film"], color="#0f3460", size=18, shape="square", title=row["film"])
                    net.add_edge("Anne Hathaway", row["film"], color="#888")
                    films_seen.add(row["film"])
                if row["co_actor"] not in actors_seen:
                    net.add_node(row["co_actor"], color="#16213e", size=15, title=row["co_actor"])
                    actors_seen.add(row["co_actor"])
                net.add_edge(row["film"], row["co_actor"], color="#555")
            net.set_options('{"physics":{"stabilization":{"iterations":100}}}')
            st.subheader("Graphe de co-acteurs")
            render_pyvis(net, height=500)
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
        edges = q21_network_data(driver)
        if edges:
            net = Network(height="500px", width="100%", bgcolor="#1a1a2e", font_color="white")
            all_films = set()
            for e in edges:
                all_films.add(e["film1"]); all_films.add(e["film2"])
            for film in all_films:
                net.add_node(film, color="#e94560", size=20, title=film)
            for e in edges:
                net.add_edge(e["film1"], e["film2"], value=e["acteurs_communs"],
                             title=f"{e['acteurs_communs']} acteur(s) commun(s)")
            net.set_options('{"physics":{"stabilization":{"iterations":80}}}')
            st.subheader("Réseau de films connectés")
            render_pyvis(net, height=520)

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
    edges = q24_influence_network(driver)
    if edges:
        net = Network(height="500px", width="100%", bgcolor="#1a1a2e", font_color="white", directed=True)
        nodes_seen = set()
        for e in edges:
            for name in [e["source"], e["target"]]:
                if name not in nodes_seen:
                    net.add_node(name, color="#0f3460", size=20, title=name)
                    nodes_seen.add(name)
            net.add_edge(e["source"], e["target"], color="#e94560", arrows="to")
        net.set_options('{"physics":{"stabilization":{"iterations":80}}}')
        st.subheader("Réseau INFLUENCE_PAR")
        render_pyvis(net, height=520)
    else:
        st.info("Cliquez sur 'Créer les relations' pour générer le réseau.")

elif question == "Q25 - Chemin le plus court":
    st.header("Q25 - Chemin le plus court entre deux acteurs")
    actor1 = st.text_input("Acteur 1", value="Tom Hanks")
    actor2 = st.text_input("Acteur 2", value="Scarlett Johansson")
    if actor1 and actor2:
        r = q25_shortest_path(driver, actor1, actor2)
        if r:
            st.metric("Distance", r["distance"])
            chemin = [n for n in r["chemin"] if n]
            st.write("**Chemin :** " + " → ".join(chemin))
            net = Network(height="300px", width="100%", bgcolor="#1a1a2e", font_color="white", directed=True)
            for i, node in enumerate(chemin):
                is_actor = (i % 2 == 0)
                net.add_node(node, color="#e94560" if is_actor else "#0f3460",
                             shape="dot" if is_actor else "square",
                             size=25 if is_actor else 18, title=node)
            for i in range(len(chemin) - 1):
                net.add_edge(chemin[i], chemin[i+1], color="#888", arrows="to")
            net.set_options('{"physics":{"enabled":false}}')
            st.subheader("Visualisation du chemin")
            render_pyvis(net, height=320)
        else:
            st.warning("Aucun chemin trouvé entre ces deux acteurs.")

elif question == "Q26 - Communautés d'acteurs":
    st.header("Q26 - Paires d'acteurs qui collaborent le plus")
    df = q26_actor_communities(driver)
    if not df.empty:
        st.dataframe(df)
        net = Network(height="500px", width="100%", bgcolor="#1a1a2e", font_color="white")
        actors_seen = set()
        for _, row in df.iterrows():
            for actor in [row["Acteur 1"], row["Acteur 2"]]:
                if actor not in actors_seen:
                    net.add_node(actor, color="#e94560", size=20, title=actor)
                    actors_seen.add(actor)
            net.add_edge(row["Acteur 1"], row["Acteur 2"],
                         value=int(row["Films en commun"]),
                         title=f"{row['Films en commun']} film(s) en commun",
                         color="#0f3460")
        net.set_options('{"physics":{"stabilization":{"iterations":80}}}')
        st.subheader("Réseau de collaborations")
        render_pyvis(net, height=520)

# ── QUESTIONS TRANSVERSALES ───────────────────────────────────────────────────

elif question == "Q27 - Films genres communs, réalisateurs différents":
    st.header("Q27 - Films avec genres en commun mais réalisateurs différents")
    df = q27_common_genre_diff_director(driver)
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("Aucun résultat trouvé.")

elif question == "Q28 - Recommandation par acteur":
    st.header("Q28 - Recommander des films selon les préférences d'un acteur")
    actor_name = st.text_input("Nom de l'acteur", value="Tom Hanks")
    if actor_name:
        df = q28_recommend_by_actor(driver, actor_name)
        if df.empty:
            st.warning(f"Aucune recommandation trouvée pour {actor_name}.")
        else:
            st.write(f"Films recommandés pour **{actor_name}** :")
            st.dataframe(df)

elif question == "Q29 - Relations CONCURRENT":
    st.header("Q29 - Créer des relations CONCURRENT entre réalisateurs")
    st.write("Relie les réalisateurs ayant fait des films du même genre la même année.")
    if st.button("Créer les relations CONCURRENT"):
        r = q29_create_concurrent_relations(driver)
        st.success(f"Relations CONCURRENT créées !")

elif question == "Q30 - Collaborations réalisateur-acteur":
    st.header("Q30 - Collaborations fréquentes réalisateur-acteur")
    df = q30_director_actor_collabs(driver)
    if not df.empty:
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 5))
        labels = [f"{r} / {a}" for r, a in zip(df["Réalisateur"], df["Acteur"])]
        ax.barh(labels, df["Collaborations"], color="steelblue")
        ax.set_xlabel("Nombre de collaborations")
        ax.set_title("Collaborations les plus fréquentes")
        st.pyplot(fig)
        net = Network(height="520px", width="100%", bgcolor="#1a1a2e", font_color="white")
        directors_seen, actors_seen = set(), set()
        for _, row in df.iterrows():
            if row["Réalisateur"] not in directors_seen:
                net.add_node(row["Réalisateur"], color="#e94560", size=22,
                             shape="diamond", title=f"Réalisateur: {row['Réalisateur']}")
                directors_seen.add(row["Réalisateur"])
            if row["Acteur"] not in actors_seen:
                net.add_node(row["Acteur"], color="#0f3460", size=18,
                             title=f"Acteur: {row['Acteur']}")
                actors_seen.add(row["Acteur"])
            net.add_edge(row["Réalisateur"], row["Acteur"],
                         value=int(row["Collaborations"]),
                         title=f"{row['Collaborations']} film(s) | rev. moy. {row['Revenu moyen (M$)']}M$",
                         color="#16213e")
        net.set_options('{"physics":{"stabilization":{"iterations":80}}}')
        st.subheader("Graphe bipartite réalisateurs / acteurs")
        st.caption("Losanges rouges = réalisateurs | Cercles bleus = acteurs | Épaisseur = nb de collaborations")
        render_pyvis(net, height=540)

# ── REQUÊTE LIBRE MONGODB ─────────────────────────────────────────────────────

elif section == "Requête libre (MongoDB)":
    st.header("Requête libre MongoDB")

    def parse_query(text):
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            pass
        try:
            return ast.literal_eval(text)
        except Exception as e:
            raise ValueError(f"Impossible de parser la requête : {e}")

    operation = st.radio("Opération", ["aggregate", "find"], horizontal=True)

    if operation == "aggregate":
        st.markdown("**Pipeline** (liste de stages JSON, ex: `[{\"$group\": ...}, {\"$sort\": ...}]`)")
        default_pipeline = '[{"$group": {"_id": "$year", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 5}]'
        pipeline_input = st.text_area("Pipeline JSON", value=default_pipeline, height=160)
        limit = st.slider("Limite de résultats", 1, 500, 50)
        if st.button("Exécuter"):
            try:
                pipeline = parse_query(pipeline_input)
                if not isinstance(pipeline, list):
                    st.error("Le pipeline doit être une liste de stages : [{ ... }, { ... }]")
                else:
                    results = list(col.aggregate(pipeline))[:limit]
                    if results:
                        for doc in results:
                            if "_id" in doc and hasattr(doc["_id"], "__iter__") and not isinstance(doc["_id"], str):
                                doc["_id"] = str(doc["_id"])
                        st.success(f"{len(results)} résultat(s)")
                        try:
                            st.dataframe(pd.DataFrame(results))
                        except Exception:
                            st.json(results)
                    else:
                        st.warning("Aucun résultat.")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erreur MongoDB : {e}")

    else:  # find
        st.markdown("**Filtre** (ex: `{\"year\": 2010}`)")
        filter_input = st.text_area("Filtre JSON", value="{}", height=80)
        st.markdown("**Projection** (ex: `{\"title\": 1, \"year\": 1, \"_id\": 0}`)")
        proj_input = st.text_area("Projection JSON", value="{}", height=80)
        limit = st.slider("Limite de résultats", 1, 500, 20)
        if st.button("Exécuter"):
            try:
                filt = parse_query(filter_input)
                proj = parse_query(proj_input)
                results = list(col.find(filt, proj or None).limit(limit))
                if results:
                    for doc in results:
                        doc.pop("_id", None)
                    st.success(f"{len(results)} résultat(s)")
                    try:
                        st.dataframe(pd.DataFrame(results))
                    except Exception:
                        st.json(results)
                else:
                    st.warning("Aucun résultat.")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erreur MongoDB : {e}")