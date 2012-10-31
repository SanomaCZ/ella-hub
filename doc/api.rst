======================
Ella-hub Documentation
======================

.. secnum
.. contents::


Django-tastypie doc__

__ http://django-tastypie.readthedocs.org/en/latest/interacting.html

Ella doc__

__ http://ella.readthedocs.org/en/latest/index.html


Develop servers
===============

Main
----
``http://crawler.bfhost.cz:12345``

root_dir: ``/home/seocity/elladev/ella-hope-new/``

virtual_env: ``/home/seocity/elladev/env_ella-hope/``


Alternative
-----------
``http://crawler.bfhost.cz:33333``

root_dir: ``/home/brigant/elladev/ella-hope/``

virtual_env: ``/home/brigant/elladev/env_ella-hope_brigant/``


Basic commands
--------------
To activate proper virtual environment:

::

 source <virtual_env>/bin/activate

To deactivate virtual environment:

::

 deactivate


To kill server running on <port>:

::

 kill `ps -ef | grep "runserver 0.0.0.0:<port>" | grep -v grep | awk '{print $2}'`

To start server running on <port>:

::

 python <root_dir>/manage.py syncdb
 python <root_dir>/manage.py runserver 0.0.0.0:<port>




Login and logout
================

Login
-----
1. Make POST request with fields `username`, `password`

 ::

 	http://crawler.bfhost.cz:12345/admin-api/login/

2. Returned JSON object contains `api_key` attribute with API key.

 ::

 	{
 		"api_key": "204db7bcfafb2deb7506b89eb3b9b715b09905c8"
	}

3. Add *Authorization* HTTP header to every next request in format:

 ::

 	Authorization: ApiKey <username>:<api_key>
	Authorization: ApiKey user:204db7bcfafb2deb7506b89eb3b9b715b09905c8

You can use GET parameters, too.

 ::

 	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/?username=<username>&api_key=<api_key>
 	http://crawler.bfhost.cz:12345/admin-api/article/?username=user&api_key=204db7bcfafb2deb7506b89eb3b9b715b09905c8



Validate API key
----------------
1. Make POST request with *Authorization* HTTP header

 ::

 	http://crawler.bfhost.cz:12345/admin-api/validate-api-key/

2. Returned JSON object contains boolean `api_key_validity` attribute.

 ::

 	{
 		"api_key_validity": true
	}



Logout
------
1. Make POST request to logout URL

 ::

 	http://crawler.bfhost.cz:12345/admin-api/logout/



Object State Switching
======================
All possible states object (article, photo etc.) can be switched to (with respect
to used workflow), are accessible via "states" resource field.
When creating new object in admin, "states" sent in login response content for particular
resource should be used. These "states" are states object can switch to from initial state.
Object state can be switched simply setting "state" resource field to state codename in POST/PUT/PATCH request.



Generic API for all resources
=============================

GET
---

1. Get top-level resources schema
`````````````````````````````````
 ::

 	http://crawler.bfhost.cz:12345/admin-api/

2. Get resource-specific schema
```````````````````````````````
 ::

 	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/


