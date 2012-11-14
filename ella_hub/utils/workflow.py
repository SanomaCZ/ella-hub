from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable

from ella_hub.models import CommonArticle
from ella_hub.models import Role, Permission, ModelPermission, PrincipalRoleRelation
from ella_hub.models import State, Transition, Workflow
from ella_hub.models import (StateObjectRelation, WorkflowModelRelation,
    WorkflowPermissionRelation, StatePermissionRelation)
from ella_hub.utils.perms import grant_permission


def init_ella_workflow(resources):
    """
    Ella workflow specification here.
    """
    workflow = Workflow.objects.get_or_create(title="Ella workflow",
        description="Workflow for Ella publishable-based models.")[0]

    editor_in_chief = Role.objects.get_or_create(title=unicode(_("Editor in chief")))[0]

    STATES = (
        (_("Added"), "added"),
        (_("Ready"), "ready"),
        (_("Approved"), "approved"),
        (_("Published"), "published"),
        (_("Postponed"), "postponed"),
        (_("Deleted"), "deleted")
    )

    PERMISSIONS = (
        (_("Can view"), "can_view"),
        (_("Can add"), "can_add"),
        (_("Can edit"), "can_change"),
        (_("Can delete"), "can_delete"),
    )

    all_models = [resource._meta.object_class for resource in resources]
    publishable_models = [model for model in all_models
        if issubclass(model, Publishable) and model != Publishable]

    state_obj_list = []
    perm_obj_list = []

    state_obj_list = _create_states(STATES, workflow)
    workflow.initial_state = state_obj_list[0]
    workflow.save()

    _make_all_possible_transitions(state_obj_list, workflow)

    # set workflow to all models
    for model in all_models:
        workflow.set_to_model(model)

    # create basic permissions
    for (perm_name, perm_codename) in PERMISSIONS:
        p = Permission.objects.get_or_create(title=unicode(perm_name), codename=perm_codename)[0]
        perm_obj_list.append(p)

    # map permissions to models for roles (only for editor in chief)
    for model in all_models:
        content_type = ContentType.objects.get_for_model(model)
        for perm_obj in perm_obj_list:
            ModelPermission.objects.get_or_create(role=editor_in_chief,
                permission=perm_obj, content_type=content_type)

    for perm_obj in perm_obj_list:
        WorkflowPermissionRelation.objects.get_or_create(workflow=workflow,
            permission=perm_obj)

        for state_obj in state_obj_list:
            StatePermissionRelation.objects.get_or_create(state=state_obj,
                permission=perm_obj, role=editor_in_chief)

    ##### Editor
    editor = Role.objects.get_or_create(title=unicode(_("Editor")))[0]

    STATES = (
        (_("Added"), "added"),
        (_("Ready"), "ready"),
        (_("Deleted"), "deleted")
    )

    # create states
    added_state = State.objects.get_or_create(title=unicode(_("Added")),
        codename="added", workflow=workflow)[0]
    ready_state = State.objects.get_or_create(title=unicode(_("Ready")),
        codename="ready", workflow=workflow)[0]
    deleted_state = State.objects.get_or_create(title=unicode(_("Deleted")),
        codename="deleted", workflow=workflow)[0]

    all_models = [resource._meta.object_class for resource in resources]
    publishable_models = [model for model in all_models
        if issubclass(model, Publishable) and model != Publishable]

    state_obj_list = _create_states(STATES, workflow)

    to_added = Transition.objects.get_or_create(title="to %s" % added_state.title,
            workflow=workflow, destination=added_state)[0]
    to_ready = Transition.objects.get_or_create(title="to %s" % ready_state.title,
            workflow=workflow, destination=ready_state)[0]
    to_deleted = Transition.objects.get_or_create(title="to %s" % deleted_state.title,
            workflow=workflow, destination=deleted_state)[0]

    added_state.transitions.add(to_added)
    added_state.transitions.add(to_ready)
    added_state.transitions.add(to_deleted)
    ready_state.transitions.add(to_added)
    ready_state.transitions.add(to_ready)
    deleted_state.transitions.add(to_added)
    deleted_state.transitions.add(to_deleted)

    # only view permissions
    for model in all_models:
        content_type = ContentType.objects.get_for_model(model)
        for perm_obj in perm_obj_list[:1]:
            ModelPermission.objects.get_or_create(role=editor,
                permission=perm_obj, content_type=content_type)

    for perm_obj in perm_obj_list[:1]:
        WorkflowPermissionRelation.objects.get_or_create(workflow=workflow,
            permission=perm_obj)

        for state_obj in state_obj_list:
            StatePermissionRelation.objects.get_or_create(state=state_obj,
                permission=perm_obj, role=editor)

    r = Permission.objects.get_or_create(title="Readonly content",
        restriction=True, codename="readonly_content")[0]
    d = Permission.objects.get_or_create(title="Disabled authors",
        restriction=True, codename="disabled_authors")[0]

    content_type = ContentType.objects.get_for_model(CommonArticle)

    ModelPermission.objects.get_or_create(role=editor,
        permission=r, content_type=content_type)
    ModelPermission.objects.get_or_create(role=editor,
        permission=d, content_type=content_type)

    WorkflowPermissionRelation.objects.get_or_create(workflow=workflow,
        permission=r)
    WorkflowPermissionRelation.objects.get_or_create(workflow=workflow,
        permission=d)

    for state_obj in state_obj_list:
        StatePermissionRelation.objects.get_or_create(state=state_obj,
            permission=r, role=editor)
        StatePermissionRelation.objects.get_or_create(state=state_obj,
            permission=d, role=editor)

    return workflow


