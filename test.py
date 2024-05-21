from ProjetAlgo.app.app.Class.User import User
from ProjetAlgo.app.app.utils import graphDB

GDB = graphDB("bolt://localhost:7687", "neo4j", "password")

GDB.modify_profil("ROMEGA", "Romeo", "CORREC", 21, "Paris", "Male", "mail.fr")
