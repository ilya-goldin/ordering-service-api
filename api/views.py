import requests
from distutils.util import strtobool
from django.db import IntegrityError
from django.db.models import Sum, F, Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, EmailValidator
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import login, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from yaml import load as load_yaml, Loader
from json import loads as load_json
from .models import Shop, Category, ProductInfo, Product, Parameter, \
    ProductParameter, Order, ConfirmEmailToken, User, Contact, OrderItem
from .permissions import IsPartner, IsShopOwner, IsAdminOrReadOnly
from .serializers import ShopSerializer, OrderSerializer, UserSerializer, \
    ContactSerializer, CategorySerializer, ProductInfoSerializer, OrderItemSerializer


class SignUpViewSet(viewsets.GenericViewSet):
    """
    Класс для регистрации покупателей
    """

    def create(self, request, *args, **kwargs):
        if {'username', 'email', 'password', }.issubset(request.data):
            try:
                validate_password(request.data['password'])
                validate_email = EmailValidator()
                validate_email(request.data['email'])
            except Exception as validate_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in validate_error:
                    error_array.append(item)
                return Response({'Errors': {'password': error_array}}, status=status.HTTP_400_BAD_REQUEST)
            else:
                request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = User.objects.create_user(
                        email=user_serializer.validated_data.get('email'),
                        password=request.data['password'],
                        username=user_serializer.validated_data.get('username'),
                    )
                    token, _ = ConfirmEmailToken.objects.get_or_create(user=user)
                    msg = EmailMultiAlternatives(
                        f"Password Reset Token for {token.user.email}",
                        token.key,
                        settings.EMAIL_HOST_USER,
                        [token.user.email]
                    )
                    msg.send()
                    login(request, user)
                    return Response(user_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)


class EmailConfirmViewSet(viewsets.GenericViewSet):
    """
    Класс для подтверждения почты
    """

    def create(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(
                user__email=request.data['email'],
                key=request.data['token']
            ).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'Status': True}, status=status.HTTP_201_CREATED)
            else:
                return Response({'Errors': 'Неправильно указан токен или email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)


class AccountDetailsViewSet(viewsets.ModelViewSet):
    """
    Класс для работы с данными пользователя
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class ContactViewSet(viewsets.ModelViewSet):
    """
    Класс для работы с адресами пользователя
    """

    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Contact.objects.filter(user=self.request.user.id)
        return queryset


class SignInViewSet(viewsets.GenericViewSet):
    """
    Класс для авторизации пользователя
    """

    def create(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'Token': token.key}, status=status.HTTP_200_OK)
            return Response({'Errors': 'Не удалось авторизовать'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)


class PartnerUpdateViewSet(viewsets.GenericViewSet):
    """
    Класс для обновления прайса от поставщика
    """

    permission_classes = (IsAuthenticated, IsPartner,)

    def create(self, request, *args, **kwargs):
        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                stream = requests.get(url).text
                data = load_yaml(stream, Loader=Loader)

                shop, _ = Shop.objects.get_or_create(
                    name=data['shop'],
                    user_id=request.user.id
                )
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(
                        id=category['id'],
                        name=category['name']
                    )
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(
                        name=item['name'],
                        category_id=item['category']
                    )
                    product_info = ProductInfo.objects.create(
                        product_id=product.id,
                        external_id=item['id'],
                        model=item['model'],
                        price=item['price'],
                        price_rrc=item['price_rrc'],
                        quantity=item['quantity'],
                        shop_id=shop.id
                    )
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(
                            product_info_id=product_info.id,
                            parameter_id=parameter_object.id,
                            value=value
                        )
                return Response(status=status.HTTP_201_CREATED)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)


class PartnerStateViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Класс для работы с статусом поставщика
    """

    permission_classes = (IsAuthenticated, IsPartner, IsShopOwner,)
    serializer_class = ShopSerializer

    def patch(self, request, *args, **kwargs):
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return Response(status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'Errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        queryset = Shop.objects.filter(user=user)
        return queryset


class PartnerOrdersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Класс для работы с заказами поставщика
    """

    permission_classes = (IsAuthenticated, IsPartner,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        orders = Order.objects.filter(
            ordered_items__product_info__shop_id=self.request.user.shop.id
        ).exclude(status='cart').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        return orders


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Класс для просмотра категорий
    """

    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopViewSet(viewsets.ModelViewSet):
    """
    Класс для просмотра списка магазинов
    """

    permission_classes = (IsAdminOrReadOnly,)
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductInfoViewSet(viewsets.GenericViewSet):
    """
    Класс для поиска товаров
    """

    def list(self, request, *args, **kwargs):
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        if shop_id:
            query = query & Q(shop_id=shop_id)
        if category_id:
            query = query & Q(product__category_id=category_id)
        queryset = ProductInfo.objects.filter(query).select_related(
            'shop', 'product__category'
        ).prefetch_related(
            'product_parameters__parameter'
        ).distinct()
        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)


class CartViewSet(viewsets.GenericViewSet):
    """
    Класс для работы с корзиной пользователя
    """

    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        cart = Order.objects.filter(
            user_id=request.user.id, status='cart').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(cart, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError as e:
                return Response({'Errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                cart, _ = Order.objects.get_or_create(
                    user_id=request.user.id,
                    status='cart',
                )
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': cart.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return Response({'Errors': str(error)}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            objects_created += 1
                    else:
                        return Response({'Errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'Создано объектов': objects_created}, status=status.HTTP_201_CREATED)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            cart, _ = Order.objects.get_or_create(
                user_id=request.user.id,
                status='cart',
            )
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=cart.id, id=order_item_id)
                    objects_deleted = True
            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return Response({'Удалено объектов': deleted_count}, status=status.HTTP_200_OK)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                Response({'Errors': 'Неверный формат запроса'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                cart, _ = Order.objects.get_or_create(
                    user_id=request.user.id,
                    status='cart',
                )
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(
                            order_id=cart.id,
                            id=order_item['id'],
                        ).update(
                            quantity=order_item['quantity'],
                        )
                return Response({'Обновлено объектов': objects_updated}, status=status.HTTP_201_CREATED)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.GenericViewSet):
    """
    Класс для получения и размещения заказов пользователями
    """

    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        order = Order.objects.filter(
            user_id=request.user.id).exclude(status='cart').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        status='new')
                except IntegrityError as error:
                    print(error)
                    return Response({'Errors': 'Неправильно указаны аргументы'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if is_updated:
                        msg = EmailMultiAlternatives(
                            "Обновление статуса заказа",
                            'Заказ сформирован',
                            settings.EMAIL_HOST_USER,
                            [request.user.email]
                        )
                        msg.send()
                        return Response(status=status.HTTP_201_CREATED)
        return Response({'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)