3. Get max 20 objects of given resource
```````````````````````````````````````
- max 20, because it is implicit limit, to change or disable this limit, see_.

 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/

*example: get max 20 articles*

 ::

	http://crawler.bfhost.cz:12345/admin-api/article/

 ::

	[
		{
			announced: false,
			app_data: "{}",
			authors: [
				{
					description: "",
					email: "",
					id: "1",
					name: "Seocity",
					resource_uri: "/admin-api/author/1/",
					slug: "seocity",
					text: ""
				},
				{
					description: "",
					email: "",
					id: "2",
					name: "Mr. Pohodička",
					resource_uri: "/admin-api/author/2/",
					slug: "mr-pohodicka",
					text: ""
				}
			],
			category: {
				app_data: "{}",
				content: "",
				description: "",
				id: "1",
				resource_uri: "/admin-api/category/1/",
				slug: "test-category",
				template: "category.html",
				title: "Test category",
				tree_path: ""
			},
			content: "Content of article",
			description: "",
			id: "1",
			last_updated: "2012-07-19T19:21:55+00:00",
			listings: [
			],
			photo: null,
			publish_from: "2012-07-19T19:21:55+00:00",
			publish_to: null,
			published: true,
			resource_uri: "/admin-api/article/1/",
			slug: "article-title",
			static: false,
			title: "Article title",
			url: "http://example.com/2012/7/19/article-title/"
		},
		...
	]


4. Getting a detailed resource
``````````````````````````````
 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/{id}/


5. Selecting a subset of resources
``````````````````````````````````
 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/set/{id_from};{id_to}/



6. Filtering
````````````
 a. Direct filtering

 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/?{attr_name}[__lt|gt|lte|gte|exact|not]={value}

*example: filter user named daniel:*
 ::

  http://crawler.bfhost.cz:12345/admin-api/user/?name=daniel


*example: filter all articles with id > 4:*
 ::

  http://crawler.bfhost.cz:12345/admin-api/article/?id__gt=4


 b. Filtering based on foreign key

 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/?{foreign_key}__{attr}={value}

*example: filter articles written by daniel:*
 ::

	http://crawler.bfhost.cz:12345/admin-api/article/?authors__name=daniel


Required parameters
```````````````````

 ::

 	format=json


Optional parameters
```````````````````
.. _see:

 ::

	limit=<number>

 - page limit, return <number> objects on one page, set limit=0 to disable paging [`more info`__]

__ http://django-tastypie.readthedocs.org/en/latest/interacting.html#getting-a-collection-of-resources



POST
----

- creation of a new resource

- "Content-Type: application/json"

- to create new resources/objects, you will POST to the list endpoint of a resource, trying to POST to a detail endpoint has a different meaning in the REST mindset (meaning to add a resource as a child of a resource of the same type)

- related objects are identified by their resource URI

To create new resource (article) send POST request to:

 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/


*example: creation of a new article*

 ::

	{
	    "title": "Article title",
	    "authors": ["/admin-api/user/6/", "/admin-api/user/1/"],
	    "content": "Unicode text",
	    "description": "Perex",
	    "publish_from_date": "2012-08-09",
	    "publish_from_time": "15:47",
	    "published": true,
	    "category": "/admin-api/category/2/",
	    "last_updated": "2012-08-07T09:47:44",
	    "publish_from": "2012-08-09T15:47",
	    "slug": "slug-like-a-hmm",
	    "static": true
	}


PUT
---

- requires that the entire resource representation be enclosed, missing fields may cause errors, or be filled in by default values

1. Updating an existing resource
````````````````````````````````

::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/{id}/


2. Updating a whole collection of resources
```````````````````````````````````````````

::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/

*example: updating authors*
::

	{
		"objects": [
			{
				"description": "desc about seo",
				"email": "seo@sea.ocean",
				"id": "1",
				"name": "Seocity",
				"resource_uri": "/admin-api/author/1/",
				"slug": "seocity",
				"text": "seo is op"
			},
			{
				"description": "cool man",
				"email": "cool@swag.com",
				"id": "2",
				"name": "Mr. Pohodička",
				"resource_uri": "/admin-api/author/2/",
				"slug": "mr-pohodicka",
				"text": "coolness is op"
			},
			{
				"description": "benjamin? u alive?",
				"email": "frank@marka.euro",
				"id": "3",
				"name": "Franklyn",
				"resource_uri": "/admin-api/author/3/",
				"slug": "franklyn",
				"text": "money is op"
			}
		]
	}

::

	http://crawler.bfhost.cz:12345/admin-api/author/




PATCH
-----

- partially update of an existing resource
- all required attributes needed, `related issue`__

__ https://github.com/toastdriven/django-tastypie/pull/411


::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/{id}/



DELETE
------

