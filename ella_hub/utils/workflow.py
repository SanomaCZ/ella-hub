from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from ella.core.models import Publishable

from ella_hub.models import Role, Permission, ModelPermission
from ella_hub.models import State, Transition, Workflow
from ella_hub.models import (StateModelRelation, WorkflowModelRelation,
    WorkflowPermissionRelation, StatePermissionRelation)


def init_ella_workflow(resources):
    """
    Ella workflow specification here.
    """
    workflow = Workflow.objects.get_or_create(title="Ella workflow",
        description="Workflow for Ella publishable-based models.")[0]

    models = []

    # resources filtering, set workflow to only Publishable-subclassed models
    for resource in resources:
        res_model = resource._meta.object_class
        if issubclass(res_model, Publishable) and res_model != Publishable:
            models.append(res_model)

    STATES = (
        _("Added"),
        _("Ready"),
        _("Approved"),
        _("Published"),
        _("Postponed"),
        _("Deleted")
    )

    state_obj_list = []
    perm_obj_list = []

    # create states
    for state_name in STATES:
        s = State.objects.get_or_create(title=unicode(state_name), workflow=workflow)[0]
        state_obj_list.append(s)

    # make all possible transitions
    for state_obj_dest in state_obj_list:
        t = Transition.objects.get_or_create(title="to %s" % state_obj_dest.title,
            workflow=workflow, destination=state_obj_dest)[0]

        for state_obj_src in state_obj_list:
            state_obj_src.transitions.add(t)
            state_obj_src.save()

    # set workflow to all registered models
    for model in models:
        workflow.set_to_model(model)


    ROLES = (
        _("Photographer"),
        _("Editor"),
        _("Editor in chief")
    )

    PERMISSIONS = (
        (_("Can view"), "can_view"),
        (_("Can add"), "can_add"),
        (_("Can edit"), "can_edit"),
        (_("Can delete"), "can_delete"),
        (_("Can publish"), "can_publish"),
        (_("Can view content"), "can_view_content"),
    )

    # create basic roles
    for role_name in ROLES:
        r = Role.objects.get_or_create(title=unicode(role_name))[0]

    # create basic permissions
    for (perm_name, perm_codename) in PERMISSIONS:
        p = Permission.objects.get_or_create(title=unicode(perm_name), codename=perm_codename)[0]
        perm_obj_list.append(p)

    # map permissions to models for roles (only for editor in chief)
    editor_in_chief = Role.objects.get(title="Editor in chief")
    for model in models:
        content_type = ContentType.objects.get_for_model(model)

        for perm_obj in perm_obj_list:
            ModelPermission.objects.get_or_create(role=editor_in_chief,
                permission=perm_obj, content_type=content_type)
        # editor in chief can do anything in every state
        for state_obj in state_obj_list:
            StateModelRelation.objects.get_or_create(state=state_obj,
                content_type=content_type)

    for perm_obj in perm_obj_list:
        WorkflowPermissionRelation.objects.get_or_create(workflow=workflow,
            permission=perm_obj)

        for state_obj in state_obj_list:
            StatePermissionRelation.objects.get_or_create(state=state_obj,
                permission=perm_obj, role=editor_in_chief)

    return workflow


def get_workflow(model):
    content_type = ContentType.objects.get_for_model(model)
    try:
        relation = WorkflowModelRelation.objects.get(content_type=content_type)
    except WorkflowModelRelation.DoesNotExist:
        return None
    else:
        return relation.workflow


def update_permissions(model):
    """
    1. Remove all permissions for the workflow (from ModelPermission relation)
    2. Grant permission for the current state (to ModelPermission relation)
    """
    workflow = get_workflow(model)
    state = get_state(model)

    content_type = ContentType.objects.get_for_model(model)
    perms = [wpr.permission for wpr in WorkflowPermissionRelation.objects.filter(
        workflow=workflow)]

    ModelPermission.objects.filter(content_type=content_type,
        permission__in=perms).delete()

    for relation in StatePermissionRelation.objects.filter(state=state):
        permissions.utils.grant_permission(model, relation.role, relation.permission)


def set_state(model, state):
    content_type = ContentType.objects.get_for_model(model)
    try:
        relation = StateModelRelation.objects.get(content_type=content_type)
    except StateModelRelation.DoesNotExist:
        relation = StateModelRelation.objects.create(content_type=content_type,
            state=state)
    else:
        relation.state = state
        relation.save()
    update_permissions(model)


def get_state(model):
    content_type = ContentType.objects.get_for_model(model)
    try:
        relation = StateModelRelation.objects.get(content_type=content_type)
    except StateModelRelation.DoesNotExist:
        return None
    else:
        return relation.state
