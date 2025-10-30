import pytest
from django.urls import reverse

from comments.api.serializers import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
)
from comments.models import Comment
from main.models import Post

pytestmark = [pytest.mark.django_db]


class TestCommentListCreate:
    def test_permission_for_not_authenticated(self, api, comment):
        response = api.get(reverse("v1:comments:comment-list"))
        response_results = response["results"]

        assert response_results[0]["id"] == comment.pk
        assert response_results[0]["content"] == comment.content
        assert len(response_results) == 1

        response = api.post(
            reverse("v1:comments:comment-list"),
            data={"content": "Test content"},
            expected_status_code=401,
        )

    def test_get_fields(self, api, comment):
        response = api.get(reverse("v1:comments:comment-list"))
        response_results = response["results"]

        serializer = CommentSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response_results[0]

    def test_post_fields(self, api, auth_user, comment, post):
        # Error with no post id
        response = api.post(
            reverse("v1:comments:comment-list"),
            data={"content": "Test content"},
            expected_status_code=400,
        )

        # Normal response
        response = api.post(
            reverse("v1:comments:comment-list"),
            data={"post": post.pk, "content": "Test content"},
            expected_status_code=201,
        )
        serializer = CommentCreateSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

    def test_returning_only_active(self, api, post, mixer):
        comment_1 = mixer.blend(
            Comment, post=post, content="Test content 1", is_active=False
        )
        comment_2 = mixer.blend(
            Comment, post=post, content="Test content 2", is_active=True
        )
        comment_3 = mixer.blend(
            Comment, post=post, content="Test content 3", is_active=True
        )

        response = api.get(reverse("v1:comments:comment-list"))
        response_results = response["results"]

        # Comments ordered by "-created"
        assert response_results[0]["id"] == comment_3.pk
        assert response_results[1]["id"] == comment_2.pk

        assert len(response_results) == 2


class TestCommentDetail:
    def test_permission_for_not_authenticated(self, api, comment):
        response = api.get(
            reverse("v1:comments:comment-detail", kwargs={"pk": comment.pk}),
        )
        assert response["content"] == comment.content

        response = api.api_client.patch(
            reverse("v1:comments:comment-detail", kwargs={"pk": comment.pk}),
            data={"content": "Test content"},
        )
        assert response.status_code == 401

    def test_permission_for_authenticated_but_not_author(self, api, auth_user, mixer):
        comment_1 = mixer.blend(
            Comment,
        )
        response = api.api_client.patch(
            reverse("v1:comments:comment-detail", kwargs={"pk": comment_1.pk}),
            data={"content": "Test content"},
        )
        assert response.status_code == 403

    def test_get_fields(self, api, comment):
        response = api.get(
            reverse("v1:comments:comment-detail", kwargs={"pk": comment.pk})
        )

        serializer = CommentDetailSerializer()
        expected_fields = serializer.fields
        for field in expected_fields:
            assert field in response

    def test_only_active(self, api, auth_user, mixer, post):
        comment_1 = mixer.blend(
            Comment, post=post, content="Test content 1", is_active=False
        )
        response = api.get(
            reverse("v1:comments:comment-detail", kwargs={"pk": comment_1.pk}),
            expected_status_code=404,
        )

    @pytest.mark.parametrize("method", ["put", "patch"])
    @pytest.mark.parametrize(
        "data, validity",
        [
            ({"content": "New content"}, True),
            ({"content": ""}, False),
        ],
    )
    def test_update(self, api, auth_user, comment, method, data, validity):
        if method == "put":
            response = api.api_client.put(
                reverse("v1:comments:comment-detail", kwargs={"pk": comment.pk}),
                data=data,
            )
        if method == "patch":
            response = api.api_client.put(
                reverse("v1:comments:comment-detail", kwargs={"pk": comment.pk}),
                data=data,
            )
        if validity:
            assert response.status_code == 200
            assert response.data["content"] == data["content"]

            # Test response fields
            serializer = CommentUpdateSerializer()
            expected_fields = serializer.fields

            for field in expected_fields:
                assert field in response.data
        else:
            assert response.status_code == 400

    def test_soft_delete(self, api, auth_user, comment, post):
        assert comment.is_active

        # Should just mark as inactive
        response = api.api_client.delete(
            reverse("v1:comments:comment-detail", kwargs={"pk": comment.pk}),
        )
        db_comment = Comment.objects.get(pk=comment.pk)

        assert db_comment.is_active is False


