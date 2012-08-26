from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from object_permissions import get_users_any

from ella.articles.models import Article
from ella.core.models import Author


__all__ = ('has_obj_perm', 'has_user_model_perm', 
	       'has_user_model_object_with_any_perm', 'is_resource_allowed',)


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
	if found_perm:
		return True
	return False


def has_user_model_object_with_any_perm(user, model_name, perm_list=[]):
	"""
	Return True if user has any permission from `perm_list` 
	to any object of `model_name` model,
	if `perm_list` is not specified, return True if user
	has any permission to any object of `model_name` model.
	"""
	ct = ContentType.objects.get(model=model_name)
	objects = []

	try:		
		objects = user.get_objects_any_perms(ct.model_class(), perms=perm_list)
	except FieldError:
		pass
		#print "Class %s has no registered permissions." % ct.model_class()
	
	if objects:
	    return True
	return False


def is_resource_allowed(user, model_name):
	"""
	Return True if user has rights to get schema
	specified by `model_name`.
	"""
	if (has_user_model_perm(user, model_name) or
		has_user_model_object_with_any_perm(user, model_name)):
		return True
	return False
	