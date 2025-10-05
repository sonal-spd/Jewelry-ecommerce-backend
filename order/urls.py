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
    
    # Coupons
    path('coupons/', views.CouponListView.as_view(), name='coupon-list'),
    path('coupons/validate/', views.CouponValidateView.as_view(), name='coupon-validate'),
    path('coupons/usage/', views.CouponUsageListView.as_view(), name='coupon-usage-list'),
]
