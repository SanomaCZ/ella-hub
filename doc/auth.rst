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
After login request is sent and requesting user is authenticated, login response is sent with specified content format. All necessary resources definitions are sent to user with all attributes. If user don't have rights to see resource attribute, ``disabled`` flag is set to ``true``.
Object-level permissions are implemented too. Every resource has ``_patch`` and ``_delete`` boolean attributes.

Login response content format:
::

  {
    "api_key": "...", 
    "auth_tree": 
      {
        "resource_name": 
          {
            "allowed_http_methods":["get", "post", "put", "delete", "patch"],
            "fields":
               {
                "attr1":
                  {
                    "nullable":boolean, "readonly":boolean, "disabled":boolean
                  },
                "_patch": {...},
                "_delete":{...}
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
        "roles_definition":{},
        "publishable_states":
          {
            "added": "Added",
            "ready": "Ready",
            "approved": "Approved",
            "published": "Published",
            "postponed": "Postponed",
            "deleted": "Deleted"
          }
      }
  }

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
          "fields": {...}
        },
        "encyclopedia": {
          "allowed_http_methods": [...],
          "fields": {...}
        },
        "pagedarticle": {
          "allowed_http_methods": [...],
          "fields": {...}
        },
        "recipe": {
          "allowed_http_methods": [...],
          "fields": {...}
        }
      },
      "photo": {
        "allowed_http_methods": [...],
        "fields": {...}
      }
    },
    "system": {
      "publishable_states": {
        "added": "Added",
        "approved": "Approved",
        "deleted": "Deleted",
        "postponed": "Postponed",
        "published": "Published",
        "ready": "Ready"
      },
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
      "roles_definition": {}
    }
  }

