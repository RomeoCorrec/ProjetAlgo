from py2neo import Graph, NodeMatcher, Node, Relationship


# Connect to the local Neo4j database
graph = Graph("bolt://neo4j:adminadmin@localhost:7687")
user1 = Node("User", name="TEST1")
user2 = Node("User", name="TEST2")
rel = Relationship(user1, "FRIEND", user2, weight=5)
graph.create(user1)
graph.create(user2)
graph.create(rel)