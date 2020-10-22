from django.conf.urls import url
from django.urls import path
from . import views, admin
from . import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.base, name='home'),
    path('user/register/', views.register, name='register'),
    path('user/login/', views.login, name='login'),
    path('user/Info/', views.user_info, name='getUserInfo'),
    path('admin/login/app/', admin.admin_login, name='admin-login'),
    path('user/logout/', views.logout, name='logout'),
    path('user/delete/', views.delete_account, name='delete-account'),
    path('user/changePassword/', views.change_pass),
    path('user/favorite/', views.user_favorite_foods, ),
    path('user/getAddress/', views.get_user_address,),
    path('user/address/', views.insert_user_address,),
    path('user/order/', views.insert_user_order,),
    path('homeInfo/', views.get_home_info, name='home-info'),
    path('getDetail/', views.get_food_detail, ),
    path('getOrder/', views.get_orders, ),
    path('insertOrder/', views.insert_user_order),
    path('setRate/', views.set_food_rate),
    path('completedOrder/', views.complete_order),
    path('search/', views.search_food),
    path('filter/', views.filter_food),
    path('resInfo/', views.get_res_info),
    path('ticket/', views.ticket),
    path('invoice/', admin.invoice),
    path('filterOrder', admin.filter_order),
    path('orderOfDay', admin.order_of_day),
    path('orderWithDetail', admin.order_with_detail),
    url(r'^resInfo/(?P<res_id>\w+)/$', admin.res_info),
    path('postCode/', admin.post_code),
    path('offer/', admin.offer),
    path('resLocation/', admin.res_location),
    url(r'^resLocation/(?P<location_id>\w+)/$', admin.res_location),
    path('resTime/', admin.res_times),
    url(r'^resTime/(?P<time_id>\w+)/$', admin.res_times),
    path('group/', admin.group),
    url(r'^group/(?P<group_id>\w+)/$', admin.group),
    path('food/', admin.food),
    url(r'^food/(?P<food_id>\w+)/$', admin.food),
    path('option/', admin.option),
    url(r'^option/(?P<option_id>\w+)/$', admin.option),
    path('ordersToday/', admin.orders_today),
    path('resRole/', admin.res_role),
    path('acceptRejectOrder/', admin.accept_reject_order),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
