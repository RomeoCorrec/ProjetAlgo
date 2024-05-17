from neo4j import GraphDatabase
from Class.User import User

class graphDB:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_user(self, user: User):
        with self._driver.session() as session:
            query = "Create (u:User {username: $username, name: $name, surname: $surname, age: $age, password: $password, location: $location})"
            print(query)
            session.run(query, username=user.username, name=user.name, surname=user.surname, age=user.age,
                        password=user.password, location=user.location, sex=user.sex, mail=user.mail)

    def get_connected_users(self, user_name):
        with self._driver.session() as session:
            result = session.run("MATCH (u:User {name: $user_name})-[:KNOWS]->(v:User) WHERE NOT u = v RETURN v.name AS name", user_name=user_name)
            connected_users = [row['name'] for row in result]
        return connected_users

    def get_user_by_name(self, user_name):
        with self._driver.session() as session:
            result = session.run("MATCH (u:User {name: $user_name}) RETURN u.name AS name, u.age AS age", user_name=user_name)
            user = result.single()
        return user

    def find_common_friends(self, user_name):
        with self._driver.session() as session:
            result = session.run("""
                MATCH (u:User {name: $user_name})-[:KNOWS]->(common:User)<-[:KNOWS]-(v:User)
                WHERE NOT (u)-[:KNOWS]->(v)
                RETURN v.name AS name
            """, user_name=user_name)
            common_friends = [row['name'] for row in result]
        return common_friends

    def get_all_users(self):
        with self._driver.session() as session:
            result = session.run("MATCH (u:User) RETURN u.name AS name")
            all_users = [row['name'] for row in result]
        return all_users

    def calculate_user_similarities(self, user_name, common_friends):
        # Get user interests
        with self._driver.session() as session:
            result = session.run("MATCH (u:User {name: $user_name}) RETURN u.interests AS interests",
                                 user_name=user_name)
            user_interests = result.single()["interests"]

        # Calculate similarities between the user and their common friends
        similarities = {}
        for friend in common_friends:
            with self._driver.session() as session:
                result = session.run("MATCH (u:User {name: $friend}) RETURN u.interests AS interests", friend=friend)
                friend_interests = result.single()["interests"]

            similarity = len(set(user_interests).intersection(set(friend_interests)))
            similarities[friend] = similarity

        return similarities

    def calculate_similarities_between_common_friends(self, user_name):
        # Find common friends of the specified user
        common_friends = self.find_common_friends(user_name)

        # Calculate similarities between the specified user and their common friends
        similarities = {}
        for friend in common_friends:
            similarity = self.calculate_user_similarities(user_name, [friend])
            similarities[friend] = similarity[friend]

        # Sort the similarities in ascending order
        sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

        # Return the sorted list of similarities
        return sorted_similarities
