import pytest
from django.urls import reverse

from main.api.serializers import CategorySerializer, PostListSerializer
from main.models import Category, Post

pytestmark = [pytest.mark.django_db]


class TestCategoryList:
    def test_read_only_for_not_authenticated(self, api):
        response = api.get(reverse("v1:posts:category-list"))

        response = api.post(reverse("v1:posts:category-list"), expected_status_code=401)

    def test_get_fields(self, api, mixer):
        category_1 = mixer.blend(Category, name="Category 1", description="ABC")

        response = api.get(reverse("v1:posts:category-list"))
        response_results = response.get("results")

        serializer = CategorySerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response_results[0]

    def test_response_ordering(self, api, mixer):
        category_1 = mixer.blend(Category, name="Category 1", description="ABC")
        category_2 = mixer.blend(Category, name="Category 2", description="DEF")

        response = api.get(reverse("v1:posts:category-list"))
        response_results = response.get("results")

        # Default ordering is ordering by name
        assert response_results[0]["name"] == category_1.name
        assert response_results[1]["name"] == category_2.name

        response = api.get(reverse("v1:posts:category-list") + "?ordering=-created")
        response_results = response.get("results")

        assert response_results[1]["name"] == category_1.name
        assert response_results[0]["name"] == category_2.name

    def test_response_search(self, api, mixer):
        category_1 = mixer.blend(Category, name="Category 1", description="ABC")
        category_2 = mixer.blend(Category, name="Category 2", description="DEF")

        response = api.get(reverse("v1:posts:category-list") + "?search=f")
        response_results = response.get("results")
        assert response_results[0]["name"] == category_2.name
        assert len(response_results) == 1

    def test_create_category(self, api, auth_user):
        response = api.post(
            reverse("v1:posts:category-list"),
            data={"name": "New Category"},
            expected_status_code=201,
        )

        serializer = CategorySerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response


class TestCategoryDetail:
    def test_read_only_for_not_authenticated(self, api, category):
        response = api.get(
            reverse("v1:posts:category-detail", kwargs={"slug": category.slug}),
        )

        response = api.post(
            reverse("v1:posts:category-detail", kwargs={"slug": category.slug}),
            expected_status_code=401,
        )

    def test_get_fields(self, api, category):
        response = api.get(
            reverse("v1:posts:category-detail", kwargs={"slug": category.slug}),
        )

        serializer = CategorySerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

    @pytest.mark.parametrize("method", ["put", "patch"])
    @pytest.mark.parametrize(
        "data, validity",
        [
            (
                {
                    "name": "Category New Name",
                    "description": "Category New Description",
                },
                True,
            ),
            ({"description": "n"}, False),
        ],
    )
    def test_update(self, api, auth_user, category, method, data, validity):
        if method == "put":
            response = api.api_client.put(
                reverse("v1:posts:category-detail", kwargs={"slug": category.slug}),
                data=data,
            )
        if method == "patch":
            response = api.api_client.put(
                reverse("v1:posts:category-detail", kwargs={"slug": category.slug}),
                data=data,
            )
        if validity:
            assert response.status_code == 200
            assert response.data["name"] == data["name"]
        else:
            assert response.status_code == 400

    def test_delete(self, api, auth_user, category):
        assert Category.objects.filter(slug=category.slug).exists()

        response = api.api_client.delete(
            reverse("v1:posts:category-detail", kwargs={"slug": category.slug})
        )

        assert response.status_code == 204
        assert not Category.objects.filter(slug=category.slug).exists()


class TestPostsByCategory:

    def test_no_category(self, api, auth_user):
        response = api.get(
            reverse(
                "v1:posts:posts-by-category", kwargs={"category_slug": "not-exist"}
            ),
            expected_status_code=404,
        )

    def test_not_valid_method(self, api, category, mixer):
        post_1 = mixer.blend(Post, category=category)

        response = api.post(
            reverse(
                "v1:posts:posts-by-category", kwargs={"category_slug": category.slug}
            ),
            expected_status_code=405,
        )

    def test_get(self, api, category, mixer):
        post_1 = mixer.blend(Post, category=category)
        post_2 = mixer.blend(Post, category=category)
        post_no_category = mixer.blend(
            Post,
        )

        response = api.get(
            reverse(
                "v1:posts:posts-by-category", kwargs={"category_slug": category.slug}
            )
        )

        # Test category response fields
        response_category = response.get("category")
        category_serializer = CategorySerializer()
        for field in category_serializer.fields:
            assert field in response_category
        assert response_category["id"] == category.pk
        assert response_category["name"] == category.name

        # Test posts response fields
        response_posts = response.get("posts")
        posts_serializer = PostListSerializer()
        for field in posts_serializer.fields:
            assert field in response_posts[0]

        # Posts in view ordered by desc "creation"
        assert response_posts[0]["id"] == post_2.id
        assert response_posts[0]["title"] == post_2.title
        assert response_posts[1]["id"] == post_1.id
        assert response_posts[1]["title"] == post_1.title

        assert len(response_posts) == 2
