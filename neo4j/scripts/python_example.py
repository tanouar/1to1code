from neo4j import GraphDatabase

# Connexion au serveur Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "plbconsultant"

driver = GraphDatabase.driver(uri, auth=(username, password))

def get_all_nodes(tx):
    # Requête Cypher pour récupérer tous les nœuds
    result = tx.run("MATCH (n) RETURN n")
    return [record["n"] for record in result]

# Utilisation de la session pour exécuter la requête
with driver.session() as session:
    nodes = session.read_transaction(get_all_nodes)
    for node in nodes:
        print(node)

driver.close()
