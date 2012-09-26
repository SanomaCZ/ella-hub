import os
import django.utils.simplejson as json

from PIL import Image
from nose import tools, SkipTest
from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from django.test.client import MULTIPART_CONTENT
from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed
from ella.core.models import Author
from ella.photos.models import Photo, Format, FormatedPhoto


class TestPhotosResources(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass", True)
        self.client = Client()

        self.author = Author.objects.create(name="Author", slug="author")
        self.photo_filename = self.__create_tmp_image(".test_image.jpg")
        self.photo = Photo.objects.create(id=999, title="Title of photo #999",
            image=self.photo_filename)

    def tearDown(self):
        self.user.delete()
        FormatedPhoto.objects.all().delete()
        Format.objects.all().delete()
        Photo.objects.all().delete()
        Author.objects.all().delete()
        os.remove(self.photo_filename)

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user

    def test_photo_resource_upload(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        file = open(self.photo_filename)
        payload = {
            "image": file,
            "resource_data": json.dumps({
                "objects": [
                    {
                        "id": 100,
                        "title": "Title of photo",
                        "image": "attached_object_id image",
                        "authors": ["/admin-api/author/%d/" % self.author.id],
                        "created": "2012-08-07T14:51:29",
                        "description": "this is description"
                    }
                ]
            }),
        }
        response = self.patch("/admin-api/photo/", payload, **headers)
        tools.assert_equals(response.status_code, 202, response.content)
        file.close()

        response = self.client.get('/admin-api/photo/100/', **headers)
        tools.assert_equals(response.status_code, 200)
        resource = self.__get_response_json(response)
        tools.assert_true('image' in resource)
        tools.assert_true('public_url' in resource)

        self.__logout(headers)

    def test_multiple_upload(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        red_image_path = self.__create_tmp_image(".red.jpg", "red")
        green_image_path = self.__create_tmp_image(".green.jpg", "green")
        blue_image_path = self.__create_tmp_image(".blue.jpg", "blue")

        payload = {
            "red-photo": open(red_image_path),
            "green-photo": open(green_image_path),
            "blue-photo": open(blue_image_path),
            "resource_data": json.dumps({
                "objects": [
                    {
                        "title": "RED photo",
                        "slug": "red-photo",
                        "description": "RED description of photo",
                        "width": 256, "height": 256,
                        "created": "2012-09-05T10:16:32.131517",
                        "authors": ["/admin-api/author/%d/" % self.author.id],
                        "app_data": '{"dominant_color": "red"}',
                        "image": "attached_object_id red-photo"
                    }, {
                        "title": "GREEN photo",
                        "slug": "green-photo",
                        "description": "GREEN description of photo",
                        "width": 256, "height": 256,
                        "created": "2012-09-05T10:16:32.131517",
                        "authors": ["/admin-api/author/%d/" % self.author.id],
                        "app_data": '{"dominant_color": "green"}',
                        "image": "attached_object_id green-photo"
                    }, {
                        "title": "BLUE photo",
                        "slug": "blue-photo",
                        "description": "BLUE description of photo",
                        "width": 256, "height": 256,
                        "created": "2012-09-05T10:16:32.131517",
                        "authors": ["/admin-api/author/%d/" % self.author.id],
                        "app_data": '{"dominant_color": "blue"}',
                        "image": "attached_object_id blue-photo"
                    }
                ]
            }),
        }
        response = self.patch('/admin-api/photo/', payload, **headers)
        tools.assert_equals(response.status_code, 202, response.content)

        self.__logout(headers)

        os.remove(red_image_path)
        os.remove(green_image_path)
        os.remove(blue_image_path)

    @tools.raises(FormatedPhoto.DoesNotExist)
    def test_update_photo_of_formated_photo(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        format = Format.objects.create(name="Base format", max_height=200,
            max_width=200)
        photo = FormatedPhoto.objects.create(
            photo=Photo.objects.get(pk=self.photo.pk), format=format)

        # update photo via API
        file = open(self.photo_filename)
        payload = {
            "unique_id": file,
            "resource_data": json.dumps({
                "objects": [
                    {
                        "resource_uri": "/admin-api/photo/999/",
                        "authors": ["/admin-api/author/%d/" % self.author.id],
                        "description": "PATCHed (image data included).",
                        "image": "attached_object_id unique_id",
                    }
                ]
            }),
        }
        response = self.patch('/admin-api/photo/', payload, **headers)
        tools.assert_equals(response.status_code, 202)
        file.close()

        self.__logout(headers)

        FormatedPhoto.objects.get(pk=photo.pk)

    def patch(self, path, data={}, content_type=MULTIPART_CONTENT, follow=False, **kwargs):
        """Performs a simulated PATCH request to the provided URI."""
        kwargs.update({
            'REQUEST_METHOD': 'PATCH',
        })
        return self.client.post(path, data, content_type, follow, **kwargs)

    def test_download_photo(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get('/admin-api/photo/download/999/', **headers)
        tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

    def test_download_photo_unauthenticated(self):
        response = self.client.get('/admin-api/photo/download/999/')
        tools.assert_equals(response.status_code, 401)

    def test_download_photo_not_get(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.post('/admin-api/photo/download/999/', **headers)
        tools.assert_equals(response.status_code, HttpResponseNotAllowed.status_code)

        self.__logout(headers)

    def test_download_formatedphoto(self):
        """
        This test fails because of issue with Photo model.
        http://stackoverflow.com/questions/3029988/django-gives-i-o-operation-on-closed-file-error-when-reading-from-a-saved-imag
        """
        raise SkipTest()

        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        format = Format.objects.create(name="format_name",
            max_height=200, max_width=200)
        FormatedPhoto.objects.create(photo=self.photo, format=format)

        response = self.client.get('/admin-api/formatedphoto/download/999/', **headers)
        tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

    def test_download_formatedphoto_unauthenticated(self):
        """
        This test fails because of issue with Photo model.
        http://stackoverflow.com/questions/3029988/django-gives-i-o-operation-on-closed-file-error-when-reading-from-a-saved-imag
        """
        raise SkipTest()

        format = Format.objects.create(name="format_name",
            max_height=200, max_width=200)
        FormatedPhoto.objects.create(photo=self.photo, format=format)

        response = self.client.get('/admin-api/formatedphoto/download/999/')
        tools.assert_equals(response.status_code, 401)

    def test_download_formatedphoto_not_get(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.post('/admin-api/formatedphoto/download/999/',
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, HttpResponseNotAllowed.status_code)

        self.__logout(headers)

    def __create_tmp_image(self, filename, colour="black"):
        image = Image.new("RGB", (200, 100), colour)
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        image.save(settings.MEDIA_ROOT + "/" + filename, format="jpeg")
        return settings.MEDIA_ROOT + "/" + filename

    def __login(self, username, password):
        response = self.client.post('/admin-api/login/', data={"username": username, "password": password})
        tools.assert_equals(response.status_code, 200)

        resources = self.__get_response_json(response)
        tools.assert_true("api_key" in resources)

        return resources["api_key"]

    def __logout(self, headers):
        response = self.client.post('/admin-api/logout/', **headers)
        tools.assert_equals(response.status_code, 302)

    def __build_headers(self, username, api_key):
        return {
            "HTTP_AUTHORIZATION": "ApiKey %s:%s" % (username, api_key),
        }

    def __get_response_json(self, response):
        return json.loads(response.content)
