import unittest

from nose import tools
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from ella.utils.test_helpers import create_basic_categories

from ella_hub.utils.timezone import now
from ella_hub.models import PublishableLock, Encyclopedia
from ella_hub.exceptions import PublishableLocked


class TestPublishableLock(unittest.TestCase):
    def setUp(self):
        create_basic_categories(self)
        self.publishable = Encyclopedia.objects.create(title="Title like a boss",
            category=self.category, slug="title-article", publish_from=now())
        self.user = User.objects.create_user(username="user", password="pass")
        self.lock = PublishableLock.objects.create(publishable=self.publishable,
            user=self.user, locked=True)

    def tearDown(self):
        Encyclopedia.objects.all().delete()
        self.user.delete()
        self.lock.delete()

    def test_to_string(self):
        self.lock.locked = True
        self.lock.save()
        tools.assert_equals(unicode(self.lock),
            u"Locked publishable #%d for user 'user'" % self.publishable.id)

        self.lock.locked = False
        self.lock.save()
        tools.assert_equals(unicode(self.lock),
            u"Unlocked publishable #%d for user 'user'" % self.publishable.id)

    @tools.raises(PublishableLocked)
    def test_article_locked(self):
        self.lock.locked = True
        self.lock.save()
        self.publishable.title = u"New fancy title"
        self.publishable.save()
