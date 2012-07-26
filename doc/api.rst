============================
DEV SERVER API DOCUMENTATION
============================

.. secnum
.. contents::



Resource list: http://crawler.bfhost.cz:12345/admin-api/?format=json



Generic API for all resources
=============================

GET
----------

1. Get first 20 objects of given resource

 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/

*example: get first 20 articles*
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

2. Get first 50 objects of given resource (default value is 20)

 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/?limit=50

3. Getting a detailed resource

 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/{id}/

4. Selecting a subset of resources:

 ::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/set/{id_from};{id_to}/



5. Filtering

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





*Required parameters:*

* format=json


*Optional parameters:*

* limit=<number>

 - page limit, return <number> objects on one page, set limit=0 to disable paging [`more info`__]

__ http://django-tastypie.readthedocs.org/en/latest/interacting.html#getting-a-collection-of-resources



POST
----

- create a new resource

- "Content-Type: application/json"

- to create new resources/objects, you will POST to the list endpoint of a resource, trying to POST to a detail endpoint has a different meaning in the REST mindset (meaning to add a resource as a child of a resource of the same type

To create new resource:
::

 http://crawler.bfhost.cz:12345/admin-api/{resource_name}/


PUT
---

- requires that the entire resource representation be enclosed, missing fields may cause errors, or be filled in by default values

1. Updating an existing resource

::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/{id}/

2. Updating a whole collection of resources

::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/

*example: update authors*
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

- partially updating an existing resource

::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/{id}/



DELETE
------

1. Deleting a single resource
::

	http://crawler.bfhost.cz:12345/admin-api/{resource_name}/{id}/

2. Deleting a whole collection of resources
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
- `ella doc`__, schema__
- inherits from `publishable` resource


__ http://ella.readthedocs.org/en/latest/reference/models.html#module-ella.articles.models
__ http://crawler.bfhost.cz:12345/admin-api/article/schema/?format=json



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
	- upper_title
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
- `ella doc`__, schema__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-author-model
__ http://crawler.bfhost.cz:12345/admin-api/author/schema/?format=json


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
- `ella doc`__, schema__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-category-model
__ http://crawler.bfhost.cz:12345/admin-api/category/schema/?format=json


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

- auto-defined attributes:
	- id
	- tree_path
	- main_parent
	- path








listing
-------
- `ella doc`__, schema__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-listing-model
__ http://crawler.bfhost.cz:12345/admin-api/listing/schema/?format=json


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
- `ella doc`__, schema__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-photo-model
__ http://crawler.bfhost.cz:12345/admin-api/photo/schema/?format=json


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











publishable
-----------
- `ella doc`__, schema__

__ http://ella.readthedocs.org/en/latest/reference/models.html#the-publishable-model
__ http://crawler.bfhost.cz:12345/admin-api/publishable/schema/?format=json


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
- schema__

__ http://crawler.bfhost.cz:12345/admin-api/user/schema/?format=json


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


Contacts:

::

 vladimir.brigant@business-factory.cz
 michal.belica@business-factory.cz


