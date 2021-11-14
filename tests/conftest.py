import pytest
from model_bakery import baker
from faker import Faker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from api.models import ConfirmEmailToken

fake = Faker()
Faker.seed(1)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_client_auth(user):
    user = user(is_active=True)
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def api_client_partner(user):
    user = user(is_active=True, type='shop')
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def api_client_admin(user):
    user = user(is_active=True, is_staff=True, is_superuser=True)
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user(client, django_user_model):
    def func(is_active=False, **kwargs):
        fake_user = fake.simple_profile()
        user = django_user_model.objects.create_user(
            email=fake_user['mail'],
            password='123secret123',
            username=fake_user['username'],
            **kwargs,
        )
        baker.make('api.Contact', user=user)
        token, _ = ConfirmEmailToken.objects.get_or_create(user=user)
        user.is_active = is_active
        user.save()
        client.force_login(user)
        return user

    return func


@pytest.fixture
def user_factory():
    def func(**kwargs):
        user = baker.make('api.User', **kwargs)
        return user
    return func


@pytest.fixture
def shop():
    def func(**kwargs):
        return baker.make('api.Shop', **kwargs)
    return func


@pytest.fixture
def category():
    def func(**kwargs):
        return baker.make('api.Category', **kwargs)
    return func


@pytest.fixture
def product(category):
    def func(**kwargs):
        category_id = category().id
        return baker.make('api.Product', category_id=category_id, **kwargs)
    return func


@pytest.fixture
def product_info(product, shop):
    def func(**kwargs):
        product_id = product().id
        if 'partner_id' in kwargs.keys():
            shop_id = shop(user_id=kwargs.pop('partner_id')).id
        else:
            shop_id = shop().id
        return baker.make(
            'api.ProductInfo',
            product_id=product_id,
            shop_id=shop_id,
            price=fake.random.randint(1, 10000),
            make_m2m=True,
            **kwargs
        )
    return func


@pytest.fixture
def order():
    def func(**kwargs):
        return baker.make('api.Order', **kwargs)
    return func


@pytest.fixture
def order_items(order, product_info):
    def func(**kwargs):
        data = {}
        if 'partner_id' in kwargs.keys():
            data['partner_id'] = kwargs.pop('partner_id')
        product_info_ = product_info(**data)
        data = {}
        if 'user_id' in kwargs.keys():
            data['user_id'] = kwargs.pop('user_id')
        if 'status' in kwargs.keys():
            data['status'] = kwargs.pop('status')
        order_ = order(**data)
        return baker.make(
            'api.OrderItem',
            order=order_,
            product_info=product_info_,
            quantity=fake.random.randint(1, 100),
            make_m2m=True,
            **kwargs)
    return func
