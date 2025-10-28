from neo4j import GraphDatabase, basic_auth

# Configuration de la connexion
URI = "bolt://localhost:7687"
AUTH = basic_auth("neo4j", "plbconsultant")

driver = GraphDatabase.driver(URI, auth=AUTH)

with driver.session() as session:
    print("\n--- Étape 1 : Vérification du nœud Hulk ---")
    result = session.run("MATCH (c:Character {name: 'Hulk'}) RETURN c")
    record = result.single()
    if record:
        print("✅ Hulk trouvé :", record["c"])
    else:
        print("❌ Hulk n'existe pas encore, création du nœud...")
        session.run("CREATE (c:Character {name: 'Hulk', strength: 100, mood: 'angry'})")

    print("\n--- Étape 2 : Démarrage d'une transaction ---")
    tx = session.begin_transaction()

    try:
        print("➡️  Mise à jour du mood de Hulk dans la transaction...")
        tx.run("MATCH (c:Character {name: 'Hulk'}) SET c.mood = 'happy' RETURN c")

        print("  💬 Hulk est désormais 'happy' dans la transaction (non commitée).")
        raise Exception("Simulation d'erreur : rollback imminent")

        # Si on voulait valider, on ferait :
        # tx.commit()
    except Exception as e:
        print("\n⚠️  Exception détectée :", e)
        tx.rollback()
        print("⏪ Rollback effectué, les modifications sont annulées.")

    print("\n--- Étape 3 : Vérification après rollback ---")
    result = session.run("MATCH (c:Character {name: 'Hulk'}) RETURN c.mood AS mood")
    print("Mood actuel de Hulk :", result.single()["mood"])

driver.close()
