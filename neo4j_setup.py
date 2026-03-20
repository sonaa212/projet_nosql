from database import get_connection
from database_neo4j import get_neo4j_connection

def setup_neo4j():
    # Connexion MongoDB
    col = get_connection()
    films = list(col.find({}))

    # Connexion Neo4j
    driver = get_neo4j_connection()

    with driver.session(database="50c439a6") as session:

        # Supprimer toutes les données existantes
        print("Suppression des données existantes...")
        session.run("MATCH (n) DETACH DELETE n")

        print(f"Import de {len(films)} films...")

        for film in films:
            title      = film.get("title", "")
            year       = film.get("year", 0)
            votes      = film.get("Votes", 0)
            revenue    = film.get("Revenue (Millions)", 0)
            rating     = film.get("Metascore", 0)
            director   = film.get("Director", "")
            actors_str = film.get("Actors", "")
            genre      = film.get("genre", "")
            film_id    = str(film.get("_id", ""))

            if not title:
                continue

            # 1. Créer le nœud Film
            session.run("""
                MERGE (f:Film {title: $title})
                SET f.id       = $id,
                    f.year     = $year,
                    f.votes    = $votes,
                    f.revenue  = $revenue,
                    f.rating   = $rating,
                    f.director = $director,
                    f.genre    = $genre
            """,
                title=title,
                id=film_id,
                year=year,
                votes=votes if isinstance(votes, (int, float)) else 0,
                revenue=revenue if isinstance(revenue, float) else 0,
                rating=rating if isinstance(rating, int) else 0,
                director=director,
                genre=genre
            )

            # 2. Créer le nœud Realisateur + relation A_REALISE
            if director:
                session.run("""
                    MERGE (r:Realisateur {name: $name})
                    WITH r
                    MATCH (f:Film {title: $title})
                    MERGE (r)-[:A_REALISE]->(f)
                """, name=director, title=title)

            # 3. Créer les nœuds Actor + relation A_JOUE
            if actors_str:
                actors = [a.strip() for a in str(actors_str).split(",")]
                for actor in actors:
                    if actor:
                        session.run("""
                            MERGE (a:Actor {name: $name})
                            WITH a
                            MATCH (f:Film {title: $title})
                            MERGE (a)-[:A_JOUE]->(f)
                        """, name=actor, title=title)

        # 4. Créer les nœuds membres du groupe + les attacher à Avengers
        print("Ajout des membres du groupe...")
        membres = ["Bhargavi Ramanadane", "Eric Jr Songo", "Ryadh Sehanine"]
        for membre in membres:
            session.run("""
                MERGE (a:Actor {name: $name})
                WITH a
                MATCH (f:Film) WHERE f.title CONTAINS 'Avengers'
                MERGE (a)-[:A_JOUE]->(f)
            """, name=membre)

    driver.close()
    print("Setup Neo4j terminé avec succès !")

if __name__ == "__main__":
    setup_neo4j()
