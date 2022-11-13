from time import strftime
from datetime import datetime

from django.test import TestCase

from network.models import User, Post, ViewedPost, Comment, Reaction


class TestModels(TestCase):
    """
    Set of tests to test applications models behaviour.
    """

    def setUp(self):
        """
        Set of fixtures to use in tests.
        """
        self.user1 = User(
            username = 'user1',
            password = 'password',
            first_name = "User1",
            last_name = "Useroff",
            email = "user1@test.com"
        )
        self.user1.save()

        self.user2 = User(
            username = 'user2',
            password = 'password',
            first_name = "User2",
            last_name = "Useroff",
            email = "user2@test.com"
        )
        self.user2.save()

        self.post1 = Post(
            title = "post",
            body = "post text",
            created_by = self.user1
        )
        self.post1.save()
        
    def test_user_repr(self):
        # test string representation of User instance
        self.assertTrue(
            str(self.user1) == "user1"
            )

    def test_user_last_seen(self):
        # test User last_seen property displays last seen lost
        viewed = ViewedPost(viewer = self.user2, viewed_post = self.post1)
        viewed.save()

        self.assertEqual(self.user2.last_seen, viewed.viewed_post)

    def test_post_repr(self):
        # test string representation of Post instance and autoset created_on are correct
        self.assertEqual(
            str(self.post1), 
            f"Post. Published on {datetime.today().strftime('%Y-%m-%d')}"
            )

    def test_add_post_to_viewed(self):
        # test User 'last_seen' property returns last seen post
        self.user2.viewed_posts.add(self.post1)

        self.assertTrue(self.user2.last_seen == self.post1)


    def test_comment_repr(self):
        # test string representation of Comment instance and autoset created_on are correct
        comment = Comment(
            post = self.post1,
            body = "Some comment",
            created_by = self.user2
        )
        comment.save()

        self.assertEqual(
            str(comment), 
            f"user2 comments to post 'Post' on {datetime.today().strftime('%Y-%m-%d')}"
            )

    def test_reaction_repr_and_creation_date(self):
        # test string representation of Reaction instance and autoset created_on are correct
        reaction = Reaction(
            post = self.post1,
            user = self.user2,
            status = 'L'
        )
        reaction.save()

        self.assertEqual(reaction.created_on.date(), datetime.today().date())

        self.assertEqual(
            str(reaction),
            f"Reaction of {self.user2} to post {self.post1.title}"
        )
