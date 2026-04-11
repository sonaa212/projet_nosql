import pandas as pd

DATABASE = "50c439a6"

# Q14 - Acteur ayant joué dans le plus grand nombre de films
def q14_actor_most_films(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (a:Actor)-[:A_JOUE]->(f:Film)
            RETURN a.name AS acteur, count(f) AS nb_films
            ORDER BY nb_films DESC
            LIMIT 1
        """)
        return result.single()

# Q15 - Acteurs ayant joué dans les mêmes films qu'Anne Hathaway
def q15_actors_with_anne_hathaway(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (anne:Actor {name: "Anne Hathaway"})-[:A_JOUE]->(f:Film)<-[:A_JOUE]-(co:Actor)
            WHERE co.name <> "Anne Hathaway"
            RETURN DISTINCT co.name AS acteur
            ORDER BY acteur
        """)
        return [r["acteur"] for r in result]

# Q16 - Acteur ayant joué dans des films totalisant le plus de revenus
def q16_actor_most_revenue(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (a:Actor)-[:A_JOUE]->(f:Film)
            WHERE f.revenue > 0
            RETURN a.name AS acteur, round(sum(f.revenue)) AS total_revenus
            ORDER BY total_revenus DESC
            LIMIT 1
        """)
        return result.single()

# Q17 - Moyenne des votes de tous les films
def q17_avg_votes(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (f:Film)
            WHERE f.votes > 0
            RETURN round(avg(f.votes)) AS moyenne_votes
        """)
        return result.single()

# Q18 - Genre le plus représenté
def q18_most_common_genre(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (f:Film)
            WHERE f.genre IS NOT NULL
            UNWIND split(f.genre, ",") AS g
            RETURN trim(g) AS genre, count(*) AS nb_films
            ORDER BY nb_films DESC
            LIMIT 1
        """)
        return result.single()

# Q19 - Films où les membres du groupe ont joué
def q19_group_member_films(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (membre:Actor)-[:A_JOUE]->(f:Film)
            WHERE membre.name IN ["Bhargavi Ramanadane", "Eric Jr Songo", "Ryadh Sehanine"]
            RETURN DISTINCT f.title AS film, membre.name AS membre
            ORDER BY membre
        """)
        rows = [{"Film": r["film"], "Membre": r["membre"]} for r in result]
        return pd.DataFrame(rows)

# Q20 - Réalisateur ayant travaillé avec le plus d'acteurs distincts
def q20_director_most_actors(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (r:Realisateur)-[:A_REALISE]->(f:Film)<-[:A_JOUE]-(a:Actor)
            RETURN r.name AS realisateur, count(DISTINCT a) AS nb_acteurs
            ORDER BY nb_acteurs DESC
            LIMIT 1
        """)
        return result.single()

# Q21 - Films les plus connectés (le plus d'acteurs en commun avec d'autres films)
def q21_most_connected_films(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (f1:Film)<-[:A_JOUE]-(a:Actor)-[:A_JOUE]->(f2:Film)
            WHERE f1 <> f2
            RETURN f1.title AS film, count(DISTINCT f2) AS films_connectes
            ORDER BY films_connectes DESC
            LIMIT 5
        """)
        rows = [{"Film": r["film"], "Films connectés": r["films_connectes"]} for r in result]
        return pd.DataFrame(rows)

# Q22 - 5 acteurs ayant joué avec le plus de réalisateurs différents
def q22_actors_most_directors(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (a:Actor)-[:A_JOUE]->(f:Film)<-[:A_REALISE]-(r:Realisateur)
            RETURN a.name AS acteur, count(DISTINCT r) AS nb_realisateurs
            ORDER BY nb_realisateurs DESC
            LIMIT 5
        """)
        rows = [{"Acteur": r["acteur"], "Nb réalisateurs": r["nb_realisateurs"]} for r in result]
        return pd.DataFrame(rows)

# Q23 - Recommander un film à un acteur selon ses genres préférés
def q23_recommend_film(driver, actor_name):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (a:Actor {name: $actor_name})-[:A_JOUE]->(f:Film)
            WHERE f.genre IS NOT NULL
            WITH a, collect(DISTINCT trim(split(f.genre, ",")[0])) AS genres_aimes
            MATCH (rec:Film)
            WHERE ANY(g IN genres_aimes WHERE rec.genre CONTAINS g)
            AND NOT (a)-[:A_JOUE]->(rec)
            RETURN rec.title AS film, rec.genre AS genre, rec.rating AS note
            ORDER BY rec.rating DESC
            LIMIT 5
        """, actor_name=actor_name)
        rows = [{"Film": r["film"], "Genre": r["genre"], "Note": r["note"]} for r in result]
        return pd.DataFrame(rows)

# Q24 - Créer les relations INFLUENCE_PAR entre réalisateurs (même genre)
def q24_create_influence_relations(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (r1:Realisateur)-[:A_REALISE]->(f1:Film)
            MATCH (r2:Realisateur)-[:A_REALISE]->(f2:Film)
            WHERE r1 <> r2
              AND f1.genre IS NOT NULL AND f2.genre IS NOT NULL
              AND f1.genre = f2.genre
            MERGE (r1)-[:INFLUENCE_PAR]->(r2)
            RETURN count(*) AS relations_creees
        """)
        return result.single()

# Q25 - Chemin le plus court entre deux acteurs
def q25_shortest_path(driver, actor1="Tom Hanks", actor2="Scarlett Johansson"):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH path = shortestPath(
                (a1:Actor {name: $actor1})-[:A_JOUE*]-(a2:Actor {name: $actor2})
            )
            RETURN [n IN nodes(path) |
                CASE
                    WHEN n:Actor THEN n.name
                    WHEN n:Film  THEN n.title
                    ELSE ""
                END
            ] AS chemin, length(path) AS distance
        """, actor1=actor1, actor2=actor2)
        return result.single()

