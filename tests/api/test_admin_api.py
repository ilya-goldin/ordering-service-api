import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_post_categories(api_client_admin, category):
    url = reverse('api:categories-list')
    category(_quantity=5)

    resp = api_client_admin.post(url, data={
        'name': 'New Category',
    })

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_post_shops_fail(api_client_admin, shop):
    url = reverse('api:shops-list')

    resp = api_client_admin.post(url, data={
        'name': 'New Shop',
        'state': False
    })

    assert resp.status_code == status.HTTP_201_CREATED
