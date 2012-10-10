===========
Ella.photos
===========

.. contents::


--------------
Photo resource
--------------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-photo-model

C(reate)
========
Image upload is needed to create Photo resource. Creation is made via
HTTP **PATCH** request with ``multipart/form-data`` content-type.
This method allows to create multiple resources with image.
Uploaded images is implicitely saved to:

 ::

   settings.MEDIA_URL + photos/<year>/<month>/<day>/filename

``id`` attribute is't needed to specify, it is set internaly.

``image`` has special meaning and contains pointer to uploaded image.
The pointer identifies file which will be assigned to corresponding resource.

*Format of image pointer*
 ::

   attached_object_id:<filename_attribute_of_attached_file>


*Curl example:*
 ::

  image_path=/path/to/image.png
  image_path_basename=$(basename $image_path)
  server=http://www.server-domain.cz

  curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" \
  -X PATCH --form "attached_object=@${image_path}" --form 'resource_data={
    "objects": [{
      "title": "Multipart photo",
      "slug": "multipart-photo",
      "description": "Multipart description of photo",
      "created": "2012-09-05T10:16:32.131517",
      "authors": ["/admin-api/author/<id>/"],
      "app_data": "{}",
      "image": "attached_object_id:'$image_path_basename'"
    }]
  }' "$server/admin-api/photo/"



R(ead)
======
1. Get all Photo resources

 ::

  curl -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" <server>/admin-api/photo/

2. Get specific Photo resource

 ::

  curl -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" <server>/admin-api/photo/<id>/

3. Download image

 ::

  curl -H "Authorization: ApiKey <name>:<api_key>" <server>/admin-api/photo/download/<id>/


U(pdate)
========

PUT method does't allow to update ``image`` attribute of ``Photo`` resource.
For updating ``image`` attribute see PATCH method.


PUT
'''

::

  curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" \
  -H "Content-Type: application/json" -X PUT --data '{
    "title": "Modified photo by PUT method",
    "description": "Modified description by PUT method."
  }' "<server>/admin-api/photo/<id>/"


PATCH
'''''

1. without image

::

  curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" \
  -H "Content-Type: application/json" -X PATCH --data '{
    "title": "Modified photo by PATCH method",
    "description": "Modified description by PATCH method."
  }' "<server>/admin-api/photo/<id>/""


2. with image

Updating ``Photo`` resource is similar to creating one, but ``resource_uri``
attribute has to be specified. If ``resource_uri`` is't specified new
object is created if possible.

For each object in objects:

- If the object does not have a ``resource_uri`` attribute then the item
  is considered new and is handled like a POST to the resource list.
- If the object has a ``resource_uri`` attribute and the ``resource_uri``
  refers to an existing resource then the item is a update. It's treated like
  a PATCH to the corresponding resource detail.
- If the object has a ``resource_uri`` but the resource doesn't exist,
  then this is considered to be a create-via-PUT.

::

  new_image_path=/path/to/writable/dir/file_name.png
  new_image_path_basename=$(basename $new_image_path)

  curl --dump-header - -X PATCH -H "Authorization: ApiKey <name>:<api_key>" \
    --form "attached_object=@${new_image_path}" --form 'resource_data={
    "objects": [{
      "resource_uri": "/admin-api/photo/<id>/",
      "image": "attached_object_id:'$new_image_path_basename'",
      "description":"Modified photo by PATCH method (image data included)."
    }]
  }' "<server>/admin-api/photo/"





D(elete)
========

If ``Photo`` object is deleted, all related FormatedPhoto objects are deleted too.

::

  curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" -X DELETE <server>/admin-api/photo/<id>/



---------------
Format resource
---------------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-format-model

*Note: Format resource cannot be created with specified custom (not-existing) id right now, see* https://github.com/ella/ella/pull/127


C(reate)
========

::


  format=
    {
      "name": "Perex photo",
      "max_width": 300, "max_height": 200,
      "nocrop": true,
      "stretch": true,
      "resample_quality": 95,
      "flexible_height": false,
      "sites": [{
        "domain": "domain2.com",
        "name": "domain2.com"
      }]
    }

  curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" -X POST --data "$format" <server>/admin-api/format/



R(ead)
======

::

  curl -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" <server>/admin-api/format/


U(pdate)
========

If ``Format`` is updated, all related ``FormatedPhoto`` objects are deleted.

PUT/PATCH
'''''''''

::

 update_format=
    {
      "name": "New name",
      "max_width": 400,
      "sites": [{
        "domain": "domain2.com",
        "name": "domain2.com"
      }]
    }

  curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X [PUT|PATCH] --data "$update_format" <server>/admin-api/format/<id>/


D(elete)
========

If ``Format`` object is deleted, all related FormatedPhoto objects are deleted too.

::

  curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" -X DELETE <server>/admin-api/format/<id>/



----------------------
Formatedphoto resource
----------------------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-photo-model

Specified Format is applied to Photo and new image is saved to:

 ::

   settings.MEDIA_URL + photos/<year>/<month>/<day>/filename



C(reate)
========

::

 formatedphoto=
   {
     "photo": "/admin-api/photo/<id>/",
     "format": "/admin-api/format/<id>/"
   }

  curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" -X POST --data "$formatedphoto" <server>/admin-api/formatedphoto/



R(ead)
======

::

  curl -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" <server>/admin-api/formatedphoto/


U(pdate)
========

PUT/PATCH
'''''''''

::

  curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" \
  -X [PUT|PATCH] --data '{
    "crop_top": 0,
    "crop_left": 50,
    "crop_height": 50,
    "width": 200
  }' <server>/admin-api/formatedphoto/<id>/


D(elete)
========

::

  curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" -X DELETE <server>/admin-api/formatedphoto/<id>/

