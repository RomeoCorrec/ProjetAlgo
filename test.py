from ProjetAlgo.app.app.Class.User import User
from ProjetAlgo.app.app.utils import graphDB

GDB = graphDB("bolt://localhost:7687", "neo4j", "password")

GDB.delete_post(7)
GDB.delete_post(6)
