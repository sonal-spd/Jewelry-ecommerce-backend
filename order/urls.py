from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/stripe-config/', views.GetStripeConfigView.as_view(), name='stripe-config'),
    path('payments/create-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('payments/confirm/', views.ConfirmPaymentView.as_view(), name='confirm-payment'),
    path('payments/create-checkout-session/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('payments/verify-checkout/', views.VerifyCheckoutSessionView.as_view(), name='verify-checkout'),
    path('payments/webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # Coupons
    path('coupons/', views.CouponListView.as_view(), name='coupon-list'),
    path('coupons/<int:pk>/', views.CouponDetailView.as_view(), name='coupon-detail'),
    path('coupons/validate/', views.CouponValidateView.as_view(), name='coupon-validate'),
    path('coupons/usage/', views.CouponUsageListView.as_view(), name='coupon-usage-list'),
]
