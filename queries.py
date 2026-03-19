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

