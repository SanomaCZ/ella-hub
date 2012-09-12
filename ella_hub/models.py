from django.db import models, IntegrityError
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date
from object_permissions import register

from ella.core.models import Author, Category, Source, Listing, Publishable
from ella.core.admin import PublishableAdmin
from ella.articles.models import Article
from ella.photos.models import Photo

from jsonfield import JSONField


class Draft(models.Model):
    """Auto-saved objects and user templates."""

    content_type = models.ForeignKey(ContentType, verbose_name=_("Model"))
    user = models.ForeignKey(User, verbose_name=_("User"))
    name = models.CharField(_("Name"), max_length=64, blank=True)
    timestamp = models.DateTimeField(editable=False, auto_now=True)
    data = JSONField(_("Data"))

    def __unicode__(self):
        if self.name != "":
            return u"%s (%s)" % (self.name, date(self.timestamp, "y-m-d H:i"))
        else:
            return u"%s %s (%s)" % (_("Autosaved"), _(self.content_type.name),
                date(self.timestamp, "y-m-d H:i"))

    class Meta:
        verbose_name = _("Draft item")
        verbose_name_plural = _("Draft items")
        ordering = ("-timestamp",)


class PublishableLockManager(models.Manager):
    def lock(self, publishable, user):
        try:
            return self.create(publishable=publishable, locked_by=user)
        except IntegrityError:
            # duplicate entry 'publishable'
            return None

    def is_locked(self, publishable):
        try:
            return self.get(publishable=publishable)
        except PublishableLock.DoesNotExist:
            return None

    def unlock(self, publishable):
        return self.filter(publishable=publishable).delete()


class PublishableLock(models.Model):
    """Lock for publishable objects."""

    objects = PublishableLockManager()

    publishable = models.ForeignKey(Publishable, unique=True,
        verbose_name=_("Locked publishable"))
    locked_by = models.ForeignKey(User)
    timestamp = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return _("Publishable #%d locked by '%s'") % (
            self.publishable.id,
            self.locked_by.username,
        )

    class Meta:
        verbose_name = _("Publishable lock")
        verbose_name_plural = _("Publishable locks")


COMMENTS_CHOICES = (
    ("all", _("All")),
    ("registered", _("Registered")),
    ("nobody", _("Nobody")),
)

PUBLISHABLE_STATES = (
        ("added", _("Added")),
        ("ready", _("Ready")),
        ("approved", _("Approved")),
        ("published", _("Published")),
        ("postponed", _("Postponed")),
        ("deleted", _("Deleted")),
    )

class BaseArticle(Publishable):
    updated = models.DateTimeField(_("Updated"), null=True)
    commercial = models.BooleanField(verbose_name=_("Commercial"), default=False)
    photo_displayed = models.BooleanField(verbose_name=_("Display perex photo"), default=True)
    enable_comments = models.CharField(_("Article comments"), max_length=16,
        choices=COMMENTS_CHOICES, default=COMMENTS_CHOICES[0][0])
    state = models.CharField(_("State"), choices=PUBLISHABLE_STATES, max_length=36,
        default=PUBLISHABLE_STATES[0][0])

    class Meta:
        abstract = True


class CommonArticle(BaseArticle):
    """Common article."""

    content = models.TextField(_("Text"), blank=True)

    def __init__(self, *args, **kwargs):
        super(CommonArticle, self).__init__(*args, **kwargs)
        self._meta.get_field("description").verbose_name = _("Perex")

    def __unicode__(self):
        return u"%s: %s" % (_("Article"), self.title)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")


class Encyclopedia(BaseArticle):
    """Encyclopedia article."""

    content = models.TextField(_("Description"), blank=True)

    def __init__(self, *args, **kwargs):
        super(Encyclopedia, self).__init__(*args, **kwargs)
        self._meta.get_field("photo_displayed").default = False

    def __unicode__(self):
        return u"%s: %s" % (_("Encyclopedia"), self.title)

    class Meta:
        verbose_name = _("Encyclopedia")
        verbose_name_plural = _("Encyclopedia")


RECIPE_OCCASIONS = (
    ("grill", _("Grill")),
    ("christmas", _("Christmas")),
    ("easter", _("Easter or Pancake Day")),
    ("party", _("Parties and celebrations")),
    ("wedding", _("Wedding")),
    ("feast", _("Feast")),
    ("birthday", _("Birthday")),
    ("new_year", _("New Year's Eve")),
)


RECOMENDED_TO_CHOICES = (
    ("for_diabetics", _("For diabetics")),
    ("for_childs", _("For childs")),
    ("for_vegetarians", _("For vegetarians")),
    ("for_diet", _("For diet")),
    ("without_gluten", _("Without gluten")),
    ("milk_allergy", _("Milk Allergy")),
    ("for_bread_machines", _("For bread machines")),
)


