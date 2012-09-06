#!/bin/bash
# script to test functionality of ella-hope dev-server API

# setup
name=seocity
pass=seocity

#server=http://crawler.bfhost.cz:12345
server=http://crawler.bfhost.cz:33333
#server=http://localhost:8000

resources=( "author" "photo" "pagedarticle" "recipe" "site" "encyclopedia" "draft" "user" "publishable" "listing" "article" "category" )

##############
echo "---------------------------------------------"
echo "Tested server: "$server
echo "---------------------------------------------"
api_key=

echo -n "Login - "
api_key=`curl --dump-header - -H "Content-Type: application/json" -X POST --data "username=$name&password=$pass" $server/admin-api/login/ 2> /dev/null | grep "api_key" | sed -e 's/{"api_key": "\([^"]*\)".*}/\1/'`

echo "api_key: $api_key"
echo "name: $name"
echo "pass: $pass"
echo "---------------------------------------------"

# get top_level schema
echo -n "Top level schema: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" $server/admin-api/article/ 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
echo "-"

# get all schemas
for resource in "${resources[@]}"
do
	echo -n "$resource schema: "
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" $server/admin-api/$resource/schema/ 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
done
echo "-"



# get resources lists
for resource in "${resources[@]}"
do
	echo -n "get $resource items: "
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" $server/admin-api/$resource/ 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
done
echo "-"


############################
# post, patch, put, delete na author resource
echo -n "POST author: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{"description": "this is descr", "email": "mail@mail.com", "id": 100, "name": "dumb_name", "resource_uri": "/admin-api/author/100/", "slug":"dumb-name", "text":"this is text"}' "$server/admin-api/author/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

echo -n "PUT author: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X PUT --data '{"description": "this is descr", "email": "mail@mail.com", "id": 100, "name": "dumb_name", "resource_uri": "/admin-api/author/100/", "slug":"dumb-name", "text":"this is text"}' "$server/admin-api/author/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

echo -n "PATCH author: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X PATCH --data '{"description": "this is descr"}' "$server/admin-api/author/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

############################
# post, patch, put, delete na user resource
echo -n "POST user: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{"email": "user@mail.com", "first_name": "test", "id": 100, "is_staff": 1, "is_superuser": 1, "last_name": "user", "password": "heslo", "resource_uri":"/admin-api/user/100/", "username":"test_user"}' "$server/admin-api/user/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'


echo -n "PUT user: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X PUT --data '{"email": "user@mail.com", "first_name": "test", "id": 100, "is_staff": 1, "is_superuser": 1, "last_name": "user", "password": "heslo", "resource_uri":"/admin-api/user/100/", "username":"test_user"}' "$server/admin-api/user/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

echo -n "PATCH user: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X PATCH --data '{"email": "imejl@mejl.com"}' "$server/admin-api/user/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

############################
# POST site resource
echo -n "POST site: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{"domain":"test_domain.com", "id":100, "name": "test_domain.com", "resource_uri": "/admin-api/site/100/"}' "$server/admin-api/site/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

############################
# post category resource
echo -n "POST category: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{"app_data": "{}","content": "this is content","description" : "this is a category description","id":100,"resource_uri": "/admin-api/category/100/","site": "/admin-api/site/100/","slug":"category1","template": "category.html","title":"category100","tree_path":"category100"}' "$server/admin-api/category/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'


############################
# post article resource
echo -n "POST article: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{ "authors": [{ "description": "this is descr.", "email": "mail@mail.com", "id": 100, "name": "dumb_name", "resource_uri": "/admin-api/author/100/", "slug": "dumb-name", "text": "this is text"}], "category": "/admin-api/category/100/", "content":"this is awesome new-article content", "description":"this is awesome description", "id":100, "publish_from": "2012-08-07T14:51:29", "publish_to": "2012-08-15T14:51:35", "resource_uri":"/admin-api/article/100/", "slug": "test-article", "title":"test_article"}' "$server/admin-api/article/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'



# DELETE all created objects #
##############################

echo -n "DELETE article: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X DELETE "$server/admin-api/article/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

echo -n "DELETE category: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X DELETE "$server/admin-api/category/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

echo -n "DELETE site: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X DELETE "$server/admin-api/site/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

echo -n "DELETE user: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X DELETE "$server/admin-api/user/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

echo -n "DELETE author: "
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X DELETE "$server/admin-api/author/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

exit 1

