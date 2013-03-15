from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from ella.core.cache import get_cached_object

from ella_hub.models import Permission, ModelPermission, PrincipalRoleRelation
from ella_hub.models import StatePermissionRelation, State


REST_PERMS = {
    "GET":"can_view",
    "POST":"can_add",
    "PUT":"can_change",
    "PATCH":"can_change",
    "DELETE":"can_delete"
}


def has_model_state_permission(model, user, permission, state=None, roles=None):
    """
    Returns True if objects of class <model> in <state>
    defined for <user> role/roles has <permission>,
    otherwise returns False. If <roles> is None, all <user> roles are considered.

    Example:
    User Peter has editor role, so he can edit articles in "editing" state,
    but can't publish articles in "editing" state.
    """
    if isinstance(user, AnonymousUser):
        return False

    import ella_hub.utils.workflow

    workflow = ella_hub.utils.workflow.get_workflow(model)
    if not workflow and state:
        return False

    if state and not isinstance(state, State):
        try:
            state = get_cached_object(State, codename=state)
        except State.DoesNotExist:
            return False

     # state need to belong to the workflow
    if state and state.workflow != workflow:
        return False

    ct = ContentType.objects.get_for_model(model)

    if not isinstance(permission, Permission):
        try:
            permission = get_cached_object(Permission, codename=permission)
        except Permission.DoesNotExist:
            return False

    # if Permission is specified as restriction (perm.restriction==True),
    # superuser is not restricted
    if user.is_superuser and not permission.restriction:
        return True

    # if no roles are specified, lookup all user roles
    if not roles:
        relations = PrincipalRoleRelation.objects.filter(user=user).\
                        select_related('role')
        roles = [relation.role for relation in relations]

    model_perms = ModelPermission.objects.filter(role__in=roles,
        content_type=ct, permission=permission).select_related('permission')

    perms = [model_perm.permission for model_perm in model_perms]

    if state:
        return StatePermissionRelation.objects.filter(state=state,
            permission__in=perms, role__in=roles).count()

    return len(perms)


def has_object_permission(model_obj, user, codename, roles=None):
    """
    Returns True if <user> has at least one of <roles> which
    has permission specified by <codename> for specified <model_obj>,
    otherwise returns False.

    If roles is None, all <user> roles are considered.
    """
    if isinstance(user, AnonymousUser):
        return False

    ct = ContentType.objects.get_for_model(model_obj)

    try:
        perm = get_cached_object(Permission, codename=codename)
    except Permission.DoesNotExist:
        return False

    if user.is_superuser and not perm.restriction:
        return True

    if not roles:
        relations = PrincipalRoleRelation.objects.filter(user=user).\
                        select_related('role')
        roles = [relation.role for relation in relations]

    o_perms = ModelPermission.objects.filter(role__in=roles,
        content_type=ct, permission=perm)

    if not o_perms.exists():
        return False

    import ella_hub.utils.workflow

    state = ella_hub.utils.workflow.get_state(model_obj)

    try:
        StatePermissionRelation.objects.get(state=state,
            permission=perm, role__in=roles)
    except StatePermissionRelation.DoesNotExist:
        return False
    else:
        return True

def grant_permission(model, role, permission):
    """
    Grants <permission> to <model> for specified <role>.
    <permission> - can be codename or Permission object
    """
    if not isinstance(permission, Permission):
        try:
            permission = get_cached_object(Permission, codename=permission)
        except Permission.DoesNotExist:
            return False

    ct = ContentType.objects.get_for_model(model)
    ModelPermission.objects.get_or_create(role=role, content_type=ct,
        permission=permission)

    return True


def add_role(principal, role):
    "Adds <role> to user or group (<principal>)."
    if isinstance(principal, User):
        try:
            relation = PrincipalRoleRelation.objects.get(user=principal,
                role=role, content_id=None, content_type=None)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(user=principal, role=role)
            return True
    else:
        try:
            relation = PrincipalRoleRelation.objects.get(group=principal,
                role=role, content_id=None, content_type=None)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(group=principal, role=role)
            return True


def remove_role(principal, role):
    "Removes specific <role> from user or group (<principal>)."
    try:
        if isinstance(principal, User):
            relation = PrincipalRoleRelation.objects.get(user=principal,
                role=role, content_id=None, content_type=None)
        else:
            relation = PrincipalRoleRelation.objects.get(group=principal,
                role=role, content_id=None, content_type=None)
    except PrincipalRoleRelation.DoesNotExist:
        return False
    else:
        relation.delete()
    return True


def remove_roles(principal):
    "Removes all roles from user or group (<principal>)."
    if isinstance(principal, User):
        relations = PrincipalRoleRelation.objects.filter(user=principal,
            content_id=None, content_type=None)
    else:
        relations = PrincipalRoleRelation.objects.filter(group=principal,
            content_id=None, content_type=None)
    if relations:
        relations.delete()
        return True
    else:
        return False


def get_roles(principal):
    "Returns all roles of user or group (<principal>)."
    if isinstance(principal, User):
        kwargs = {'user': principal}
    else:
        kwargs = {'group': principal}
    relations = PrincipalRoleRelation.objects.filter(**kwargs).\
                    select_related('role')
    roles = [relation.role for relation in relations]
    return roles
