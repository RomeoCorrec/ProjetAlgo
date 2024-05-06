from py2neo import Graph, NodeMatcher, Node, Relationship
import networkx as nx
import matplotlib.pyplot as plt
# Connect to the local Neo4j database
graph = Graph("bolt://neo4j:adminadmin@localhost:7687")


query = """
MATCH (n:User)-[r:FRIEND]->(m:User)
RETURN n, r, m
"""
result = graph.run(query)

# Créer un nouvel objet de graphe NetworkX
G = nx.Graph()

# Parcourir les résultats de la requête et ajouter des nœuds et des arêtes à NetworkX
for record in result:
    node1 = record['n']
    node2 = record['m']
    relation = record['r']

    # Ajouter les nœuds
    G.add_node(node1['name'])
    G.add_node(node2['name'])

    # Ajouter l'arête avec le poids
    G.add_edge(node1['name'], node2['name'], weight=relation['weight'])


# Afficher le graphe
nx.draw(G, with_labels=True)
plt.show()


#Recomandation:
#MATCH (user:User {name: "Alice"})-[:FRIEND]-(friend)-[:FRIEND]-(friend_of_friend)
#WHERE NOT (user)-[:FRIEND]-(friend_of_friend)
#RETURN friend_of_friend
