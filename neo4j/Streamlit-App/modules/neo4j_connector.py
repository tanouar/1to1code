# modules/neo4j_connector.py
from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_all_labels(self):
        query = "CALL db.labels() YIELD label RETURN label"
        with self.driver.session() as session:
            result = session.run(query)
            return [record["label"] for record in result]

    def get_all_relation_types(self):
        query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
        with self.driver.session() as session:
            result = session.run(query)
            return [record["relationshipType"] for record in result]

    def get_graph(self, labels=None, rel_types=None):
        """
        Récupère les nœuds et relations filtrés dynamiquement.
        """
        label_filter = ""
        if labels:
            label_filter = "WHERE " + " OR ".join([f"'{l}' IN labels(n)" for l in labels])

        rel_filter = ""
        if rel_types:
            rel_filter = "AND " + " OR ".join([f"type(r) = '{r_type}'" for r_type in rel_types])

        query = f"""
        MATCH (n)
        {label_filter}
        OPTIONAL MATCH (n)-[r]->(m)
        WHERE r IS NOT NULL {rel_filter}
        RETURN DISTINCT n, r, m
        LIMIT 500
        """
        nodes = {}
        relationships = []
        with self.driver.session() as session:
            result = session.run(query)
            for record in result:
                n = record["n"]
                m = record["m"]
                r = record["r"]

                if n:
                    nodes[n.id] = {"id": n.id, "label": list(n.labels)[0] if n.labels else "", **dict(n.items())}
                if m:
                    nodes[m.id] = {"id": m.id, "label": list(m.labels)[0] if m.labels else "", **dict(m.items())}
                if r:
                    relationships.append({
                        "source": r.start_node.id,
                        "target": r.end_node.id,
                        "type": r.type
                    })
        return list(nodes.values()), relationships
