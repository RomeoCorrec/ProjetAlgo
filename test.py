from app.app.Class.User import User
from app.app.utils import graphDB

GDB = graphDB("neo4j+s://fb7779f4.databases.neo4j.io", "neo4j", "4DTufAW-6wB0UlMjaLpJ_53j1-ZzKV3N1U3tCCka9Qo")

print(GDB.get_user_by_username("user"))
