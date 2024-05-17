from Class.User import User
from utils import graphDB
from neo4j import GraphDatabase

GDB = graphDB("bolt://localhost:7687", "neo4j", "password")

user3 = User("test3", "test3", "test3", 20, "password3", "Paris", "F","mail3")

user4 = User("test4", "test4", "test4", 20, "password4", "Paris", "F","mail4")

print(GDB.get_friends_requests(user3.username))