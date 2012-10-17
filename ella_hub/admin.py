from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from ella.core.admin import PublishableAdmin, ListingInlineAdmin, RelatedInlineAdmin

from ella_hub.models import Draft, CommonArticle, Encyclopedia, Recipe, RecipeIngredient
from ella_hub.models import Permission, Role, ModelPermission, PrincipalRoleRelation
from ella_hub.models import (Workflow, State, Transition, StatePermissionRelation,
    StateObjectRelation, WorkflowModelRelation, WorkflowPermissionRelation)


class ArticleAdmin(PublishableAdmin):
    ordering = ("-publish_from",)
    fieldsets = (
        (_("Article heading"), {"fields": ("title", "slug")}),
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
        (_("Article heading"), {"fields": ("title", "slug")}),
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
        (_("Article heading"), {"fields": ("title", "slug")}),
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


admin.site.register(Draft)
admin.site.register(CommonArticle, ArticleAdmin)
admin.site.register(Encyclopedia, EncyclopediaAdmin)
admin.site.register(Recipe, RecipeAdmin)


class PermissionAdmin(admin.ModelAdmin):
    exclude = ("content_types",)


admin.site.register(Permission, PermissionAdmin)
admin.site.register(Role)
admin.site.register(ModelPermission)


class PrincipalRoleRelationAdmin(admin.ModelAdmin):
    exclude = ("content_type", "content_id")

admin.site.register(PrincipalRoleRelation, PrincipalRoleRelationAdmin)

admin.site.register(Workflow)
admin.site.register(State)
admin.site.register(Transition)
admin.site.register(StatePermissionRelation)
admin.site.register(StateObjectRelation)
admin.site.register(WorkflowModelRelation)
admin.site.register(WorkflowPermissionRelation)
