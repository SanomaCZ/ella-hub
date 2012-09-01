from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ella.core.admin import PublishableAdmin, ListingInlineAdmin, RelatedInlineAdmin
from ella_hub.models import Draft, CommonArticle, Encyclopedia, PagedArticle, ArticlePage, Recipe, RecipeIngredient


class ArticleAdmin(PublishableAdmin):
    ordering = ("-publish_from",)
    fieldsets = (
        (_("Article heading"), {"fields": ("title", "upper_title", "slug", "state")}),
        (_("Article contents"), {"fields": ("description", "content")}),
        (_("Metadata"), {"fields": ("category", "authors", "source",
            ("photo", "photo_displayed"))}),
        (_("Publication"), {"fields": (
            ("publish_from", "publish_to", "updated"),
            ("enable_comments", "published", "static", "commercial"),
        )}),
    )
    inlines = [ListingInlineAdmin, RelatedInlineAdmin]


class EncyclopediaAdmin(PublishableAdmin):
    ordering = ("-publish_from",)
    fieldsets = (
        (_("Article heading"), {"fields": ("title", "upper_title", "slug", "state")}),
        (_("Article contents"), {"fields": ("description", "content")}),
        (_("Metadata"), {"fields": ("category", "authors", "source",
            ("photo", "photo_displayed"))}),
        (_("Publication"), {"fields": (
            ("publish_from", "publish_to", "updated"),
            ("enable_comments", "published", "static", "commercial"),
        )}),
    )
    inlines = [ListingInlineAdmin, RelatedInlineAdmin]


class IngredientInlineAdmin(admin.StackedInline):
    model = RecipeIngredient
    fieldsets = ((
        None, {"fields": (
            ("amount", "amount_unit", "name"),
            "note",
            "type",
        )}
    ),)


class RecipeAdmin(PublishableAdmin):
    ordering = ("-publish_from",)
    fieldsets = (
        (_("Article heading"), {"fields": ("title", "upper_title", "slug", "state")}),
        (_("Article contents"), {"fields": (
            "description",
            "redaction_note",
            ("cook_time", "type", "rank"),
            ("occasion", "recommended_to", "recommended_by", "kitchen_type"),
            ("portion_count", "difficulty")
        )}),
        (_("Metadata"), {"fields": ("category", "authors", "source",
            ("photo", "photo_displayed"))}),
        (_("Publication"), {"fields": (
            ("publish_from", "publish_to", "updated"),
            ("enable_comments", "published", "static", "commercial"),
        )}),
    )
    inlines = [IngredientInlineAdmin, ListingInlineAdmin, RelatedInlineAdmin]


class PageInlineAdmin(admin.StackedInline):
    model = ArticlePage
    fieldsets = ((
        None, {"fields": (
            ("page_number", "content"),
        )}
    ),)


class PagedArticleAdmin(PublishableAdmin):
    ordering = ("-publish_from",)
    fieldsets = (
        (_("Article heading"), {"fields": ("title", "upper_title", "slug", "state")}),
        (_("Article contents"), {"fields": ("description",)}),
        (_("Metadata"), {"fields": ("category", "authors", "source",
            ("photo", "photo_displayed"))}),
        (_("Publication"), {"fields": (
            ("publish_from", "publish_to", "updated"),
            ("enable_comments", "published", "static", "commercial"),
        )}),
    )
    inlines = [PageInlineAdmin, ListingInlineAdmin, RelatedInlineAdmin]


admin.site.register(Draft)
admin.site.register(CommonArticle, ArticleAdmin)
admin.site.register(Encyclopedia, EncyclopediaAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(PagedArticle, PagedArticleAdmin)
