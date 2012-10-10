from object_permissions import get_users_any

from django.core.exceptions import FieldError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser

from ella.articles.models import Article
from ella.core.models import Author

from ella_hub.models import Permission, ModelPermission, PrincipalRoleRelation


##############################################
# Utils fot ella_hub.models.permissions module
def has_permission(model, user, codename, roles=None):
    """
    Returns True if <user> has at least one of <roles> which
    has permission specified by <codename> for specified <model>,
    otherwise returns False.

    If roles is None, all user roles are considered.
    """
    ct = ContentType.objects.get_for_model(model)
    # Checking if specified <codenane> Permission exists.
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


def grant_permission(model, role, permission):
    """
    Grants <permission> to <model> for specified <role>.
    <permission> - can be codename or Permission object
    """
    if not isinstance(permission, Permission):
        try:
            permission = Permission.objects.get(codename = permission)
        except Permission.DoesNotExist:
            return False

    ct = ContentType.objects.get_for_model(model)

    try:
        ModelPermission.objects.get(role=role, content_type = ct, permission=permission)
    except ModelPermission.DoesNotExist:
        ModelPermission.objects.create(role=role, content_type=ct, permission=permission)

    return True
##############################################


def has_obj_perm(user, obj, perm=None):
    """
    Return True if user has `perm` to `obj`,
    if `perm` is not specified, return True
    if user has any perm to `obj`.
    """
    ct = ContentType.objects.get(model=obj.__class__.__name__.lower())

    if perm:
        if ((ct.app_label + '.' + perm) in user.get_all_permissions() or
            user.has_perm(perm, obj)):
            return True
    else:
        if user.has_any_perms(obj):
            return True
    return False


def has_user_model_perm(user, model_name, perm=None):
    """
    Return True if user has `perm` to `model_name` model.
    If `perm` is not specified, return True if user
    has any perm to `model_name` mode.
    """
    ct = ContentType.objects.get(model=model_name)
    found_perm = False

    permission = ct.app_label + "."
    if perm:
        found_perm = (ct.app_label + "." + perm + "_" + model_name) in user.get_all_permissions()
    else:
        found_perm = filter(lambda perm: perm.startswith(ct.app_label+".") and perm.endswith(model_name),
            user.get_all_permissions())

    return found_perm


def has_user_model_object_with_any_perm(user, model_name, perm_list=[]):
    """
    Return True if user has any permission from `perm_list`
    to any object of `model_name` model,
    if `perm_list` is not specified, return True if user
    has any permission to any object of `model_name` model.
    """
    if isinstance(user, AnonymousUser):
        return False

    ct = ContentType.objects.get(model=model_name)

    try:
        objects = user.get_objects_any_perms(ct.model_class(), perms=perm_list)
    except FieldError:
        # print "Class %s has no registered permissions." % ct.model_class()
        return False

    return bool(objects)


def is_resource_allowed(user, model_name):
    """
    Return True if user has rights to get schema
    specified by `model_name`.
    """
    return (has_user_model_perm(user, model_name) or
        has_user_model_object_with_any_perm(user, model_name))
