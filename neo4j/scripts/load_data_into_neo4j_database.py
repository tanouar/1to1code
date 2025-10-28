from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://0.0.0.0:7687',
                              auth=('neo4j', 'plbconsultant'))

# deleting data
print('Deleting previous data')

query = '''
MATCH (n) 
DETACH DELETE n
'''

with driver.session() as session:
    print(query)
    session.run(query)

print('done')

# inserting data
print('Inserting characters')

query = '''
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/mcu/characters.csv' AS row
CREATE (:Character {name: row.character});
'''

with driver.session() as session:
    print(query)
    session.run(query)

print('done')

print('Inserting people')

query = '''
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/mcu/person.csv' AS row
CREATE (:Person {id: row.nconst, name:row.primaryName, birth_year: toInteger(row.birthYear), death_year: toInteger(row.deathYear), profession: split(row.primaryProfession, ',')});
'''

with driver.session() as session:
    print(query)
    session.run(query)

print('done')

print('Inserting movies')

query = '''
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/mcu/movies.csv' AS row
CREATE (:Movie {id: row.tconst, title: row.primaryTitle, year:  toInteger(row.startYear), runtime:toInteger(row.runtimeMinutes), genres: split(row.genres, ',')});
'''

with driver.session() as session:
    print(query)
    session.run(query)

print('done')

print('Creating relationships')

queries = [
    '''// Loading acting and changing the labels
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/mcu/person_plays_character.csv' AS row
    MATCH (p:Person) WHERE p.id = row.nconst
    MATCH (c:Character) WHERE c.name = row.character
    CREATE (p)-[:PLAY]->(c)
    WITH p
    SET p :Actor
    RETURN p;''',

    '''
    // Loading appearances
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/mcu/character_appears_in_movie.csv' AS row
    MATCH (c:Character) WHERE c.name = row.character
    MATCH (m:Movie) WHERE m.id = row.tconst
    CREATE (c)-[:APPEAR_IN]->(m);
    ''',

    '''
    // Loading directions
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/mcu/person_directs_movie.csv' AS row
    MATCH (p:Person) WHERE p.id = row.nconst
    MATCH (m:Movie) WHERE m.id = row.tconst
    CREATE (p)-[:DIRECTED]->(m);
    ''',

    '''
    // Loading productions
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/mcu/person_produces_movie.csv' AS row
    MATCH (p:Person) WHERE p.id = row.nconst
    MATCH (m:Movie) WHERE m.id = row.tconst
    CREATE (p)-[:PRODUCED]->(m);
    '''
]

with driver.session() as session:
    for q in queries:
        print(q)
        session.run(q)

print('done')