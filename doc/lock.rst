===========================
Locking publishable objects
===========================

.. secnum
.. contents::


All models that inherits from `ella.core.modelsPublishable` may be locked.
Lock is represented by model `ella_hub.models.PublishableLock` with
extended manager. Lock doesn't protect publishable object from concurrent
modification. It's only information that someone else is working with
publishable object. User can decide to edit publishable object despite
of this lock, but her work may be corrupted.

Lock manager has three methods for manipulating with locks.


- `PublishableLock.lock`(publishable, user)

Locks publishable object for user. Returns created lock or `None` if
publishable object is already locked.


- `PublishableLock.unlock`(publishable)

Unlocks publishable object. Publishable may be unlocked by any user.


- `PublishableLock.is_locked`(publishable)

Returns instance of `PublishableLock` if publishable object is locked
or `None` otherwise.



PublishableLock structure
-------------------------

- required attributes:
    - publishable <fk>
    - locked_by

- optional attributes:

- auto-defined attributes:
    - timestamp


Manipulating with locks via API
-------------------------------

There are 3 main endpoints.


Lock publishable object by sending POST request to the URL below. Returned JSON
object contains field 'locked' with boolean value `true` if publishable object
is locked by current user. Value `false` is returned if publishable object
was (and still is) locked by someone else.

 ::

    http://crawler.bfhost.cz:12345/admin-api/lock-publishable/<publishable_id>/
    http://crawler.bfhost.cz:12345/admin-api/lock-publishable/1/

 ::

    {"locked": true}

*cURL variant*
 ::

     curl --dump-header - -H "Content-Type: application/json" -X POST "http://crawler.bfhost.cz:12345/admin-api/lock-publishable/1/?format=json&username=<username>&api_key=<api_key_for_user>"


Unlock publishable object by sending POST request to the URL below. No data are
returned and object is always unlocked.

 ::

    http://crawler.bfhost.cz:12345/admin-api/unlock-publishable/<publishable_id>/
    http://crawler.bfhost.cz:12345/admin-api/unlock-publishable/1/

*cURL variant*
 ::

     curl --dump-header - -H "Content-Type: application/json" -X POST "http://crawler.bfhost.cz:12345/admin-api/unlock-publishable/1/?format=json&username=<username>&api_key=<api_key_for_user>"


Determine if publishable object is locked by sending GET request to the URL below.
Returned object contains field 'locked' with boolean value. If publishable
object is locked then 2 more fields with lock information are returned.

 ::

    http://crawler.bfhost.cz:12345/admin-api/is-publishable-locked/<publishable_id>/
    http://crawler.bfhost.cz:12345/admin-api/is-publishable-locked/1/

*Returned structure if publishable object is locked*
 ::

    {
        "locked": true,
        "locked_at": "2012-08-24T08:48:53.813675",
        "locked_by": "/admin-api/user/1/"
    }

*Returned structure if publishable object is not locked*
 ::

    {
        "locked": false
    }

*cURL variant*
 ::

     curl --dump-header - -H "Content-Type: application/json" -X GET "http://crawler.bfhost.cz:12345/admin-api/is-publishable-locked/1/?format=json&username=<username>&api_key=<api_key_for_user>"

