======================
Creating draft objects
======================

.. secnum
.. contents::


Model for draft object is class `ella_hub.models.Draft`.
It is available via API `draft` resource with URL

 ::

    http://crawler.bfhost.cz:12345/admin-api/draft/

Draft may be used to store any data in JSON format with reference to some other
object (article, photo, ...). It is suitable for autosave and as templates.


Draft structure
---------------

- required attributes:
    - user <fk>
    - data
    - content_type

- optional attributes:
    - name (used mainly as template name)

- auto-defined attributes:
    - id
    - timestamp


Getting drafts
--------------

Every user get only its own drafts. Drafts can be filtered according their
`content_type`. For example drafts associated with article can be filtered
the way below.

 ::

    http://crawler.bfhost.cz:12345/admin-api/draft/?content_type=article

*example of returned data*
 ::

    [{
        "data": {
            "width": 1024,
            "height": 666
        },
        "id": 2,
        "name": "",
        "resource_uri": "/admin-api/draft/2/",
        "timestamp": "2012-08-09T07:24:14.044584",
        "user": {
            "first_name": "",
            "id": 1,
            "last_name": "",
            "resource_uri": "/admin-api/user/1/",
            "username": "MacGyver"
        }
    }, {
        "data": "a",
        "id": 1,
        "name": "Pepek",
        "resource_uri": "/admin-api/draft/1/",
        "timestamp": "2012-08-09T07:23:25.805348",
        "user": {
            "first_name": "",
            "id": 1,
            "last_name": "",
            "resource_uri": "/admin-api/user/1/",
            "username": "MacGyver"
        }
    }]


Creating drafts
---------------

Drafts is created via POST method by sending attributes below at URL:

 ::

    http://crawler.bfhost.cz:12345/admin-api/draft/

*example: create draft of photo*
 ::

    {
        "user": 1,
        "content_type": "photo",
        "data": {
            "width": 200,
            "height": 200,
            "orientation": "upside-down",
            "data": "data:image/gif;base64,R0lGODlhUAAPAKIAAAsL...",
            "title": "Really beautiful image"
        }
    }
