import pandas as pd
import numpy as np
from scipy import stats

def q1_year_most_films(col):
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    result = list(col.aggregate(pipeline))
    return result[0] if result else {}

def q2_films_after_1999(col):
    return col.count_documents({"year": {"$gt": 1999}})

def q3_avg_votes_2007(col):
    pipeline = [
        {"$match": {"year": 2007}},
        {"$group": {"_id": None, "avg_votes": {"$avg": "$Votes"}}}
    ]
    result = list(col.aggregate(pipeline))
    return round(result[0]["avg_votes"], 2) if result else 0

def q4_films_per_year(col):
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = list(col.aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Année", "count": "Nombre de films"})

def q5_available_genres(col):
    pipeline = [
        {"$project": {"genres": {"$split": ["$genre", ","]}}},
        {"$unwind": "$genres"},
        {"$group": {"_id": {"$trim": {"input": "$genres"}}}},
        {"$sort": {"_id": 1}}
    ]
    result = list(col.aggregate(pipeline))
    return [r["_id"] for r in result]

def q6_highest_revenue_film(col):
    pipeline = [
        {"$match": {"Revenue (Millions)": {"$type": "double"}}},
        {"$sort": {"Revenue (Millions)": -1}},
        {"$limit": 1},
        {"$project": {"_id": 0, "title": 1, "Revenue (Millions)": 1, "year": 1, "Director": 1}}
    ]
    result = list(col.aggregate(pipeline))
    return result[0] if result else {}

def q7_directors_more_than_5(col):
    pipeline = [
        {"$group": {"_id": "$Director", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 5}}},
        {"$sort": {"count": -1}}
    ]
    result = list(col.aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Réalisateur", "count": "Nombre de films"})

def q8_genre_most_revenue(col):
    pipeline = [
        {"$match": {"Revenue (Millions)": {"$type": "double"}}},
        {"$project": {"genres": {"$split": ["$genre", ","]}, "Revenue (Millions)": 1}},
        {"$unwind": "$genres"},
        {"$group": {
            "_id": {"$trim": {"input": "$genres"}},
            "avg_revenue": {"$avg": "$Revenue (Millions)"}
        }},
        {"$sort": {"avg_revenue": -1}}
    ]
    result = list(col.aggregate(pipeline))
    df = pd.DataFrame(result).rename(columns={"_id": "Genre", "avg_revenue": "Revenu moyen (M$)"})
    df["Revenu moyen (M$)"] = df["Revenu moyen (M$)"].round(2)
    return df

def q9_top3_per_decade(col):
    pipeline = [
        {"$match": {"Metascore": {"$type": "int"}}},
        {"$addFields": {"decade": {"$multiply": [{"$floor": {"$divide": ["$year", 10]}}, 10]}}},
        {"$sort": {"decade": 1, "Metascore": -1}},
        {"$group": {
            "_id": "$decade",
            "top3": {"$push": {"title": "$title", "Metascore": "$Metascore", "year": "$year"}}
        }},
        {"$project": {"_id": 1, "top3": {"$slice": ["$top3", 3]}}},
        {"$sort": {"_id": 1}}
    ]
    result = list(col.aggregate(pipeline))
    rows = []
    for r in result:
        for film in r["top3"]:
            rows.append({"Décennie": f"{int(r['_id'])}s", "Titre": film["title"], "Année": film["year"], "Metascore": film["Metascore"]})
    return pd.DataFrame(rows)

def q10_longest_film_per_genre(col):
    pipeline = [
        {"$project": {"title": 1, "Runtime (Minutes)": 1, "genres": {"$split": ["$genre", ","]}}},
        {"$unwind": "$genres"},
        {"$addFields": {"genres": {"$trim": {"input": "$genres"}}}},
        {"$sort": {"Runtime (Minutes)": -1}},
        {"$group": {
            "_id": "$genres",
            "title": {"$first": "$title"},
            "runtime": {"$first": "$Runtime (Minutes)"}
        }},
        {"$sort": {"_id": 1}}
    ]
    result = list(col.aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Genre", "title": "Film", "runtime": "Durée (min)"})

def q11_create_view(col):
    db = col.database
    if "top_films_view" in db.list_collection_names():
        db.drop_collection("top_films_view")
    db.command({
        "create": "top_films_view",
        "viewOn": "films",
        "pipeline": [
            {"$match": {"Metascore": {"$gt": 80}, "Revenue (Millions)": {"$gt": 50}}},
            {"$project": {"_id": 0, "title": 1, "Metascore": 1, "Revenue (Millions)": 1, "year": 1, "Director": 1}}
        ]
    })

def q11_get_view(col):
    db = col.database
    return pd.DataFrame(list(db["top_films_view"].find()))

def q12_correlation(col):
    pipeline = [
        {"$match": {"Revenue (Millions)": {"$type": "double"}, "Runtime (Minutes)": {"$exists": True}}},
        {"$project": {"_id": 0, "title": 1, "runtime": "$Runtime (Minutes)", "revenue": "$Revenue (Millions)"}}
    ]
    df = pd.DataFrame(list(col.aggregate(pipeline)))
    if df.empty:
        return {"df": df, "corr": None}
    corr = df["runtime"].corr(df["revenue"])
    return {"df": df, "corr": round(corr, 4)}

def q13_avg_runtime_per_decade(col):
    pipeline = [
        {"$addFields": {"decade": {"$multiply": [{"$floor": {"$divide": ["$year", 10]}}, 10]}}},
        {"$group": {"_id": "$decade", "avg_runtime": {"$avg": "$Runtime (Minutes)"}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = list(col.aggregate(pipeline))
    df = pd.DataFrame(result).rename(columns={"_id": "Décennie", "avg_runtime": "Durée moyenne (min)", "count": "Nb films"})
    df["Durée moyenne (min)"] = df["Durée moyenne (min)"].round(1)
    df["Décennie"] = df["Décennie"].astype(str) + "s"
    return df