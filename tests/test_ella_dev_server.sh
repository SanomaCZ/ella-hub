#!/bin/bash
# script to test functionality of ella-hope dev-server API

# setup
name=seocity
pass=seocity

#server=http://crawler.bfhost.cz:12345
server=http://crawler.bfhost.cz:33333
#server=http://crawler.bfhost.cz:44444

# test top-level & resource-specific schemas?
test_schemas=0
test_resource_lists=0
test_core=0
test_photos=1

resources=( "author" "pagedarticle" "recipe" "site" "encyclopedia" "draft" "user" "publishable" "listing" "article" "category" "photo" "formatedphoto" "format")


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






if [ $test_schemas -eq 1 ];
then
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
fi






if [ $test_resource_lists -eq 1 ];
then
	# get resources lists
	for resource in "${resources[@]}"
	do
		echo -n "get $resource items: "
		curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" $server/admin-api/$resource/ 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	done
	echo "-"
fi





if [ $test_core -eq 1 ];
then
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
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{ "authors": [{ "description": "this is descr.", "email": "mail@mail.com", "id": 100, "name": "dumb_name", "resource_uri": "/admin-api/author/100/", "slug": "dumb-name", "text": "this is text"}], "category": "/admin-api/category/100/", "content":"this is awesome new-article content", "description":"this is awesome description", "id":100, "publish_from": "2012-08-07T14:51:29", "publish_to": "2012-08-15T14:51:35", "resource_uri":"/admin-api/article/100/", "slug": "test-article", "title":"test_article", "state":3}' "$server/admin-api/article/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

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
	echo "-"
fi



if [ $test_photos -eq 1 ];
then
	############################
	# POST photo resource
	echo -n "POST photo: "
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{"app_data": "{}", "id": 100, "created": "2012-09-05T10:16:32.131517", "description": "this is desc", "image": "1-fotka.png", "height": 256, "important_bottom": null, "important_left": null, "important_right": null, "important_top": null, "resource_uri": "/admin-api/photo/100/", "slug": "1-fotka", "title": "fotka", "width": 256}' "$server/admin-api/photo/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	############################
	# POST format resource
	echo -n "POST format: "
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{"id": 100, "resource_uri": "/admin-api/format/100/", "flexible_height": false, "flexible_max_height": null, "max_height": 200, "max_width": 34, "name": "formatik", "nocrop": true, "resample_quality": 95, "sites": [{"domain": "domain2.com", "id": 3, "name": "domain2.com", "resource_uri": "/admin-api/site/3/"}], "stretch": true}' "$server/admin-api/format/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'


	############################
	# POST formatedphoto resource
	echo -n "POST formatedphoto: "
# Problem: tastypie has a bug that doesn’t allow to POST/PUT 3-and-more level nested resources, see: https://github.com/toastdriven/django-tastypie/issues/307, so format may be specified only with resource URI!
#	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{"resource_uri": "/admin-api/formatedphoto/100/", "crop_height": 0, "crop_left": 0, "crop_top": 0, "crop_width": 0, "id": 100, "format": { "flexible_height": false, "flexible_max_height": null, "id": 200, "max_height": 200, "max_width": 34, "name": "formatik", "nocrop": true, "resample_quality": 95, "resource_uri": "/admin-api/format/200/", "sites": [{ "domain": "domain2.com", "id": 3, "name": "domain2.com", "resource_uri": "/admin-api/site/3/"}], "stretch": true}, "height": 200, "photo": "/admin-api/photo/1/", "width": 200}' "$server/admin-api/formatedphoto/"
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X POST --data '{"resource_uri": "/admin-api/formatedphoto/100/", "crop_height": 0, "crop_left": 0, "crop_top": 0, "crop_width": 0, "id": 100, "format": "/admin-api/format/100/", "height": 200, "photo": "/admin-api/photo/1/", "width": 200}' "$server/admin-api/formatedphoto/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/' 


	echo -n "DELETE formatedphoto: "
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X DELETE "$server/admin-api/formatedphoto/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE format: "
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X DELETE "$server/admin-api/format/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE photo: "
	curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey $name:$api_key" -X DELETE "$server/admin-api/photo/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	echo "-"
fi


exit 1
