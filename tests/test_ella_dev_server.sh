#!/bin/bash
# Script testing functionality of ella-hope dev-server API.

name=sanoma
pass=sanoma

# run via ./test_ella_dev_server.sh <port_number>
server=http://crawler.bfhost.cz:$1

# set to 0 to not test particular API part (otherwise set to 1)
test_schemas=1
test_resource_lists=1
test_core=1
test_photos=1
test_tags=1

resources=( "article" "author" "category" "draft" "format" "formatedphoto" "gallery" "galleryitem" "listing" "photo" "publishable" "site" "source" "user" "wikipage" )


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
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	"$server/admin-api/article/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "Ordered publishable: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	"$server/admin-api/article/?order_by=-publish_from" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	echo "-"

	# Get schemas of resources defined in `resources` array.
	for resource in "${resources[@]}"
	do
		echo -n "$resource schema: "
		curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
		$server/admin-api/$resource/schema/ 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
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
	echo -n "POST article #100: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100,
		"title": "test_article",
		"slug": "test-article",
		"authors": [{
			"id": 100, "resource_uri": "/admin-api/author/100/",
			"name": "dumb_name", "slug": "dumb-name",
			"email": "mail@mail.com",
			"description": "this is descr.",
			"text": "this is text"
		}],
		"category": "/admin-api/category/100/",
		"content": "this is awesome new-article content",
		"description": "this is awesome description",
		"publish_from": "2012-08-07T14:51:29",
		"publish_to": "2012-08-15T14:51:35",
		"state": 3
	}' "$server/admin-api/article/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "POST article #101: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 101,
		"title": "Related article",
		"slug": "related-article",
		"content": "Funky text",
		"description": "Description best ever",
		"authors": ["/admin-api/author/100/"],
		"category": "/admin-api/category/100/",
		"publish_from": "2012-08-07T14:51:29",
		"publish_to": "2012-08-15T14:51:35",
		"state": "added"
	}' "$server/admin-api/article/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "POST gallery #100: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100,
		"title": "Gallery",
		"slug": "1000-year-gallery",
		"content": "So beautiful gallery",
		"description": "Hmm..",
		"authors": ["/admin-api/author/100/"],
		"category": "/admin-api/category/100/",
		"publish_from": "2013-1-14T11:37",
		"publish_to": "3013-1-14T11:37",
		"state": "added"
	}' "$server/admin-api/gallery/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "POST article listing: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100,
		"publishable": "/admin-api/article/100/",
		"category": "/admin-api/category/100/",
		"publish_from": "2013-1-14T11:37",
		"commercial": false
	}' "$server/admin-api/listing/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "POST gallery listing: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 101,
		"publishable": "/admin-api/gallery/100/",
		"category": "/admin-api/category/100/",
		"publish_from": "2013-1-14T11:37",
		"commercial": false
	}' "$server/admin-api/listing/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "POST related article: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"publishable": "/admin-api/article/100/",
		"related": "/admin-api/article/101/"
	}' "$server/admin-api/related/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Deletion of all created `core` objects.
	echo -n "DELETE article listing: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE "$server/admin-api/listing/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE gallery listing: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE "$server/admin-api/listing/101/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE article: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE "$server/admin-api/article/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE article: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE "$server/admin-api/article/101/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

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
	IMAGE_PATH=./example_image.png
	IMAGE_PATH_BASENAME=$(basename $IMAGE_PATH)
	IMAGE_PATH_CHANGED=./example_changed_image.png
	IMAGE_PATH_CHANGED_BASENAME=$(basename $IMAGE_PATH_CHANGED)


	# `Photo` resource creation. (file & JSON in one multipart/form request).
	echo -n "PATCH new photos (like a POST for all included objects): "
	curl --dump-header - -H "$AUTH_HEADER" \
	-X PATCH --form "attached_object=@${IMAGE_PATH}" --form 'resource_data={
		"objects": [{
			"id": 100,
			"title": "Multipart photo",
			"slug": "multipart-photo",
			"description": "Multipart description of photo",
			"width": 256, "height": 256,
			"created": "2012-09-05T10:16:32.131517",
			"authors": ["/admin-api/author/100/"],
			"app_data": "{}",
			"image": "attached_object_id:'$IMAGE_PATH_BASENAME'"
		}]
	}' "$server/admin-api/photo/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `Format` resource creation.
	echo -n "POST format: "
	curl --dump-header - -X POST -H "$AUTH_HEADER" \
	-H "Content-Type: application/json" --data '{
		"id": 100,
		"name": "formatik",
		"nocrop": true,
		"stretch": true,
		"flexible_height": false,
		"resample_quality": 95,
		"max_width": 50, "max_height": 50,
		"sites": [{
			"domain": "web-domain.com",
			"name": "WEB domain"
		}]
	}' "$server/admin-api/format/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `FormatedPhoto` resource creation.
	echo -n "POST formatedphoto with new format: "
	# Problem: tastypie has a bug that doesn’t allow to POST/PUT 3-and-more
	# level nested resources, see: https://github.com/toastdriven/django-tastypie/issues/307,
	# so site may be specified only with resource URI!
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X POST --data '{
		"id": 100,
		"photo": "/admin-api/photo/100/",
		"format": {
			"id": 101,
			"name": "Thumbnail",
			"nocrop": false,
			"stretch": false,
			"flexible_height": false,
			"resample_quality": 95,
			"max_width": 50, "max_height": 50,
			"sites": ["/admin-api/site/1/"]
		}
	}' "$server/admin-api/formatedphoto/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "POST formatedphoto: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X POST --data '{
		"id": 101,
		"photo": "/admin-api/photo/100/",
		"format": "/admin-api/format/100/"
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
		"description": "Modified description by PATCH method.",
		"app_data": null
	}' "$server/admin-api/photo/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# all formated photos will be deleted by image change, so delete them now
	echo -n "DELETE formatedphoto#100: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	 "$server/admin-api/formatedphoto/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE formatedphoto#101: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	 "$server/admin-api/formatedphoto/101/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `Photo` resource alteration via PUT - with image, with multipart/form-data Content-Type.
	echo -n "PATCH photo (with image): "
	curl --dump-header - -X PATCH -H "$AUTH_HEADER" \
	--form "attached_object=@${IMAGE_PATH_CHANGED}" --form 'resource_data={
		"objects": [{
			"resource_uri": "/admin-api/photo/100/",
			"image": "attached_object_id:'$IMAGE_PATH_CHANGED_BASENAME'",
			"description":"Modified photo by PATCH method (image data included).",
			"app_data": null
		}]
	}' "$server/admin-api/photo/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE format#100: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	 "$server/admin-api/format/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE format#101: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	 "$server/admin-api/format/101/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE photo: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	"$server/admin-api/photo/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	echo "-"
