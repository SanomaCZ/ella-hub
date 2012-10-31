==============================
Authentication & Authorization
==============================

.. secnum
.. contents::

--------------
Authentication
--------------

Ella-hub authentication uses ``tastypie.ApiKeyAuthentication`` class, so ``api_key`` is generated (if username and password are correct) after login request and sent to client in login response. After user is logged in,
resource requests need ``"Authorization: ApiKey username:api_key"`` header specified.

-------------
Authorization
-------------

Ella-hub authorization uses subclassed ``tastypie.Authorization``, it overrides ``is_authenticated`` method and defines ``apply_limits`` method. Top level schema, particular resource schemas and resource items are generated with respect to user's permissions.


Login response content
----------------------
After login request is sent and requesting user is authenticated, login response is acquired with specified content format. All necessary resources definitions are sent to user with all attributes. If user doesn't have rights to see resource attribute, ``disabled`` flag is set to ``true``.

.. Object-level permissions are implemented too. Every resource has ``_patch`` and ``_delete`` boolean attributes.

Login response content format:
::

  {
    "api_key": "...",
    "auth_tree":
      {
        "resource_name":
          {
            "allowed_http_methods":["get", "post", "put", "delete", "patch"],
            "states":
              {
                "added": "Added",
                ...
              }
            "fields":
               {
                "attr1":
                  {
                    "nullable":boolean, "readonly":boolean, "disabled":boolean
                  },
              }
          }
        "articles":
          {
            "article_resource_name":
              {...}
          }
      },
    "system":
      {
        "resources":
          {
            "resource_name":
              {...}
          }
        "states":
          {
            "added": "Added",
            ...
          }
      }
  }

*Note: "states" field is specified only if at least one state exists.*

Current superuser login response content:

::

  {
    "api_key": "...",
    "auth_tree": {
      "articles": {
        "article": {
          "allowed_http_methods": [
            "get",
            "post",
            "put",
            "delete",
            "patch"
          ],
          "fields": {...},
          "states": {...}
        },
        "encyclopedia": {
          "allowed_http_methods": [...],
          "fields": {...},
          "states": {...}
        },
        "pagedarticle": {
          "allowed_http_methods": [...],
          "fields": {...},
          "states": {...}
        },
        "recipe": {
          "allowed_http_methods": [...],
          "fields": {...},
          "states": {...}
        }
      },
      "photo": {
        "allowed_http_methods": [...],
        "fields": {...},
        "states": {...}
      }
    },
    "system": {
      "resources": {
        "author": {
          "allowed_http_methods": [...],
          "fields": {...}
        },
        "category": {
          "allowed_http_methods": [...],
          "fields": {...}
        },
        "draft": {
          "allowed_http_methods": [],
          "fields": {...}
        },
        "site": {
          "allowed_http_methods": [...],
          "fields": {...}
        },
        "user": {
          "allowed_http_methods": [...],
          "fields": {...}
        }
      },
    }
  }
