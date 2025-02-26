from django.urls import path
from demo import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    #path('plot/', views.plot_view, name='plot_view'),
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('product_list/', views.product_list_view, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('add_product/', views.add_product_view, name='add_product'),
    path('edit_product/<int:pk>/', views.edit_product_view, name='edit_product'),
    path('delete_product/<int:pk>/', views.delete_product_view, name='delete_product'),
    path('manage_product/', views.manage_product_view, name='manage_product'),
    path('manage_category/', views.manage_category_view, name='manage_category'),
    path('add_category/', views.add_category_view, name='add_category'),
    path('edit_category/<int:pk>/', views.edit_category_view, name='edit_category'),
    path('delete_category/<int:pk>/', views.delete_category_view, name='delete_category'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('remove_from_cart/<int:order_detail_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-history/', views.order_history_view, name='order_history'),
    path('manage-product-stock-owner/', views.manage_product_stock_view, name='manage_product_stock'),
    path('manage-product-stock/', views.manage_product_stock_Staff_view, name='manage_product_stock_staff'),
    path('manage-orders-owner/', views.manage_orders_staff_view, name='manage_orders_staff'),
    path('manage-orders/', views.manage_orders_view, name='manage_orders'),
    path('manage-employees/', views.manage_employees_view, name='manage_employees'),
    path('add-employee/', views.add_employee_view, name='add_employee'),
    path('edit-employee/<int:pk>/', views.edit_employee_view, name='edit_employee'),
    path('delete-employee/<int:pk>/', views.delete_employee_view, name='delete_employee'),
    path('sales_report/', views.generate_sales_report, name='sales_report'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)