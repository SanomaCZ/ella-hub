from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from ella_hub.models import Permission, ModelPermission, PrincipalRoleRelation
from ella_hub.models import StatePermissionRelation


REST_PERMS = {
    "GET":"can_view",
    "POST":"can_add",
    "PUT":"can_change",
    "PATCH":"can_change",
    "DELETE":"can_delete"
}


def has_model_permission(model, user, codename, roles=[]):
    """
    Comment it!
    """
    if isinstance(user, AnonymousUser):
        return False

    ct = ContentType.objects.get_for_model(model)
    # Checking if specified <codename> Permission exists.
    try:
        perm = Permission.objects.get(codename=codename)
    except Permission.DoesNotExist:
        return False

    if user.is_superuser and not perm.restriction:
        return True

    if not roles:
        relations = PrincipalRoleRelation.objects.filter(user=user)
        roles = [relation.role for relation in relations]

    o_perms = ModelPermission.objects.filter(role__in=roles,
        content_type=ct, permission=perm)

    return o_perms.exists()


def has_permission(model_obj, user, codename, roles=None):
    """
    Returns True if <user> has at least one of <roles> which
    has permission specified by <codename> for specified <model_obj>,
    otherwise returns False.

    If roles is None, all user roles are considered.
    """
    if isinstance(user, AnonymousUser):
        return False

    import ella_hub.utils.workflow

    ct = ContentType.objects.get_for_model(model_obj)
    # Checking if specified <codename> Permission exists.
    try:
        perm = Permission.objects.get(codename=codename)
    except Permission.DoesNotExist:
        return False

    if user.is_superuser and not perm.restriction:
        return True

    if not roles:
        relations = PrincipalRoleRelation.objects.filter(user=user)
        roles = [relation.role for relation in relations]

    o_perms = ModelPermission.objects.filter(role__in=roles,
        content_type=ct, permission=perm)

    if not o_perms.exists():
        return False

    # ziskanie stavu
    state = ella_hub.utils.workflow.get_state(model_obj)

    try:
        StatePermissionRelation.objects.get(state=state,
            permission=perm, role__in=roles)
        return True
    except StatePermissionRelation.DoesNotExist:
        return False


def grant_permission(model, role, permission):
    """
    Grants <permission> to <model> for specified <role>.
    <permission> - can be codename or Permission object
    """
    if not isinstance(permission, Permission):
        try:
            permission = Permission.objects.get(codename=permission)
        except Permission.DoesNotExist:
            return False

    ct = ContentType.objects.get_for_model(model)
    ModelPermission.objects.get_or_create(role=role, content_type=ct,
        permission=permission)

    return True


def get_roles(user):
    if isinstance(user, AnonymousUser):
        return []

    relations = PrincipalRoleRelation.objects.filter(user=user)
    roles = [relation.role for relation in relations]
    return roles


def is_resource_allowed(user, model_class):
    """
    Return True if user has rights to get schema
    specified by `model_class`.
    """
    if isinstance(user, AnonymousUser):
        return False

    content_type = ContentType.objects.get_for_model(model_class)
    try:
        ModelPermission.objects.get(content_type=content_type,
            role__in=get_roles(user), permission=REST_PERMS["GET"])
    except ModelPermission.DoesNotExist:
        return False
    return True
