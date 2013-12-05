from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from ella.core.cache import get_cached_object

from ella_hub.models import Permission, ModelPermission, PrincipalRoleRelation


REST_PERMS = {
    "GET": "can_view",
    "POST": "can_add",
    "PUT": "can_change",
    "PATCH": "can_change",
    "DELETE": "can_delete"
}


def has_model_permission(model, user, permission):
    """
    Uses only standard django model permissions
    """

    ct = ContentType.objects.get_for_model(model)
    return user.has_perm("%s.%s_%s" % (ct.app_label, permission, ct.model))


def has_object_permission(model_obj, user, codename):
    """
    Fallback
    """

    return has_model_permission(model_obj, user, codename)


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