# Q15 - Données réseau PyVis (anne, film, co-acteur)
def q15_network_data(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (anne:Actor {name: "Anne Hathaway"})-[:A_JOUE]->(f:Film)<-[:A_JOUE]-(co:Actor)
            WHERE co.name <> "Anne Hathaway"
            RETURN anne.name AS anne, f.title AS film, co.name AS co_actor
        """)
        return [{"anne": r["anne"], "film": r["film"], "co_actor": r["co_actor"]} for r in result]

# Q21 - Données réseau film-film pour PyVis
def q21_network_data(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (f1:Film)<-[:A_JOUE]-(a:Actor)-[:A_JOUE]->(f2:Film)
            WHERE f1.title < f2.title
            WITH f1, f2, count(DISTINCT a) AS acteurs_communs
            ORDER BY acteurs_communs DESC
            LIMIT 15
            RETURN f1.title AS film1, f2.title AS film2, acteurs_communs
        """)
        return [{"film1": r["film1"], "film2": r["film2"], "acteurs_communs": r["acteurs_communs"]} for r in result]

# Q24 - Afficher le réseau INFLUENCE_PAR
def q24_influence_network(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (r1:Realisateur)-[:INFLUENCE_PAR]->(r2:Realisateur)
            RETURN r1.name AS source, r2.name AS target
            LIMIT 30
        """)
        return [{"source": r["source"], "target": r["target"]} for r in result]

# Q26 - Paires d'acteurs qui ont le plus collaboré (approximation communautés)
def q26_actor_communities(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (a1:Actor)-[:A_JOUE]->(f:Film)<-[:A_JOUE]-(a2:Actor)
            WHERE a1.name < a2.name
            RETURN a1.name AS acteur1, a2.name AS acteur2, count(f) AS films_en_commun
            ORDER BY films_en_commun DESC
            LIMIT 10
        """)
        rows = [{"Acteur 1": r["acteur1"], "Acteur 2": r["acteur2"], "Films en commun": r["films_en_commun"]} for r in result]
        return pd.DataFrame(rows)

# Q27 - Films avec genres en commun mais réalisateurs différents
def q27_common_genre_diff_director(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (f1:Film), (f2:Film)
            WHERE f1.title < f2.title
              AND f1.director <> f2.director
              AND f1.genre IS NOT NULL AND f2.genre IS NOT NULL
              AND ANY(g IN split(f1.genre, ",")
                  WHERE trim(g) IN [g2 IN split(f2.genre, ",") | trim(g2)])
            RETURN f1.title AS film1, f1.director AS realisateur1,
                   f2.title AS film2, f2.director AS realisateur2
            LIMIT 20
        """)
        rows = [{"Film 1": r["film1"], "Réalisateur 1": r["realisateur1"],
                 "Film 2": r["film2"], "Réalisateur 2": r["realisateur2"]} for r in result]
        return pd.DataFrame(rows)

# Q28 - Recommander des films à un utilisateur selon les genres préférés d'un acteur
def q28_recommend_by_actor(driver, actor_name):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (a:Actor {name: $actor_name})-[:A_JOUE]->(f:Film)
            WHERE f.genre IS NOT NULL
            WITH a, collect(DISTINCT trim(split(f.genre, ",")[0])) AS genres_aimes
            MATCH (rec:Film)
            WHERE ANY(g IN genres_aimes WHERE rec.genre CONTAINS g)
              AND NOT (a)-[:A_JOUE]->(rec)
              AND rec.revenue > 0
            RETURN rec.title AS film, rec.genre AS genre,
                   rec.rating AS note, rec.revenue AS revenu
            ORDER BY rec.revenue DESC
            LIMIT 5
        """, actor_name=actor_name)
        rows = [{"Film": r["film"], "Genre": r["genre"],
                 "Note": r["note"], "Revenu (M$)": r["revenu"]} for r in result]
        return pd.DataFrame(rows)

# Q29 - Créer les relations CONCURRENT entre réalisateurs (même genre, même année)
def q29_create_concurrent_relations(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (r1:Realisateur)-[:A_REALISE]->(f1:Film)
            MATCH (r2:Realisateur)-[:A_REALISE]->(f2:Film)
            WHERE r1 <> r2
              AND f1.year = f2.year
              AND f1.genre IS NOT NULL AND f2.genre IS NOT NULL
              AND ANY(g IN split(f1.genre, ",")
                  WHERE trim(g) IN [g2 IN split(f2.genre, ",") | trim(g2)])
            MERGE (r1)-[:CONCURRENT {annee: f1.year}]->(r2)
            RETURN count(*) AS relations_creees
        """)
        return result.single()

# Q30 - Collaborations fréquentes réalisateur-acteur et leur succès
def q30_director_actor_collabs(driver):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (r:Realisateur)-[:A_REALISE]->(f:Film)<-[:A_JOUE]-(a:Actor)
            WITH r, a, count(f) AS collaborations,
                 round(avg(f.revenue)) AS revenu_moyen,
                 round(avg(f.rating))  AS note_moyenne
            WHERE collaborations > 1
            RETURN r.name AS realisateur, a.name AS acteur,
                   collaborations, revenu_moyen, note_moyenne
            ORDER BY collaborations DESC
            LIMIT 10
        """)
        rows = [{"Réalisateur": r["realisateur"], "Acteur": r["acteur"],
                 "Collaborations": r["collaborations"],
                 "Revenu moyen (M$)": r["revenu_moyen"],
                 "Note moyenne": r["note_moyenne"]} for r in result]
        return pd.DataFrame(rows)
