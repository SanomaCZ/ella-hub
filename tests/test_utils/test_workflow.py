from nose import tools
from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser, Group
from django.test.client import Client

from ella.core.models import Author

from ella_hub.models import Workflow, State
from ella_hub.utils.workflow import set_state, get_state


class TestWorkflowUtils(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test author")
        self.user = self.__create_test_user("user", "pass1")
        self.workflow = Workflow.objects.create(title="Test workflow")
        self.state1 = State.objects.create(title="Test state 1",
            codename="test_1")
        self.state2 = State.objects.create(title="Test state 2",
            codename="test_2")
        self.client = Client()

    def tearDown(self):
        self.author.delete()
        self.user.delete()
        self.workflow.delete()
        State.objects.all().delete()

    def test_set_state(self):
        set_state(self.author, self.state1)
        set_state(self.author, self.state2)
        tools.assert_equals(get_state(self.author), self.state2)

    def test_get_state(self):
        tools.assert_equals(get_state(self.author), None)

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user
