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
            query = """Create (u:User {username: $username, name: $name, surname: $surname, age: $age,
             password: $password, location: $location, sex: $sex, mail: $mail, private: false,
              profile_picture: $profile_picture})"""
            session.run(query, username=user.username, name=user.name, surname=user.surname, age=user.age,
                        password=user.password, location=user.location, sex=user.sex, mail=user.mail, profile_picture=user.profile_picture)

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
                MATCH (u:User {username: $user_name})-[:FRIEND]->(common:User)<-[:FRIEND]-(v:User)
                WHERE NOT (u)-[:FRIEND]->(v)
                RETURN v.username AS username
            """, user_name=user_name)
            common_friends = [row['username'] for row in result]
            if len(common_friends) != 0:
                if common_friends[0] is None:
                    return []
            common_friends = list(set(common_friends))
        return common_friends

    def get_lv2recommendations(self, user_name):
        with self._driver.session() as session:
            result = session.run("""
                MATCH (u:User {username: $user_name})-[:FRIEND]->(common:User)<-[:FRIEND]-(v:User)
                WHERE NOT (u)-[:FRIEND]->(v) AND v.username <> $user_name
                OPTIONAL MATCH (v)-[:FRIEND]->(fof:User)
                WHERE NOT (u)-[:FRIEND]->(fof) AND fof.username <> $user_name
                RETURN fof.username AS fofof
            """, user_name=user_name)

            fof = [row['fofof'] for row in result]
            if len(fof) != 0:
                if fof[0] is None:
                    return []
            recomendations = set(fof)
        return list(recomendations)

    def get_recommendations(self, user_name):
        with self._driver.session() as session:
            lv1 = self.find_common_friends(user_name)
            lv2 = self.get_lv2recommendations(user_name)
            recomendations = set(lv1 + lv2)
            return list(recomendations)
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

    def is_private(self, username):
        with self._driver.session() as session:
            result = session.run("""MATCH (u:User {username: $username}) RETURN u.private AS private""", username=username)
            return result.single()["private"]

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

    def modify_profil(self, username, name, surname, age, location, sex, mail, private, profile_picture):
        with self._driver.session() as session:
            query = "MATCH (u:User {username: $username}) SET u.name = $name, u.surname = $surname, u.age = $age, u.location = $location, u.sex = $sex, u.mail = $mail, u.private = $private, u.profile_picture = $profile_picture"
            session.run(query, username=username, name=name, surname=surname, age=age, location=location, sex=sex, mail=mail, private=private, profile_picture=profile_picture)
        return

    def add_post(self, username, post):
        date = datetime.datetime.now()
        with self._driver.session() as session:
            query_creation = "CREATE (p:Post {content: $content, media: $media, media_type: $media_type, date: $date, author: $username})"
            session.run(query_creation, content = post.content, media = post.media, media_type = post.media_type, date = date, username = username)
            query_link = "MATCH (a:User {username: $username}) , (b:Post {date: $date}) CREATE (a)-[:POSTED]->(b)"
            session.run(query_link, username=username, date=date)

    def get_posts(self, username):
        with self._driver.session() as session:
            query = """
            MATCH (a:User {username: $username})-[:POSTED]->(p:Post)
            RETURN p.content AS content, p.media AS media, p.media_type as media_type, p.date AS date, p.author AS author, id(p) AS id
            ORDER BY p.date DESC
            """
            result = session.run(query, username=username)
            posts = []
            for record in result:
                post = {
                    'content': record['content'],
                    'media': record['media'],
                    'media_type': record['media_type'],
                    'date': record['date'],
                    'author': record['author'],
                    'id': record['id']
                }
                posts.append(post)
            return posts

    def get_filtered_posts(self, username, keyword):
        with self._driver.session() as session:
            query = """
            MATCH (a:User {username: $username})-[:POSTED]->(p:Post)
            WHERE p.content CONTAINS $keyword
            RETURN p.content AS content, p.image AS image, p.date AS date, p.author AS author, id(p) AS id
            ORDER BY p.date DESC
            """
            result = session.run(query, username=username, keyword=keyword)
            posts = []
            for record in result:
                post = {
                    'content': record['content'],
                    'image': record['image'],
                    'date': record['date'],
                    'author': record['author'],
                    'id': record['id']
                }
                posts.append(post)
            return posts

    def get_friends_posts(self, username):
        friends = self.get_friends(username)
        posts = []
        for friend in friends:
            posts += self.get_posts(friend)
        return posts

    def get_filtered_friends_posts(self, username, keyword):
        friends = self.get_friends(username)
        posts = []
        for friend in friends:
            posts += self.get_filtered_posts(friend, keyword)
        return posts

    def get_recommendations_posts(self, username):
        with self._driver.session() as session:
            commun_friends = self.find_common_friends(username)
            posts = []
            for friend in commun_friends:
                posts += self.get_posts(friend)
            return posts

    def delete_post(self, post_id):
        with self._driver.session() as session:
            query = "MATCH (p:Post) WHERE id(p) = $post_id DETACH DELETE p"
            session.run(query, post_id=post_id)

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

    def delete_discussion_and_messages(self, user1, user2):
        with self._driver.session() as session:
            query = (
                "MATCH (d:Discussion) WHERE (d.user1 = $user1 AND d.user2 = $user2) OR (d.user1 = $user2 AND d.user2 = $user1) "
                "DETACH DELETE d"
            )
            session.run(query, user1=user1, user2=user2)

    def create_message(self, sender, receiver, content):
        with self._driver.session() as session:
            # Création du message
            query_create_message = (
                "MATCH (d:Discussion) WHERE (d.user1 = $sender AND d.user2 = $receiver) OR (d.user1 = $receiver AND d.user2 = $sender) "
                "CREATE (m:Message {sender: $sender, receiver: $receiver, content: $content, timestamp: datetime()}) "
                "MERGE (d)-[:CONTAIN]->(m)"
            )
            session.run(query_create_message, sender=sender, receiver=receiver, content=content)

    def delete_messages(self, sender, receiver):
        with self._driver.session() as session:
            query = (
                "MATCH (m:Message) WHERE (m.sender = $sender AND m.receiver = $receiver) OR (m.sender = $receiver AND m.receiver = $sender)"
                "DETACH DELETE m"
            )
            session.run(query, sender=sender, receiver=receiver)
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

    def get_post_by_id(self, id:int):
        with self._driver.session() as session:
            query = "MATCH (p:Post) WHERE id(p) = $id RETURN p"
            post = session.run(query, id = id).single()
            return post["p"]

    def create_comment(self, post_id:int, content:str, username):
        with self._driver.session() as session:
            query = """MATCH (p:Post) WHERE id(p) = $post_id
            CREATE (c:Comment {username: $username, date: $date, content: $content})
            CREATE (c)-[:ABOUT]->(p)
            RETURN c, p"""
            date = datetime.datetime.now()
            session.run(query, post_id = post_id, date = date, username = username, content = content)

    def get_comments(self, post_id: int):
        with self._driver.session() as session:
            query = """MATCH (p:Post) WHERE id(p) = $post_id
                    MATCH (p)<-[:ABOUT]-(c:Comment)
                    RETURN c"""
            result = session.run(query, post_id=post_id)
            comments = [record["c"] for record in result]
            return comments

    def get_like_count(self,post_id):
        query = """
        MATCH (:User)-[l:LIKE]->(p:Post)
        WHERE id(p) = $post_id
        RETURN COUNT(l) AS likeCount
        """
        with self._driver.session() as session:
            result = session.run(query, post_id = post_id)
            like_count = result.single()["likeCount"]
        return like_count

    def has_liked_post(self, post_id, username):
        query = """
        MATCH (:User {username: $username})-[l:LIKE]->(p:Post)
        WHERE id(p) = $post_id
        RETURN COUNT(l) as like_count
        """
        with self._driver.session() as session:
            result = session.run(query, username = username, post_id = post_id)
            like_count = result.single()["like_count"]
        return like_count > 0

    def like_post(self, post_id, username):
        query = """
        MATCH (u:User {username: $username}), (p:Post)
        WHERE id(p) = $post_id
        CREATE (u)-[:LIKE]->(p)
        """
        with self._driver.session() as session:
            result = session.run(query, username = username, post_id = post_id)


    def create_group(self, group_name, creator, invitation_list):
        query_creation = """
            MATCH (u:User {username: $creator})
            CREATE (g:GroupDiscussion {name: $group_name, creator: $creator})"""
        with self._driver.session() as session:
            session.run(query_creation, creator = creator, group_name = group_name )

            for username in invitation_list:
                invite_query = """
                MATCH (u:User {username: $username}), (g:GroupDiscussion {name: $group_name})
                CREATE (u)-[:INVITATION]->(g)
                """
                session.run(invite_query, username=username, group_name=group_name)
            query = """MATCH (u:User {username: $username}), (g:GroupDiscussion {name: $group_name})
                       CREATE (u)-[:PARTICIPATE]->(g)"""
            session.run(query, username = creator, group_name = group_name)

    def accept_invitation_group(self, username, group_name):
        query = """
        MATCH (u:User {username: $username})-[inv:INVITATION]->(g:GroupDiscussion {name: $group_name})
        MERGE (u)-[:PARTICIPATE]->(g)
        DELETE inv
        """
        with self._driver.session() as session:
            session.run(query, username=username, group_name=group_name)

    def refuse_invitation_group(self, username, group_name):
        query = """
        MATCH (u:User {username: $username})-[inv:INVITATION]->(g:GroupDiscussion {name: $group_name})
        DELETE inv
        """
        with self._driver.session() as session:
            session.run(query, username=username, group_name=group_name)

    def add_user_in_group(self, username, group_name):
        with self._driver.session() as session:
            invite_query = """
            MATCH (u:User {username: $username}), (g:GroupDiscussion {name: $group_name})
            CREATE (u)-[:INVITATION]->(g)
            """
            session.run(invite_query, username=username, group_name=group_name)

    def get_groups(self, username):
        query = """
        MATCH (u:User {username: $username})-[:PARTICIPATE]->(g:GroupDiscussion)
        RETURN g
        """
        with self._driver.session() as session:
            result = session.run(query, username=username)
            groups = [record['g'] for record in result]
        return groups

    def get_groups_invitation(self, username):
        query = """
        MATCH (u:User {username: $username})-[:INVITATION]->(g:GroupDiscussion)
        RETURN g
        """
        with self._driver.session() as session:
            result = session.run(query, username=username)
            groups = [record["g"] for record in result]
        return groups

    def create_group_message(self, sender, group_name, content):
        with self._driver.session() as session:
            # Création du message
            query_create_message = (
                "MATCH (d:GroupDiscussion) WHERE (d.name = $name )"
                "CREATE (m:Message {sender: $sender, content: $content, timestamp: datetime()}) "
                "MERGE (d)-[:CONTAIN]->(m)"
            )
            session.run(query_create_message, sender=sender, name=group_name, content=content)

    def get_group_messages(self, group_name):
        with self._driver.session() as session:
            query = """
            MATCH (d:GroupDiscussion)
            WHERE (d.name =$name)
            MATCH (d)-[:CONTAIN]-(m:Message)
            RETURN m.content AS content, m.timestamp AS timestamp, m.sender AS sender
            ORDER BY m.timestamp
            """
            result = session.run(query, name = group_name)
            messages = [{"sender": row["sender"], "content": row["content"], "timestamp": row["timestamp"]} for row in result]
            return messages

    def get_group_users(self, group_name):
        with self._driver.session() as session:
            query = """MATCH (u:User)-[:PARTICIPATE]->(g:GroupDiscussion{name: $name})
                    RETURN u.username as username"""
            result = session.run(query, name = group_name)
            usernames = [{"username": row["username"]} for row in result]
            return usernames
    def create_notification(self, recipient_username, notification_type, content, target_id):
        query = """
        MATCH (u:User {username: $recipient_username})
        CREATE (n:Notification {type: $notification_type, content: $content, timestamp: $timestamp, target_id: $target_id})
        MERGE (u)-[:HAS_NOTIFICATION]->(n)
        """
        timestamp = datetime.datetime.now()
        with self._driver.session() as session:
            session.run(query, recipient_username=recipient_username, notification_type=notification_type, content=content, timestamp=timestamp, target_id = target_id)

    def get_notifications(self, username):
        query = """
        MATCH (n:Notification)
        MATCH (u:User {username: $username})
        WHERE (u)-[:HAS_NOTIFICATION]->(n) OR (u)-[:SEE]->(n)
        RETURN n ORDER BY n.timestamp DESC
        """
        with self._driver.session() as session:
            result = session.run(query, username=username)
            notifications = []
            for record in result:
                notifications.append(record['n'])
            return notifications

    def get_unseen_notifications(self, username):
        query = """
        MATCH (u:User {username: $username})-[:HAS_NOTIFICATION]->(n:Notification)
        RETURN n
        """
        with self._driver.session() as session:
            result = session.run(query, username=username)
            notifications = [record["n"] for record in result]
        return notifications

    def mark_notification_as_seen(self, username, notification_id):
        query = """
        MATCH (u:User {username: $username})-[rel:HAS_NOTIFICATION]->(n:Notification)
        WHERE id(n) = $notification_id
        DELETE rel
        CREATE (u)-[:SEE]->(n)
        """
        with self._driver.session() as session:
            session.run(query, username=username, notification_id=notification_id)

    def has_unseen_notification(self, username):
        query = """
        MATCH (u:User {username: $username})-[:HAS_NOTIFICATION]->(n:Notification)
        RETURN COUNT(n) > 0 AS has_unseen
        """
        with self._driver.session() as session:
            result = session.run(query, username=username)
            has_unseen = result.single()["has_unseen"]
        return has_unseen
