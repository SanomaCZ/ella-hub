#!/bin/bash
# Script testing functionality of ella-hope dev-server API.

name=seocity
pass=seocity

# run via ./test_ella_dev_server.sh <port_number>
server=http://crawler.bfhost.cz:$1

# set to 0 to not test particular API part (otherwise set to 1)
test_schemas=1
test_resource_lists=1
test_core=1
test_photos=1

resources=( "article" "author" "category" "draft" "encyclopedia" "format" "formatedphoto" "gallery" "galleryitem" "listing" "photo" "publishable" "recipe" "site" "source" "user" "wikipage" )


echo "---------------------------------------------"
echo "Tested server: "$server
echo "---------------------------------------------"
api_key="NO_APIKEY"

echo -n "Login - "
api_key=`curl --dump-header - -H "Content-Type: application/json" -X POST --data "username=$name&password=$pass" $server/admin-api/login/ 2> /dev/null | grep "api_key" | sed -e 's/{"api_key": "\([^"]*\)".*}/\1/'`

echo "api_key: $api_key"
echo "name: $name"
echo "pass: $pass"
echo "---------------------------------------------"

AUTH_HEADER="Authorization: ApiKey $name:$api_key"



if [ $test_schemas -eq 1 ];
then
	# Get top-level schema.
	echo -n "Top level schema: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" $server/admin-api/article/ 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	echo "-"
	# Get schemas of resources defined in `resources` array.
	for resource in "${resources[@]}"
	do
		echo -n "$resource schema: "
		curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" $server/admin-api/$resource/schema/ 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	done
	echo "-"
fi



if [ $test_resource_lists -eq 1 ];
then
	# Get whole lists of resources defined in `resourced` array.
	for resource in "${resources[@]}"
	do
		echo -n "get $resource items: "
		curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" $server/admin-api/$resource/ 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	done
	echo "-"
fi



echo -n "POST author: "
curl --dump-header - -X POST -H "$AUTH_HEADER" \
-H "Content-Type: application/json" --data '{
	"id": 100, "resource_uri": "/admin-api/author/100/",
	"name": "dumb_name", "description": "this is descr",
	"email": "mail@mail.com", "slug":"dumb-name", "text":"this is text"
}' "$server/admin-api/author/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
echo "-"



if [ $test_core -eq 1 ];
then
	# Testing `author` resource -POST/PUT/PATCH/DELETE.
	echo -n "PUT author: "
	curl --dump-header - -X PUT -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100, "resource_uri": "/admin-api/author/100/",
		"name": "dumb_name", "description": "this is descr",
		"email": "mail@mail.com", "slug":"dumb-name", "text":"this is text"
	}' "$server/admin-api/author/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "PATCH author: "
	curl --dump-header - -X PATCH -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"description": "this is descr"
	}' "$server/admin-api/author/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Testing `user` resource - POST/PUT/PATCH/DELETE.
	echo -n "POST user: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100, "resource_uri":"/admin-api/user/100/",
		"username":"test_user", "first_name": "test", "last_name": "user",
		"email": "user@mail.com", "password": "heslo",
		"is_staff": 1, "is_superuser": 1
	}' "$server/admin-api/user/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "PUT user: "
	curl --dump-header - -X PUT -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100, "resource_uri":"/admin-api/user/100/",
		"username":"test_user", "first_name": "test", "last_name": "user",
		"email": "mail@mail.com", "password": "heslo",
		"is_staff": 1, "is_superuser": 1
	}' "$server/admin-api/user/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "PATCH user: "
	curl --dump-header - -X PATCH -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"email": "imejl@mejl.com"
	}' "$server/admin-api/user/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Testing `site` resource - POST/DELETE.
	echo -n "POST site: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100, "resource_uri": "/admin-api/site/100/",
		"name": "test_domain.com", "domain": "test_domain.com"
	}' "$server/admin-api/site/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Testing `category` resource -POST/DELETE.
	echo -n "POST category: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"app_data": "{}","content": "this is content", "description" : "cat desc",
		"id":100, "resource_uri": "/admin-api/category/100/",
		"site": "/admin-api/site/100/","slug":"category1",
		"template": "category.html",
		"title": "category100", "tree_path": "category100"
	}' "$server/admin-api/category/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Testing `article` resource - POST/DELETE.
	echo -n "POST article: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100, "resource_uri":"/admin-api/article/100/",
		"title":"test_article", "state":3, "slug": "test-article",
		"authors": [{
			"id": 100, "resource_uri": "/admin-api/author/100/",
			"name": "dumb_name", "slug": "dumb-name",
			"description": "this is descr.", "email": "mail@mail.com", "text": "this is text"
		}],
		"category": "/admin-api/category/100/",
		"content": "this is awesome new-article content",
		"description": "this is awesome description",
		"publish_from": "2012-08-07T14:51:29", "publish_to": "2012-08-15T14:51:35"
	}' "$server/admin-api/article/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Deletion of all created `core` objects.
	echo -n "DELETE article: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE "$server/admin-api/article/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE category: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE "$server/admin-api/category/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE site: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE "$server/admin-api/site/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE user: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE "$server/admin-api/user/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	echo "-"
