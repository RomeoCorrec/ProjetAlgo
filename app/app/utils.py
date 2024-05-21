from neo4j import GraphDatabase
from .Class.User import User
import datetime

class graphDB:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def add_new_user(self, user: User):
        with self._driver.session() as session:
            query = "Create (u:User {username: $username, name: $name, surname: $surname, age: $age, password: $password, location: $location, sex: $sex, mail: $mail})"
            session.run(query, username=user.username, name=user.name, surname=user.surname, age=user.age,
                        password=user.password, location=user.location, sex=user.sex, mail=user.mail)

    def delete_user_by_username(self, username):
        with self._driver.session() as session:
            query = "MATCH (u:User {username: $username}) DETACH DELETE u"
            session.run(query, username=username)

    def get_password_by_username(self, username):
        with self._driver.session() as session:
            result = session.run("MATCH (u:User {username: $username}) RETURN u.password AS password", username=username)
            password = result.single()["password"]
        return password

    def get_connected_users(self, user_name):
        with self._driver.session() as session:
            result = session.run("MATCH (u:User {username: $user_name})-[:FRIEND]->(v:User) WHERE NOT u = v RETURN v.name AS name", user_name=user_name)
            connected_users = [row['name'] for row in result]
        return connected_users

    def get_user_by_name(self, user_name):
        with self._driver.session() as session:
            result = session.run("MATCH (u:User {username: $user_name}) RETURN u", user_name=user_name)
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

    def get_user_by_username(self, username):
        with self._driver.session() as session:
            result = session.run("""MATCH (u:User {username: $username}) RETURN u""", username=username)
            user = result.single().data().get('u')
        return user

    def check_username_exists(self, username):
        with self._driver.session() as session:
            result = session.run("""MATCH (u:User {username: $username}) RETURN u""", username=username)
            return result.single() is not None

    def add_new_friend_request(self, sender, receiver):
        with self._driver.session() as session:
            query = "MATCH (a:User {username: $sender}), (b:User {username: $receiver}) CREATE (a)-[:FRIEND_REQUEST]->(b)"
            session.run(query, sender=sender, receiver=receiver)

    def accept_friend_request(self, sender, receiver):
        with self._driver.session() as session:
            query = "MATCH (a:User {username: $sender})-[r:FRIEND_REQUEST]->(b:User {username: $receiver}) DELETE r"
            session.run(query, sender=sender, receiver=receiver)
            query = "MATCH (a:User {username: $sender}), (b:User {username: $receiver}) CREATE (a)-[:FRIEND]->(b)"
            query2 = "MATCH (a:User {username: $sender}), (b:User {username: $receiver}) CREATE (a)-[:FRIEND]->(b)"
            session.run(query, sender=sender, receiver=receiver)
            session.run(query2, sender=receiver, receiver=sender)

    def get_friends_requests(self, username):
        with self._driver.session() as session:
            result = session.run("""MATCH (a:User {username: $username})<-[r:FRIEND_REQUEST]-(b:User) RETURN b.username as username""", username=username)
            friends_requests = [row['username'] for row in result]
        return friends_requests

    def modify_profil(self, username, name, surname, age, location, sex, mail):
        with self._driver.session() as session:
            query = "MATCH (u:User {username: $username}) SET u.name = $name, u.surname = $surname, u.age = $age, u.location = $location, u.sex = $sex, u.mail = $mail"
            session.run(query, username=username, name=name, surname=surname, age=age, location=location, sex=sex, mail=mail)
        return

    def add_post(self, username, post):
        date = datetime.datetime.now()
        with self._driver.session() as session:
            query_creation = "CREATE (p:Post {content: $content, image: $image, date: $date})"
            session.run(query_creation, content = post.content, image = post.images, date = date)
            query_link = "MATCH (a:User {username: $username}) , (b:Post {date: $date}) CREATE (a)-[:POSTED]->(b)"
            session.run(query_link, username=username, date=date)

    def get_posts(self, username):
        with self._driver.session() as session:
            query = """
            MATCH (a:User {username: $username})-[:POSTED]->(p:Post)
            RETURN p.content AS content, p.image AS image, p.date AS date
            ORDER BY p.date DESC
            """
            result = session.run(query, username=username)
            posts = []
            for record in result:
                post = {
                    'content': record['content'],
                    'image': record['image'],
                    'date': record['date'],
                }
                posts.append(post)
            return posts