KITCHEN_TYPES = (
    ("african", _("African")),
    ("arab", _("Arab")),
    ("asian", _("Asian")),
    ("australian", _("Australian")),
    ("balkan", _("Balkan")),
    ("british", _("British")),
    ("bulgaria", _("Bulgaria")),
    ("czech", _("Czech")),
    ("chinese", _("Chinese")),
    ("european", _("European")),
    ("french", _("French")),
    ("indian", _("Indian")),
    ("italian", _("Italian")),
    ("japanese", _("Japanese")),
    ("south_american", _("South American")),
    ("caucasian", _("Caucasian")),
    ("korea", _("Korea")),
    ("hungary", _("Hungary")),
    ("mexican", _("Mexican")),
    ("german", _("German")),
    ("baltic", _("Baltic")),
    ("polish", _("Polish")),
    ("austria", _("Austria")),
    ("russian", _("Russian")),
    ("greek", _("Greek")),
    ("north american", _("North american")),
    ("scandinavian", _("Scandinavian")),
    ("slovak", _("Slovak")),
    ("middle_american", _("Middle American")),
    ("mediterranean", _("Mediterranean")),
    ("spanish", _("Spanish")),
    ("thai", _("Thai")),
    ("the_vietnamese", _("The Vietnamese")),
    ("jewish", _("Jewish")),
)


RECOMENDED_BY_CHOICES = (
    ("confectioner", _("Confectioner (desserts)")),
    ("dietitian", _("Dietitian (diet and healthy)")),
    ("farmer", _("Farmer (seasonal)")),
    ("editors", _("Editors (editorial)")),
    ("readers", _("READERS (favorite, tried-readers)")),
    ("student", _("Student (cheap)")),
    ("mum", _("Mum (quick and easy)")),
    ("chefs", _("Chefs (gastronomic)")),
    ("grandmother", _("Grandmother (Traditional)")),
    ("celebrity", _("CELEBRITY (from VIP)")),
)


DIFFICULTIES = (
    ("easy", _("Easy")),
    ("middle", _("Moderately difficult")),
    ("difficult", _("Difficult")),
)


RECIPE_TYPES = (
    ("editorial", _("Editorial")),
    ("readers", _("Readers")),
)


class Recipe(BaseArticle):
    """Article with recipe."""

    redaction_note = models.TextField(_("Note"), blank=True)
    occasion = models.CharField(_("Occasion"), max_length=32, blank=True,
        choices=RECIPE_OCCASIONS)
    recommended_to = models.CharField(_("Recommended to"), max_length=32,
        blank=True, choices=RECOMENDED_TO_CHOICES)
    kitchen_type = models.CharField(_("Kitchen type"), max_length=32,
        blank=True, choices=KITCHEN_TYPES)
    recommended_by = models.CharField(_("Recommended by"), max_length=32,
        blank=True, choices=RECOMENDED_BY_CHOICES)
    portion_count = models.PositiveIntegerField(_("Portion count"), null=True)
    difficulty = models.CharField(_("Difficulty"), max_length=16, blank=True,
        choices=DIFFICULTIES)
    cook_time = models.PositiveIntegerField(_("Cook time (in minutes)"))
    type = models.CharField(_("Type"), max_length=16, choices=RECIPE_TYPES,
        default=RECIPE_TYPES[0][0])
    rank = models.PositiveIntegerField(_("Rank"), default=0)

    def __init__(self, *args, **kwargs):
        super(Recipe, self).__init__(*args, **kwargs)
        self._meta.get_field("description").verbose_name = _("Directions")

    def __unicode__(self):
        return u"%s: %s" % (_("Recipe"), self.title)

    class Meta:
        verbose_name = _("Recipe")
        verbose_name_plural = _("Recipes")


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, verbose_name=_("Recipe"))
    name = models.CharField(_("Ingredient name"), max_length=128)

    amount = models.PositiveIntegerField(_("Amount"))
    amount_unit = models.CharField(_("Amount unit"), max_length=32)

    note = models.TextField(_("Note"), blank=True)
    type = models.CharField(_("Ingredient type"), blank=True, max_length=128)

    def __unicode__(self):
        return u"%s: %s" % (_("Recipe ingredient"), self.recipe.title)

    class Meta:
        verbose_name = _("Recipe ingredient")
        verbose_name_plural = _("Recipe ingredients")


def register_object_permissions():
    CLASSES = (
        ('author', Author, 'core'),
        ('user', User, 'auth'),
        ('category', Category, 'core'),
        ('source', Source, 'core'),
        ('listing', Listing, 'core'),
        ('site', Site, 'sites'),
        ('photo', Photo, 'photos'),
        ('article', CommonArticle, 'ella_hub'),
        ('recipe', Recipe, 'ella_hub'),
        ('encyclopedia', Encyclopedia, 'ella_hub'),
    )
    for class_str, class_, app_label in CLASSES:
        register(['view_%s' % class_str, 'change_%s' %class_str,
            'delete_%s' %class_str], class_ , app_label)


register_object_permissions()
