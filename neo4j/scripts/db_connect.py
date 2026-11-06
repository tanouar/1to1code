from neo4j import GraphDatabase

driver = GraphDatabase.driver(
  "neo4j://localhost:7687",       # (1)
  auth=("neo4j", "your-password") # (2)
)

##############################################################

# vérifier la connexion
driver.verify_connectivity()


##############################################################


# Execute a query
records, summary, keys = driver.execute_query( # (1)
    "RETURN COUNT {()} AS count"
)

# Get the first record
first = records[0]      # (2)

# Print the count entry
print(first["count"])   # (3)

##############################################################

# Close the driver connection
driver.close()          # (1)

##############################################################

