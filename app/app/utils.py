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
            result = session.run("MATCH (u:User {username: $user_name})-[:FRIEND]->(v:User) WHERE NOT u = v RETURN v.username AS username", user_name=user_name)
            connected_users = [row['username'] for row in result]
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

    def has_send_friend_request(self, sender, receiver):
        with self._driver.session() as session:
            result = session.run("""MATCH (a:User {username: $sender})-[:FRIEND_REQUEST]->(b:User {username: $receiver}) RETURN b""", sender=sender, receiver=receiver)
            return result.single() is not None

    def is_friend(self, sender, receiver):
        with self._driver.session() as session:
            result = session.run("""MATCH (a:User {username: $sender})-[:FRIEND]->(b:User {username: $receiver}) RETURN b""", sender=sender, receiver=receiver)
            return result.single() is not None

    def accept_friend_request(self, sender, receiver):
        with self._driver.session() as session:
            query = "MATCH (a:User {username: $sender})-[r:FRIEND_REQUEST]->(b:User {username: $receiver}) DELETE r"
            session.run(query, sender=sender, receiver=receiver)
            query1 = "MATCH (a:User {username: $sender}), (b:User {username: $receiver}) CREATE (a)-[:FRIEND]->(b)"
            query2 = "MATCH (a:User {username: $sender}), (b:User {username: $receiver}) CREATE (a)-[:FRIEND]->(b)"
            session.run(query1, sender=sender, receiver=receiver)
            session.run(query2, sender=receiver, receiver=sender)

    def get_friends_requests(self, username):
        with self._driver.session() as session:
            result = session.run("""MATCH (a:User {username: $username})<-[r:FRIEND_REQUEST]-(b:User) RETURN b.username as username""", username=username)
            friends_requests = [row['username'] for row in result]
        return friends_requests

    def delete_friend_request(self, sender, receiver):
        with self._driver.session() as session:
            query = "MATCH (a:User {username: $sender})-[r:FRIEND_REQUEST]->(b:User {username: $receiver}) DELETE r"
            session.run(query, sender=sender, receiver=receiver)

    def delete_friendship(self, sender, receiver):
        with self._driver.session() as session:
            query = "MATCH (a:User {username: $sender})-[r:FRIEND]->(b:User {username: $receiver}) DELETE r"
            session.run(query, sender=sender, receiver=receiver)
            query = "MATCH (a:User {username: $sender})-[r:FRIEND]->(b:User {username: $receiver}) DELETE r"
            session.run(query, sender=receiver, receiver=sender)

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

    def get_friends(self, username):
        with self._driver.session() as session:
            query = "MATCH (u:User {username: $username})-[:FRIEND]->(friend) RETURN friend.username AS friend_username"
            result = session.run(query, username=username)
            friends = [row['friend_username'] for row in result]
            return friends

    def create_discussion(self, user1, user2):
        with self._driver.session() as session:
            query = (
                "CREATE (d:Discussion {user1: $user1, user2: $user2}) "
                "RETURN d"
            )
            session.run(query, user1=user1, user2=user2)

    def create_message(self, sender, receiver, content):
        with self._driver.session() as session:
            # Création du message
            query_create_message = (
                "MATCH (d:Discussion {user1: $sender, user2: $receiver}) "
                "CREATE (m:Message {sender: $sender, receiver: $receiver, content: $content, timestamp: datetime()}) "
                "MERGE (d)-[:CONTAIN]->(m)"
            )
            session.run(query_create_message, sender=sender, receiver=receiver, content=content)

    def check_discussion(self, username1, username2):
        with self._driver.session() as session:
            query = (
                "MATCH (d:Discussion) WHERE (d.user1 = $username1 AND d.user2 = $username2) OR (d.user1 = $username2 AND d.user2 = $username1) RETURN COUNT(d) AS count"
            )
            result = session.run(query, username1=username1, username2=username2)
            record = result.single()
            count = record["count"] if record else 0
            return count > 0

    def get_messages(self, username1, username2):
        with self._driver.session() as session:
            query = """
            MATCH (d:Discussion)
            WHERE (d.user1 = $username1 AND d.user2 = $username2) OR (d.user1 = $username2 AND d.user2 = $username1)
            MATCH (d)-[:CONTAIN]-(m:Message)
            RETURN m.content AS content, m.timestamp AS timestamp, m.sender AS sender
            ORDER BY m.timestamp
            """
            result = session.run(query, username1=username1, username2=username2)
            messages = [{"sender": row["sender"], "content": row["content"], "timestamp": row["timestamp"]} for row in result]
            return messages
