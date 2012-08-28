# -*- coding: utf-8 -*-

from django.test import TestCase

from nose import tools
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from ella.core.models import Author
from ella.articles.models import Article
from ella_hub.models import Draft


class TestDraftModel(TestCase):
    def setUp(self):
        article_type = ContentType.objects.get(name__iexact="article")
        author_type = ContentType.objects.get(name__iexact="author")

        self.user = user = User.objects.create_user(username="user", password="pass")

        self.article_draft = Draft.objects.create(content_type=article_type,
            user=self.user, name="Article draft",
            data={"about": "this is nothing", "useless": [True, False]})

        self.author_draft = Draft.objects.create(content_type=author_type,
            user=self.user, name="Author draft",
            data={"name": "Olivia Wilde", "nick": "thirteen"})

    def tearDown(self):
        self.user.delete()
        Draft.objects.all().delete()

    def test_get_article_draft(self):
        draft = Draft.objects.get(content_type__name__iexact="article")
        tools.assert_equals(draft.name, "Article draft")
        tools.assert_equals(draft.data,
            {"about": "this is nothing", "useless": [True, False]})

    def test_get_author_draft(self):
        draft = Draft.objects.get(content_type__name__iexact="author")
        tools.assert_equals(draft.name, "Author draft")
        tools.assert_equals(draft.data,
            {"name": "Olivia Wilde", "nick": "thirteen"})

    def test_draft_to_string(self):
        content_type = ContentType.objects.get(name__iexact="article")
        draft = Draft.objects.create(content_type=content_type,
            user=self.user, data="payload")

        tools.assert_equals(unicode(draft), u"%s %s (%s)" % (
            _("Autosaved"), _(content_type.name), date(draft.timestamp, 'y-m-d H:i')))

        draft.name = u"Some title ľščťžýáíé"
        draft.save()

        tools.assert_equals(unicode(draft),
            u"%s (%s)" % (u"Some title ľščťžýáíé", date(draft.timestamp, 'y-m-d H:i')))

        draft.delete()
