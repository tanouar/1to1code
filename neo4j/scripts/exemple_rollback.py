from neo4j import GraphDatabase

# Connexion à la base de données Neo4j
uri = "bolt://localhost:7687"  # Remplacez par votre URI
driver = GraphDatabase.driver(uri, auth=("neo4j", "plbconsultant"))

def update_character(tx, old_name, new_name):
    # 1. Rechercher le personnage (votre requête de base)
    result = tx.run("MATCH (c:Character {name: $old_name}) RETURN c", old_name=old_name)
    hulk = result.single()
    if not hulk:
        raise ValueError(f"Personnage {old_name} non trouvé !")

    # 2. Modifier son nom (simulation d'une mise à jour)
    tx.run("MATCH (c:Character {name: $old_name}) SET c.name = $new_name", old_name=old_name, new_name=new_name)
    print(f"Nom mis à jour : {old_name} -> {new_name}")

    # 3. Provoquer une erreur (pour simuler un problème et déclencher un rollback)
    raise ValueError("Oups ! Erreur simulée pour annuler la transaction.")

def main():
    try:
        with driver.session() as session:
            # Démarrer une transaction
            session.write_transaction(update_character, "Hulk", "Green Giant")
    except Exception as e:
        print(f"Transaction annulée (rollback) : {e}")
    finally:
        # Vérifier l'état final (le nom devrait être resté "Hulk")
        with driver.session() as session:
            result = session.run("MATCH (c:Character {name: 'Hulk'}) RETURN c")
            hulk = result.single()
            if hulk:
                print("Le nom est toujours 'Hulk' (rollback réussi !)")
            else:
                print("Hulk a disparu (ce ne devrait pas arriver !)")

if __name__ == "__main__":
    main()
    driver.close()
