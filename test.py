from ProjetAlgo.app.app.User import User
from ProjetAlgo.app.app.utils import graphDB

GDB = graphDB("bolt://localhost:7687", "neo4j", "password")

user3 = User("test3", "test3", "test3", 20, "password3", "Paris", "F","mail3")

user4 = User("test4", "test4", "test4", 20, "password4", "Paris", "F","mail4")

print(GDB.get_password_by_username("test3"))