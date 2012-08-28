import unittest

from nose import tools
from django.contrib.auth.models import User
from ella.utils.test_helpers import create_basic_categories
from ella.utils.timezone import now

from ella_hub.models import PublishableLock, Encyclopedia


class TestPublishableLock(unittest.TestCase):
    def setUp(self):
        create_basic_categories(self)
        self.publishable = Encyclopedia.objects.create(title=u"Title like a boss",
            category=self.category, slug="title-article", publish_from=now())

        User.objects.all().delete()
        self.user = self.__create_user("user", "pass", is_admin=True)
        self.locker_user = self.__create_user("lock", "pass", is_admin=True)

        self.lock = PublishableLock.objects.lock(self.publishable,
            self.locker_user)

    def tearDown(self):
        Encyclopedia.objects.all().delete()
        self.user.delete()
        self.locker_user.delete()
        self.lock.delete()

    def __create_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_superuser = is_admin
        user.save()
        return user

    def test_to_string(self):
        tools.assert_equals(unicode(self.lock),
            u"Publishable #%d locked by 'lock'" % self.publishable.id)

    def test_double_lock(self):
        lock = PublishableLock.objects.lock(self.publishable, self.user)
        tools.assert_false(lock)

    def test_lock_is_working(self):
        locked = PublishableLock.objects.is_locked(self.publishable)
        tools.assert_true(locked)

        PublishableLock.objects.unlock(self.publishable)

        locked = PublishableLock.objects.is_locked(self.publishable)
        tools.assert_false(locked)
