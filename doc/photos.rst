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
Image upload is needed to create Photo resource. Creation is made via HTTP request with ``multipart/form-data`` content-type. Uploaded image is implicitely saved to:

 ::

   settings.MEDIA_URL + photos/<year>/<month>/<day>/filename

``image`` attribute isn't needed to specify, it is set internaly.

*Curl example:*

 ::

  image_path=/path/to/image.png
  server=http://www.server-domain.cz

  curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" \
  -X POST --form "image=@${image_path}" --form 'photo={
    "id": 100,
    "title": "Multipart-photo",
    "slug": "multipart-photo",
    "description": "Multipart description of photo",
    "width": 256, "height": 256,
    "created": "2012-09-05T10:16:32.131517",
    "important_top": null,
    "important_left": null,
    "important_bottom": null,
    "important_right": null,
    "app_data": "{}"
  }' "$server/admin-api/photo/"



R(ead)
======
1. Get all Photo resources

 ::

   curl -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key> <server>/admin-api/photo/

2. Get specific Photo resource

 ::

   curl -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key> <server>/admin-api/photo/<id>/

3. Download image

 ::

   curl -H "Authorization: ApiKey <name>:<api_key> <server>/admin-api/photo/download/<id>/


U(pdate)
========

PUT
'''

1. without image

::

 curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key> -X PUT --data '{"description": "abrakadabra, bro", "title": "another_photo"}' <server>/admin-api/photo/1/

2. with image

::

 new_image_path=/home/vlado/pics/icons/eclipse.png

 curl --dump-header - -H "Authorization: ApiKey <name>:<api_key> -F upload_image=@${new_image_path} -F photo='{"title":"put title"}' -X PUT  <server>/admin-api/photo/1/


PATCH
'''''

1. without image

::

 curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" -X PATCH --data '{"description": "hello, bro"}' "<server>/admin-api/photo/1/"


2. with image

::

 new_image_path=/home/vlado/pics/icons/eclipse.png
 curl -H "Authorization: ApiKey <name>:<api_key>" -F upload_image=@${new_image_path} -F photo='{"title":"new_title"}' -X PATCH <server>/admin-api/photo/1/





D(elete)
========

::

 curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" -X DELETE <server>/admin-api/photo/<id>/



---------------
Format resource
---------------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-format-model

*Note: Can't create Format resource with specified custom (not-existing) id.*


C(reate)
========

::


 format=
   {
     "flexible_height": false,
     "flexible_max_height": null,
     "max_height": 200,
     "max_width": 34,
     "name": "formatik",
     "nocrop": true,
     "resample_quality": 95,
     "sites":
       [
         {
           "domain": "domain2.com",
           "id": 3,
           "name": "domain2.com",
           "resource_uri": "/admin-api/site/3/"
         }
       ],
     "stretch": true
   }

 curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" -X POST --data "$format" <server>/admin-api/format/



R(ead)
======

::

  curl -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key> <server>/admin-api/format/


U(pdate)
========

PUT/PATCH
'''''''''

::

 update_format=
   {
     "name": "formatik",
     "sites":
       [
         {
           "domain": "domain2.com",
           "id": 3,
           "name": "domain2.com",
           "resource_uri": "/admin-api/site/3/"
         }
       ]
    }

 curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X [PUT|PATCH] --data "$update_format" <server>/admin-api/format/<id>/


D(elete)
========

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
     "resource_uri": "/admin-api/formatedphoto/100/",
     "crop_height": 0,
     "crop_left": 0,
     "crop_top": 0,
     "crop_width": 0,
     "id": 100,
     "format": "/admin-api/format/100/",
     "height": 200,
     "photo": "/admin-api/photo/1/",
     "width": 200
   }

 curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key>" -X POST --data "$formatedphoto" <server>/admin-api/formatedphoto/



R(ead)
======

::

  curl -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key> <server>/admin-api/formatedphoto/


U(pdate)
========

PUT/PATCH
'''''''''

::

 curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey <name>:<api_key> -X [PUT|PATCH] --data '{"crop_height": 50, "crop_left": 50, "crop_top": 0, "width": 200}' <server>/admin-api/formatedphoto/<id>/


D(elete)
========

::

 curl --dump-header - -H "Authorization: ApiKey <name>:<api_key>" -X DELETE <server>/admin-api/formatedphoto/<id>/

