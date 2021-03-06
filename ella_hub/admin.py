from django.contrib import admin

from ella_hub.models import Draft
from ella_hub.models import Permission, Role, ModelPermission, PrincipalRoleRelation
from ella_hub.models import (
    Workflow,
    State,
    Transition,
    StatePermissionRelation,
    StateObjectRelation,
    WorkflowModelRelation,
    WorkflowPermissionRelation,
)


class PermissionAdmin(admin.ModelAdmin):
    exclude = ("content_types",)


admin.site.register(Permission, PermissionAdmin)
admin.site.register(Role)
admin.site.register(ModelPermission)


class PrincipalRoleRelationAdmin(admin.ModelAdmin):
    exclude = ("content_type", "content_id")


admin.site.register(Draft)
admin.site.register(Workflow)
admin.site.register(State)
admin.site.register(Transition)
admin.site.register(StatePermissionRelation)
admin.site.register(StateObjectRelation)
admin.site.register(WorkflowModelRelation)
admin.site.register(WorkflowPermissionRelation)
admin.site.register(PrincipalRoleRelation, PrincipalRoleRelationAdmin)
