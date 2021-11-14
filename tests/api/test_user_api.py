import json
import pytest
from random import randint
from django.urls import reverse
from rest_framework import status
from api.models import ConfirmEmailToken


@pytest.mark.parametrize(
    ['username', 'email', 'password', 'http_response'],
    (
        ('username1', 'email@mail.ru', '123secret123', status.HTTP_201_CREATED),
        ('username2', 'email.ru', '321secret321', status.HTTP_400_BAD_REQUEST),
        ('username3', 'email3@mail.ru', '123secret321', status.HTTP_201_CREATED),
        ('username4', '', 'passw', status.HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_sign_up(api_client, username, email, password, http_response):
    url = reverse('api:user-register-list')

    resp = api_client.post(url, data={
        'username': username,
        'email': email,
        'password': password,
    })

    assert resp.status_code == http_response


@pytest.mark.django_db
def test_email_confirm(api_client, user):
    user = user()
    url = reverse('api:user-register-confirm-list')
    email = user.email
    token = ConfirmEmailToken.objects.filter(
        user=user,
    ).first().key

    resp = api_client.post(url, data={
        'email': email,
        'token': token,
    })

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_email_confirm_fail(api_client, user):
    user = user()
    url = reverse('api:user-register-confirm-list')
    email = user.email
    token = '12345'

    resp = api_client.post(url, data={
        'email': email,
        'token': token,
    })

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    ['is_active', 'password', 'http_response'],
    (
        (True, '123secret123', status.HTTP_200_OK),
        (False, '123secret123', status.HTTP_400_BAD_REQUEST),
        (True, '5555555123', status.HTTP_400_BAD_REQUEST),
        (False, '5555555123', status.HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_sign_in(api_client, user, is_active, password, http_response):
    url = reverse('api:user-login-list')
    user = user(is_active=is_active)

    resp = api_client.post(url, data={
        'email': user.email,
        'password': password,
    })

    assert resp.status_code == http_response


@pytest.mark.parametrize(
    ['auth', 'http_response', 'count'],
    (
        (True, status.HTTP_200_OK, 1),
        (False, status.HTTP_403_FORBIDDEN, 0),
    )
)
@pytest.mark.django_db
def test_get_account_details(api_client, api_client_auth, auth, http_response, count):
    api_client_auth, _ = api_client_auth
    url = reverse('api:user-details-list')

    if auth:
        resp = api_client_auth.get(url)
    else:
        resp = api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == http_response
    assert resp_json.get('count', 0) == count


@pytest.mark.parametrize(
    ['auth', 'http_response'],
    (
        (True, status.HTTP_404_NOT_FOUND),
        (False, status.HTTP_403_FORBIDDEN),
    )
)
@pytest.mark.django_db
def test_get_account_details_fail(api_client, api_client_auth, user_factory, auth, http_response):
    user_factory(_quantity=5)
    url = reverse('api:user-details-detail', args=(randint(12, 16),))

    if auth:
        resp = api_client_auth[0].get(url)
    else:
        resp = api_client.get(url)

    assert resp.status_code == http_response


@pytest.mark.parametrize(
    ['auth', 'http_response'],
    (
        (True, status.HTTP_200_OK),
        (False, status.HTTP_403_FORBIDDEN),
    )
)
@pytest.mark.django_db
def test_patch_account_details(api_client, api_client_auth, user_factory, auth, http_response):
    user_factory(_quantity=5)
    api_client_auth, user = api_client_auth
    url = reverse('api:user-details-detail', args=(user.id,))
    data = {
        'username': 'new_username',
        'email': 'new_email@mail.com',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'company': 'New Company',
        'position': 'New Position',
    }

    if auth:
        resp = api_client_auth.patch(url, data=data)
    else:
        resp = api_client.patch(url, data=data)

    assert resp.status_code == http_response


@pytest.mark.django_db
def test_get_contacts(api_client_auth):
    api_client, _ = api_client_auth
    url = reverse('api:user-contacts-list')

    resp = api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json.get('results')) == 1


@pytest.mark.django_db
def test_user_get_orders_fail(api_client_auth, api_client_partner, order_items, user):
    api_client, _ = api_client_auth
    url = reverse('api:partner-orders-list')
    _, partner = api_client_partner
    order_items(partner_id=partner.id, user_id=user().id)

    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_categories(api_client_auth, category):
    api_client, _ = api_client_auth
    url = reverse('api:categories-list')
    category(_quantity=5)

    resp = api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json.get('results')) == 5


@pytest.mark.django_db
def test_post_categories_fail(api_client_auth, category):
    api_client, _ = api_client_auth
    url = reverse('api:categories-list')

    resp = api_client.post(url, data={
        'name': 'New Category',
    })

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_shops(api_client_auth, shop):
    api_client, _ = api_client_auth
    url = reverse('api:shops-list')
    shop(_quantity=5)
    shop(state=False, _quantity=3)

    resp = api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json.get('results')) == 5


@pytest.mark.django_db
def test_post_shops_fail(api_client_auth, shop):
    api_client, _ = api_client_auth
    url = reverse('api:shops-list')

    resp = api_client.post(url, data={
        'name': 'New Shop',
        'state': False
    })

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_products_info(api_client, product_info):
    url = reverse('api:products-list')
    product_info(_quantity=10)

    resp = api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json) == 10


@pytest.mark.django_db
def test_list_cart(api_client_auth, order_items):
    url = reverse("api:cart-list")
    api_client, user = api_client_auth
    order_items(user_id=user.id, status='cart')

    resp = api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    for item in resp_json:
        assert item['id']
        assert item['total_sum']
        assert item['status'] == 'cart'


@pytest.mark.django_db
def test_create_cart(api_client_auth, product_info):
    url = reverse("api:cart-list")
    api_client, _ = api_client_auth
    items = product_info(_quantity=10)
    items = [{'product_info': item.id, 'quantity': randint(1, 10)} for item in items]
    items = json.dumps(items)

    resp = api_client.post(url, data={
        'items': items,
    })
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp_json['Создано объектов'] > 0


@pytest.mark.django_db
def test_update_cart(api_client_auth, order_items):
    api_client, user = api_client_auth
    order_item = order_items(user_id=user.id, status='cart')
    items = [{'id': order_item.id, 'quantity': randint(1, 5)}]
    items = json.dumps(items)
    url = reverse('api:cart-detail', args=(order_item.order.id,))

    resp = api_client.patch(url, data={
        'items': items,
    })
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp_json.get('Обновлено объектов', 0) > 0


@pytest.mark.django_db
def test_delete_cart(api_client_auth, order_items):
    api_client, user = api_client_auth
    order_item = order_items(user_id=user.id, status='cart')
    items = [order_item.id]
    url = reverse('api:cart-detail', args=(order_item.order.id,))

    resp = api_client.delete(url, data={
        'items': items,
    })
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json.get('Удалено объектов', 0) > 0


@pytest.mark.django_db
def test_create_order(api_client_auth, order_items):
    url = reverse("api:cart-list")
    api_client, user = api_client_auth
    order_items(user_id=user.id, status='cart')

    resp = api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    for item in resp_json:
        assert item['id']
        assert item['total_sum']
        assert item['status'] == 'cart'