def _create_states(states, workflow):
    state_obj_list = []
    for state_name, state_codename in states:
        s = State.objects.get_or_create(title=unicode(state_name),
            codename=state_codename, workflow=workflow)[0]
        state_obj_list.append(s)
    return state_obj_list


def _make_all_possible_transitions(state_obj_list, workflow):
    for state_obj_dest in state_obj_list:
        t = Transition.objects.get_or_create(title="to %s" % state_obj_dest.title,
            workflow=workflow, destination=state_obj_dest)[0]

        for state_obj_src in state_obj_list:
            state_obj_src.transitions.add(t)
            state_obj_src.save()


def get_workflow(model):
    """
    Returns workflow set to <model>.
    """
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
        grant_permission(model, relation.role, relation.permission)


def set_state(obj, state):
    """
    Sets <state> of <obj>.
    """
    if not isinstance(state, State):
        try:
            state = State.objects.get(codename=state)
        except State.DoesNotExist:
            return False

    content_type = ContentType.objects.get_for_model(obj)
    try:
        relation = StateObjectRelation.objects.get(content_type=content_type,
            content_id=obj.id)
    except StateObjectRelation.DoesNotExist:
        relation = StateObjectRelation.objects.create(content_object=obj,
            state=state)
    else:
        relation.state = state
        relation.save()
    update_permissions(obj)
    return True


def get_state(obj):
    """
    Returns state of <obj>.
    """
    content_type = ContentType.objects.get_for_model(obj)
    try:
        relation = StateObjectRelation.objects.get(content_id=obj.pk,
            content_type=content_type)
    except StateObjectRelation.DoesNotExist:
        return None
    else:
        return relation.state


def get_init_states(model, user, workflow=None):
    """
    Returns initial state of <workflow> set to <model>
    - vsetky stavy, do ktorych sa je mozne z init stavu dostat
    """
    content_type = ContentType.objects.get_for_model(model)
    init_state = []

    if workflow:
        init_state = workflow.initial_state
    else:
        try:
            workflow = WorkflowModelRelation.objects.get(content_type=content_type).workflow
        except WorkflowModelRelation.DoesNotExist:
            return []

    if user.is_superuser:
        roles = [relation.role for relation in PrincipalRoleRelation.objects.all()]
    else:
        relations = PrincipalRoleRelation.objects.filter(user=user)
        roles = [relation.role for relation in relations]

    relations = ModelPermission.objects.filter(content_type=content_type,
        role__in=roles)

    perms = [relation.permission for relation in relations]

    relations = StatePermissionRelation.objects.filter(role__in=roles,
        permission__in=perms)
    states = _remove_duplicates([relation.state for relation in relations])

    if init_state:
        states = filter(lambda state: state in init_state.transitions, states)

    return states


def _remove_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
