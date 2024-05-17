from Class.User import User
from utils import graphDB
from neo4j import GraphDatabase

# Create a new user object
user = User(
    username="johndoe",
    name="John",
    surname="Doe",
    age=30,
    password="password123",
    location="New York, NY",
    sex="Male",
    mail="johndoe@example.com",
)

# Add interests to the user object
user.interests.append("Software Engineering")
user.interests.append("Travel")
user.interests.append("Photography")
GDB = graphDB("bolt://localhost:7687", "neo4j", "password")

print(GDB.calculate_similarities_between_common_friends("Alice"))