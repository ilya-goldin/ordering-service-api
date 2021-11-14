import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_shop_update(api_client_partner):
    url = reverse('api:partner-update-list')
    api_client, _ = api_client_partner

    resp = api_client.post(url, data={
        'url': 'https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml'
    })

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_get_status(api_client_partner, shop):
    url = reverse('api:partner-state-list')
    api_client, user = api_client_partner
    shops = shop(user=user)

    resp = api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json.get('results')[0].get('id') == shops.id
    assert resp_json.get('results')[0].get('state') == shops.state


@pytest.mark.parametrize(
    ['status_', 'http_response'],
    (
        (True, status.HTTP_200_OK),
        (False, status.HTTP_200_OK),
    )
)
@pytest.mark.django_db
def test_update_status(api_client_partner, shop, status_, http_response):
    url = reverse('api:partner-state-list')
    api_client, user = api_client_partner
    shop(user=user)

    resp = api_client.patch(url, data={
        'state': status_,
    })

    assert resp.status_code == http_response


@pytest.mark.django_db
def test_get_orders(api_client_partner, order_items, user):
    url = reverse('api:partner-orders-list')
    api_client, partner = api_client_partner
    order_items(partner_id=partner.id, user_id=user().id)

    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
