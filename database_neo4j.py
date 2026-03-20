from neo4j import GraphDatabase

def get_neo4j_connection():
    uri = "neo4j+s://50c439a6.databases.neo4j.io"
    username = "50c439a6"
    password = "loEaMOw2S9aI4007cU3j2ueiUDd4sXKG4iCtp1OUBis"
    driver = GraphDatabase.driver(uri, auth=(username, password))
    return driver
