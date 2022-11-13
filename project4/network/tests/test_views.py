from django.test import TestCase
from django.urls import reverse

from network.models import User, Post, ViewedPost, Comment, Reaction


class TestViews(TestCase):
    """
    Set-up to test views logic.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set of fixtures to use in tests.
        """
        User.objects.create_user(
            username = 'user1',
            password = 'password',
            first_name = "User1",
            last_name = "Useroff",
            email = "user1@test.com"
        )

        User.objects.create_user(
            username = 'user2',
            password = 'password',
            first_name = "User2",
            last_name = "Useroff",
            email = "user2@test.com"
        )

        Post.objects.create(
            title = "post",
            body = "post text",
            created_by = User.objects.get(id=1)
        )


class TestHomepageView(TestViews):
    """
    Set of tests to check Homepage view logic.
    """

    def setUp(self):
        # general setup used in each test
        self.user = User.objects.get(id=1)

    def test_homepage_url(self):
        # Check if url is reachable, url naming works
        response = self.client.get("/", follow=True)

        self.assertEqual(response.status_code, 200)

    def test_anonymous_access(self):
        # Check if anonymous user is redirected to SignUp page.
        response = self.client.get(reverse('index'), follow=True)

        self.assertFalse(response.context["user"].is_authenticated)
        self.assertTemplateUsed('/network/register.html')

    def test_authenticated_access(self):
        # Check if Home page is displayed to logged in user
        self.client.force_login(self.user)

        response = self.client.get(reverse('index'))

        self.assertTemplateUsed('/network/index.html')
        self.assertTrue(response.context['user'].is_authenticated)

class TestRegisterView(TestViews):
    """
    Set of tests to check Register page login.
    """
    
    def test_register_view_url(self):
        # Check if url is reachable, url naming works
        response = self.client.get("/register")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("/network/register.html")

    def test_wrong_confirmation(self):
        # Check if view throws an error in case of password and confirmation are not equal
        response = self.client.post(reverse("register"), {
            'username': 'user1',
            'email': 'some@email',
            'password': 'test',
            'confirmation': 'test1'
            })

        # staying on register view
        self.assertTemplateUsed("/network/register.html")
        # respective error message is displayed
        self.assertContains(response, 'Passwords must match.')

    def test_used_username(self):
        # Check if view throws an error in case of non-unique username
        response = self.client.post(reverse("register"), {
            'username': 'user1',
            'email': 'some@email',
            'password': 'test',
            'confirmation': 'test'
            })

        # staying on register view
        self.assertTemplateUsed("/network/register.html")
        # respective error message is displayed
        self.assertContains(response, 'Username already taken.')

    def test_successful_registration(self):
        # Check if view throws an error in case of non-unique username
        response = self.client.post(reverse("register"), {
            'username': 'user3',
            'email': 'some@email',
            'password': 'test',
            'confirmation': 'test'
            }, follow=True)

        # get newly sreated user from DB
        user = User.objects.get(username='user3')

        # check if user3 is logged in
        self.assertTrue(response.context["user"].is_authenticated)
        # check if user is redirected to the home page
        self.assertTemplateUsed('/network/index.html')
        self.assertRedirects(response, reverse('index'))

class TestLoginView(TestViews):
    """
    Set of tests to check Login view behaviour.
    """

    def test_login_view_url(self):
        # Check if url is reachable, url naming works, correct template is used
        response = self.client.get('/login')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('network/login.html')

    def test_invalid_username(self):
        # check if error is thrown on non-existing username input
        response = self.client.post(reverse("login"), {'username': 'invalid_user', 'password': 'password'})

        self.assertFalse(response.context["user"].is_authenticated)
        self.assertTemplateUsed("network/login.html")
        self.assertContains(response, "Invalid username and/or password.")

    def test_invalid_password(self):
        # check if error is thrown on non-existing username input
        response = self.client.post(reverse("login"), {'username': 'user1', 'password': 'invalid_password'})

        self.assertFalse(response.context["user"].is_authenticated)
        self.assertTemplateUsed("network/login.html")
        self.assertContains(response, "Invalid username and/or password.")

    def test_successful_login(self):
        # check if error is thrown on non-existing username input
        response = self.client.post(reverse("login"), {'username': 'user1', 'password': 'password'}, follow=True)

        self.assertTrue(response.context["user"].is_authenticated)
        self.assertTemplateUsed("network/index.html")

class TestLogoutView(TestViews):
    """
    Set of tests to check Logout view behaviour.
    """

    def setUp(self):
        # login user
        self.client.force_login(User.objects.get(id=1))

    def test_user_logged_out_and_redirected(self):
        # check if user is logged out and redirected to register view through index view
        response = self.client.get('/')

        # check first if user is logged in
        self.assertTrue(response.context["user"].is_authenticated)

        # log user out
        response = self.client.get("/logout", follow=True)

        # check user is logged out
        self.assertFalse(response.context["user"].is_authenticated)
        # check if user is redirected to register view
        self.assertTemplateUsed("network/register.html")