class TestUsersComments:
    def test_permission_for_not_authenticated(self, api, comment):
        response = api.get(
            reverse("v1:comments:users-comments"),
            expected_status_code=401,
        )

        response = api.post(
            reverse("v1:comments:users-comments"),
            data={"content": "Test content"},
            expected_status_code=401,
        )

    def test_get_fields(self, api, auth_user, comment):
        # In comment fixture, author = user fixture
        response = api.get(reverse("v1:comments:users-comments"))
        response_results = response["results"]

        serializer = CommentSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response_results[0]

    def test_returning_all_authored(self, api, auth_user, post, mixer):
        comment_1 = mixer.blend(
            Comment,
            post=post,
            content="Test content 1",
            author=auth_user,
            is_active=False,
        )
        comment_2 = mixer.blend(
            Comment,
            post=post,
            content="Test content 2",
            author=auth_user,
            is_active=False,
        )
        comment_3 = mixer.blend(
            Comment,
            post=post,
            content="Test content 3",
            author=auth_user,
            is_active=True,
        )

        response = api.get(reverse("v1:comments:users-comments"))
        response_results = response["results"]

        # Comments ordered by "-created"
        assert response_results[0]["id"] == comment_3.pk
        assert response_results[1]["id"] == comment_2.pk
        assert response_results[2]["id"] == comment_1.pk

        assert len(response_results) == 3


class TestPostComments:
    def test_permission_and_methods(self, api, comment, post):
        response = api.get(
            reverse("v1:comments:post-comments", kwargs={"post_id": post.pk}),
        )

        # Allowed only GET
        response = api.post(
            reverse("v1:comments:post-comments", kwargs={"post_id": post.pk}),
            expected_status_code=405,
        )

    def test_comments_for_draft_post(self, api, auth_user, mixer, comment):
        post_1 = mixer.blend(Post, publication_status=Post.DRAFT)
        response = api.get(
            reverse("v1:comments:post-comments", kwargs={"post_id": post_1.pk}),
            expected_status_code=404,
        )

    def test_successful_response(self, api, auth_user, mixer, post):
        comment_1 = mixer.blend(
            Comment, post=post, content="Test content 1", is_active=True
        )
        comment_2 = mixer.blend(
            Comment, post=post, content="Test content 2", is_active=False
        )
        comment_3 = mixer.blend(
            Comment, post=post, content="Test content 3", is_active=True
        )

        response = api.get(
            reverse("v1:comments:post-comments", kwargs={"post_id": post.pk}),
        )
        response_comments = response["comments"]
        response_post = response["post"]

        assert response_post["id"] == post.pk
        assert response_post["title"] == post.title
        assert response_post["slug"] == post.slug

        comments_serializer = CommentSerializer()
        expected_fields = comments_serializer.fields
        for field in expected_fields:
            assert field in response_comments[0]

        # Response should contain only "active" comments
        assert len(response_comments) == 2

        db_post = Post.objects.get(pk=post.pk)
        assert response["comments_count"] == db_post.comments_count


class TestCommentReplies:
    def test_permission_and_methods(self, api, comment):
        response = api.get(
            reverse("v1:comments:comment-replies", kwargs={"comment_id": comment.pk}),
        )
        # Allowed only GET
        response = api.post(
            reverse("v1:comments:comment-replies", kwargs={"comment_id": comment.pk}),
            expected_status_code=405,
        )

    def test_replies_for_inactive_comment(self, api, auth_user, mixer, post):
        comment_1 = mixer.blend(
            Comment, post=post, content="Test co1ntent 1", is_active=False
        )
        comment_2 = mixer.blend(
            Comment,
            post=post,
            content="Test content 2",
            is_active=True,
            parent=comment_1,
        )
        # Should still be shown
        response = api.get(
            reverse("v1:comments:comment-replies", kwargs={"comment_id": comment_1.pk})
        )
        assert response["replies"][0]["id"] == comment_2.id
        assert response["replies"][0]["content"] == comment_2.content
        assert response["replies"][0]["author"] == str(comment_2.author.id)

    def test_successful_response(self, api, auth_user, mixer, post):
        comment_1 = mixer.blend(Comment, post=post, content="Test content 1")
        comment_2 = mixer.blend(
            Comment,
            post=post,
            content="Test content ",
            is_active=False,
            parent=comment_1,
        )
        comment_3 = mixer.blend(
            Comment,
            post=post,
            content="Test content 3",
            is_active=True,
            parent=comment_1,
        )
        comment_4 = mixer.blend(
            Comment,
            post=post,
            content="Test content 4",
            is_active=True,
            parent=comment_1,
        )

        response = api.get(
            reverse("v1:comments:comment-replies", kwargs={"comment_id": comment_1.pk}),
        )
        response_parent_comment = response["parent_comment"]
        response_replies = response["replies"]

        serializer = CommentSerializer()
        expected_fields = serializer.fields
        for field in expected_fields:
            assert field in response_parent_comment
            assert field in response_replies[0]

        # Response should contain only "active" replies
        assert len(response_replies) == response["replies_count"] == 2

        # Replies sorted by "-created"
        assert response_replies[0]["content"] == comment_4.content
        assert response_replies[1]["content"] == comment_3.content
