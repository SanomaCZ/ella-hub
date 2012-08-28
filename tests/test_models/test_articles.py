# -*- coding: utf-8 -*-

from django.test import TestCase

from nose import tools
from django.utils.translation import ugettext_lazy as _
from ella.utils.test_helpers import create_basic_categories
from ella.utils import timezone

from ella_hub.models import CommonArticle, Recipe, Encyclopedia, PagedArticle


class TestArticleModels(TestCase):
    def setUp(self):
        create_basic_categories(self)
        self.article = CommonArticle.objects.create(title="Jop",
            category=self.category, publish_from=timezone.now(), slug="jop")
        self.recipe = Recipe.objects.create(title="Spinach", category=self.category_nested,
            publish_from=timezone.now(), slug="spinach", cook_time=30)
        self.encyclopedia = Encyclopedia.objects.create(title="Jop3", category=self.category,
            publish_from=timezone.now(), slug="jop3")
        self.paged_article = PagedArticle.objects.create(title="Jop4", category=self.category,
            publish_from=timezone.now(), slug="jop4")

    def tearDown(self):
        CommonArticle.objects.all().delete()
        Recipe.objects.all().delete()
        Encyclopedia.objects.all().delete()
        PagedArticle.objects.all().delete()

    def test_to_string(self):
        # common article
        tools.assert_equals(unicode(self.article), u"%s: %s" % (
            _("Article"), self.article.title))

        self.article.title = u"Some title ľščťžýáíé"
        self.article.save()

        tools.assert_equals(unicode(self.article), u"%s: %s" % (
            _("Article"), self.article.title))

        # recipe
        tools.assert_equals(unicode(self.recipe), u"%s: %s" % (
            _("Recipe"), self.recipe.title))

        self.recipe.title = u"Some title ľščťžýáíé"
        self.recipe.save()

        tools.assert_equals(unicode(self.recipe), u"%s: %s" % (
            _("Recipe"), self.recipe.title))

        # encyclopedia
        tools.assert_equals(unicode(self.encyclopedia), u"%s: %s" % (
            _("Encyclopedia"), self.encyclopedia.title))

        self.encyclopedia.title = u"Some title ľščťžýáíé"
        self.encyclopedia.save()

        tools.assert_equals(unicode(self.encyclopedia), u"%s: %s" % (
            _("Encyclopedia"), self.encyclopedia.title))

        # paged article
        tools.assert_equals(unicode(self.paged_article), u"%s: %s" % (
            _("Paged article"), self.paged_article.title))

        self.paged_article.title = u"Some title ľščťžýáíé"
        self.paged_article.save()

        tools.assert_equals(unicode(self.paged_article), u"%s: %s" % (
            _("Paged article"), self.paged_article.title))