fi



if [ $test_tags -eq 1 ];
then
	# `Tag` resource creation.
	echo -n "POST tag #100: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X POST --data '{
		"id": 100,
		"slug": "custom-100",
		"name": "POST tag-100"
	}' "$server/admin-api/tag/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# `Tag` resource creation.
	echo -n "POST tag #101: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X POST --data '{
		"id": 101,
		"name": "Tag#101 by POST",
		"slug": "custom-101",
		"description": "Description of slug #101"
	}' "$server/admin-api/tag/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Testing `article` resource with tags - POST.
	echo -n "POST category: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	 -X POST --data '{
		"app_data": "{}","content": "this is content", "description" : "cat desc",
		"id":100, "resource_uri": "/admin-api/category/100/",
		"site": {
			"id": 100,
			"name": "test-domain.com",
			"domain": "test-domain.com"
		},
		"slug":"category1",
		"template": "category.html",
		"title": "category100", "tree_path": "category100"
	}' "$server/admin-api/category/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "POST article with tags: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X POST --data '{
		"id": 100,
		"title": "Article with tags",
		"slug": "tagged-article",
		"category": "/admin-api/category/100/",
		"content": "This article is tagged (or it should be).",
		"description": "See tags for more info.",
		"publish_from": "2012-08-07T14:51:29",
		"publish_to": "2012-08-15T14:51:35",
		"authors": ["/admin-api/author/100/"],
		"tags": [
			"/admin-api/tag/100/",
			{
				"resource_uri": "/admin-api/tag/101/",
				"main_tag": true
			},
			{
				"id": 102,
				"slug": "art-102",
				"name": "InArticle tag-102"
			},
			{
				"id": 103,
				"slug": "art-103",
				"name": "My favourite tag-103"
			}
		]
	}' "$server/admin-api/article/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Updating article with tags
	echo -n "PUT article with tags: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X PUT --data '{
		"authors": ["/admin-api/author/100/"],
		"tags": [
			{
				"id": 104,
				"slug": "art-104",
				"name": "Taggisimo tag",
				"main_tag": true
			},
			{
				"id": 105,
				"slug": "art-105",
				"name": "2nd favourite :)"
			}
		]
	}' "$server/admin-api/article/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "PATCH article with tags: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X PATCH --data '{
		"app_data": null,
		"tags": [
			"/admin-api/tag/100/",
			"/admin-api/tag/101/",
			{
				"id": 106,
				"slug": "art-106",
				"name": "The taggest tag in the world",
				"main_tag": true
			},
			"/admin-api/tag/105/"
		]
	}' "$server/admin-api/article/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	IMAGE_PATH=./example_image.png
	IMAGE_PATH_BASENAME=$(basename $IMAGE_PATH)

	echo -n "PATCH new photo with tags: "
	curl --dump-header - -H "$AUTH_HEADER" \
	-X PATCH --form "attached_object=@${IMAGE_PATH}" --form 'resource_data={
		"objects": [{
			"id": 100,
			"title": "Photo with tags",
			"slug": "tagged-photo",
			"width": 256, "height": 256,
			"created": "2012-09-05T10:16:32.131517",
			"authors": ["/admin-api/author/100/"],
			"app_data": null,
			"image": "attached_object_id:'$IMAGE_PATH_BASENAME'",
			"tags": [
				"/admin-api/tag/100/",
				{
					"id": 107,
					"slug": "tag-107",
					"name": "Photo tag-107",
					"main_tag": true
				}
			]
		}]
	}' "$server/admin-api/photo/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "Photo has tags: "
	curl --dump-header - -H "$AUTH_HEADER" -X GET "$server/admin-api/photo/100/" 2> /dev/null | \
	grep '"resource_uri": "/admin-api/tag/10[07]/".*"resource_uri": "/admin-api/tag/10[07]/"' > /dev/null && echo "OK" || echo "FAILED"

	echo -n "Article has main tag: "
	curl --dump-header - -H "$AUTH_HEADER" -X GET "$server/admin-api/article/100/" 2> /dev/null | \
	grep '"main_tag": true' > /dev/null && echo "OK" || echo "FAILED"

	# filter articles/photos by tag
	echo -n "Article filtering by tags: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	"$server/admin-api/tag/related/article/100;101;106/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "Photo filtering by tags: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	"$server/admin-api/photo/?tags__in=106,100" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	# Deletion of all tag-related objects.
	echo -n "DELETE photo with tags: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
	"$server/admin-api/photo/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE articles with tags: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X DELETE "$server/admin-api/article/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE category: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X DELETE "$server/admin-api/category/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	echo -n "DELETE site: "
	curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
	-X DELETE "$server/admin-api/site/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'

	for tag_id in {100..107}; do
		echo -n "DELETE tag#$tag_id: "
		curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" \
		-X DELETE "$server/admin-api/tag/$tag_id/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
	done
	echo "-"
fi



echo -n "DELETE author: "
curl --dump-header - -H "Content-Type: application/json" -H "$AUTH_HEADER" -X DELETE \
"$server/admin-api/author/100/" 2> /dev/null | head -n 1 | sed -e 's/HTTP\/1.0 \(.*\)/\1/'
echo "-"



exit 0