fi



if [ $test_photos -eq 1 ];
then
	IMAGE_PATH=./media/photos/example_image.png
	IMAGE_PATH_CHANGED=./media/photos/example_changed_image.png


	# `Photo` resource creation. (file & JSON in one multipart/form request).
	echo -n "POST photo: "
	curl --dump-header - -H "$AUTH_HEADER" \
	-X PATCH --form "image=@${IMAGE_PATH}" --form 'resource_data={
		"objects": [{
			"id": 100,
			"title": "Multipart photo",
			"slug": "multipart-photo",
			"description": "Multipart description of photo",
			"width": 256, "height": 256,
			"created": "2012-09-05T10:16:32.131517",
			"authors": ["/admin-api/author/100/"],
			"app_data": "{}",
			"image": "attached_object_id image"
		}]
	}' "$server/admin-api/photo/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `Format` resource creation.
	echo -n "POST format: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100, "resource_uri": "/admin-api/format/100/",
		"flexible_height": false, "flexible_max_height": null,
		"max_height": 200, "max_width": 34,
		"name": "formatik", "nocrop": true, "resample_quality": 95,
		"sites": [{
			"domain": "example.com",
			"id": 1, "resource_uri": "/admin-api/site/1/",
			"name": "example.com"
		}], "stretch": true
	}' "$server/admin-api/format/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `FormatedPhoto` resource creation.
	echo -n "POST formatedphoto: "
	# Problem: tastypie has a bug that doesn’t allow to POST/PUT 3-and-more
	# level nested resources, see: https://github.com/toastdriven/django-tastypie/issues/307,
	# so format may be specified only with resource URI!
	: `
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100, "resource_uri": "/admin-api/formatedphoto/100/",
		"crop_height": 0, "crop_left": 0, "crop_top": 0, "crop_width": 0,
		"format": {
			"flexible_height": false, "flexible_max_height": null,
			"id": 100, "resource_uri": "/admin-api/format/100/",
			"max_height": 200, "max_width": 34,
			"name": "formatik",
			"nocrop": true, "resample_quality": 95,
			"sites": [{
				"id": 1, "resource_uri": "/admin-api/site/1/",
				"domain": "example.com", "name": "example.com"
			}],
			"stretch": true
		},
		"height": 200, "width": 200,
		"photo": "/admin-api/photo/100/"
	}' "$server/admin-api/formatedphoto/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	`
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100, "resource_uri": "/admin-api/formatedphoto/100/",
		"crop_height": 0, "crop_left": 0, "crop_top": 0, "crop_width": 0,
		"format": "/admin-api/format/100/",
		"height": 200, "width": 200,
		"photo": "/admin-api/photo/100/"
	}' "$server/admin-api/formatedphoto/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `Photo` resource alteration via PUT - without image, without multipart/form-data Content-Type.
	echo -n "PUT photo (without image): "
	curl --dump-header - -X PUT -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"title": "Modified photo by PUT method",
		"authors": ["/admin-api/author/100/"],
		"description": "Modified description by PUT method."
	}' "$server/admin-api/photo/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `Photo` resource alteration via PATCH - without image, without multipart/form-data Content-Type.
	echo -n "PATCH photo (without image): "
	curl --dump-header - -X PATCH -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"title": "Modified photo by PATCH method",
		"description": "Modified description by PATCH method."
	}' "$server/admin-api/photo/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `Photo` resource alteration via PUT - with image, with multipart/form-data Content-Type.
	echo -n "PATCH photo (with image): "
	curl --dump-header - -X PATCH -H "$AUTH_HEADER" \
	--form "some_unique_id=@${IMAGE_PATH_CHANGED}" --form 'resource_data={
		"objects": [{
			"resource_uri": "/admin-api/photo/100/",
			"image": "attached_object_id some_unique_id",
			"description":"Modified photo by PATCH method (image data included)."
		}]
	}' "$server/admin-api/photo/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Deletion of all photo-related objects.
	echo -n "DELETE formatedphoto: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	 "$server/admin-api/formatedphoto/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE format: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	 "$server/admin-api/format/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE photo: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	"$server/admin-api/photo/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	echo "-"
fi



echo -n "DELETE author: "
curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
"$server/admin-api/author/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
echo "-"



exit 0
