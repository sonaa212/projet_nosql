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
                    ELSE toString(n)
                END
            ] AS chemin, length(path) AS distance
        """, actor1=actor1, actor2=actor2)
        return result.single()

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
