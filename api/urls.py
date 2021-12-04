from django.urls import path, include
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from .views import PartnerUpdateViewSet, PartnerStateViewSet, PartnerOrdersViewSet, SignUpViewSet, \
    EmailConfirmViewSet, AccountDetailsViewSet, ContactViewSet, SignInViewSet, CategoryViewSet, \
    ShopViewSet, ProductInfoViewSet, CartViewSet, OrderViewSet
from rest_framework.routers import DefaultRouter

app_name = 'api'
router_user = DefaultRouter()
router_user.register('register', SignUpViewSet, basename='user-register')
router_user.register('register/confirm', EmailConfirmViewSet, basename='user-register-confirm')
router_user.register('login', SignInViewSet, basename='user-login')
router_user.register('contacts', ContactViewSet, basename='user-contacts')
router_user.register('details', AccountDetailsViewSet, basename='user-details')
router_user.register('cart', CartViewSet, basename='cart')
router_user.register('order', OrderViewSet, basename='order')

router_partner = DefaultRouter()
router_partner.register('update', PartnerUpdateViewSet, basename='partner-update')
router_partner.register('state', PartnerStateViewSet, basename='partner-state')
router_partner.register('orders', PartnerOrdersViewSet, basename='partner-orders')

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('shops', ShopViewSet, basename='shops')
router.register('products', ProductInfoViewSet, basename='products')

urlpatterns = [
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    path('', include(router.urls)),
    path('user/', include(router_user.urls)),
    path('partner/', include(router_partner.urls)),
]