1. Deletion of a single resource
::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/{id}/

2. Deleting of a whole collection of resources
::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/



Bulk operations
---------------

- it is possible to do many creations, updates, and deletions  to a collection in a single request by sending a PATCH to the list endpoint

::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/

*example: delete and update articles*

::

	{
		"deleted_objects": [
			"http://crawler.bfhost.cz:12345/admin-api/article/1/"
		],
		"objects": [
			{
				"slug": "article-title",",
				"content": "New awesome never seen content, follow us!"
			}
		]
	}

::

	http://crawler.bfhost.cz:12345/admin-api/article/





Resources
=========

article
-------
- `ella doc`__
- inherits from `publishable` resource

__ http://ella.readthedocs.org/en/latest/reference/models.html#module-ella.articles.models


- required attributes:
	- content

	- category <fk> *(inherited)*
	- title *(inherited)*
	- slug *(inherited)*
	- authors <many-to-many> *(inherited)*
	- published *(inherited)*
	- publish_from *(inherited)*
	- publish_to *(inherited)*
	- static *(inherited)*

- optional attributes:
	- updated

	- description *(inherited)*
	- source <fk> *(inherited)*
	- photo <fk> *(inherited)*
	- app_data *(inherited)*

- auto-defined attributes:
	- created

	- id *(inherited)*
	- content_type <fk> *(inherited)*
	- target *(inherited)*







author
------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-author-model


- required attributes:
	- slug

- optional attributes:
	- user <fk>
	- name
	- description
	- text
	- email

- auto-defined attributes:
	- id






category
--------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-category-model


- required attributes:
	- title
	- template
	- slug
	- site <fk>

- optional attributes:
	- description
	- content
	- tree_parent
	- app_data
	- parent_category <fk>

- auto-defined attributes:
	- id
	- tree_path
	- main_parent
	- path






source
--------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-source-model


- required attributes:
	- name

- optional attributes:
	- url
	- description

- auto-defined attributes:
	- id






listing
-------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-listing-model


- required attributes:
	- publishable <fk>
	- category <fk>
	- publish_from
	- publish_to


- optional attributes:
	- commercial

- auto-defined attributes:
	- id





photo
-----
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-photo-model


- required attributes:
	- title
	- slug
	- image
	- width
	- height
	- authors <many-to-many>

- optional attributes:
	- description
	- important_top
	- important_left
	- important_bottom
	- important_right
	- source <fk>
	- app_data


- auto-defined attributes:
	- id
	- created



format
------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-format-model


- required attributes:
	- name
	- max_width
	- max_height
	- flexible_height
	- flexible_max_height
	- stretch
	- nocrop
	- resample_quality


- optional attributes:
	- sites <many-to-many>

- auto-defined attributes:
	- id




formattedphoto
--------------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-photo-model


*Problem*: tastypie has a bug that doesn't allow to POST/PUT 3-and-more level nested resources, see:
https://github.com/toastdriven/django-tastypie/issues/307, so format may be specified only with resource URI!


- required attributes:
	- photo <fk>
	- format <fk>
	- image

- optional attributes:
	- crop_left
	- crop_top
	- crop_width
	- crop_height
	- width
	- height
	- url

- auto-defined attributes:
	- id




publishable
-----------
- `ella doc`__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-publishable-model


- required attributes:
	- category <fk>
	- title
	- slug
	- authors <many-to-many>
	- published
	- publish_from
	- publish_to
	- static

- optional attributes:
	- description
	- source <fk>
	- photo <fk>
	- app_data

- auto-defined attributes:
	- id
	- content_type <fk>
	- target




user
----

- required attributes:
	- password
	- username


- optional attributes:
	- email
	- first_name
	- last_name

- auto-defined attributes:
	- id
	- date_joined
	- is_active
	- is_staff
	- is_superuser
	- last_login
	- resource_uri


Contacts
========
::

 vladimir.brigant@business-factory.cz
 michal.belica@business-factory.cz
