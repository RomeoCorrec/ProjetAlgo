from ProjetAlgo.app.app.Class.User import User
from ProjetAlgo.app.app.utils import graphDB

GDB = graphDB("neo4j+s://fb7779f4.databases.neo4j.io", "neo4j", "4DTufAW-6wB0UlMjaLpJ_53j1-ZzKV3N1U3tCCka9Qo")

user = User("user2", "user", "user", 22, "Password@123", "Paris", "M", "mail@mail.com")
user.profile_picture = None
query = """Create (u:User {username: $username, name: $name, surname: $surname, age: $age,
 password: $password, location: $location, sex: $sex, mail: $mail, private: false, profile_picture: $profile_picture})"""

GDB._driver.session().run(query, username=user.username, name=user.name, surname=user.surname, age=user.age, password=user.password, location=user.location,
                          sex=user.sex, mail=user.mail, profile_picture=user.profile_picture)
