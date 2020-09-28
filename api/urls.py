from django.urls import path
from . import views
from . import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('', views.home, name='home'),
    path('user/register/', views.register, name='register'),
    path('user/login/', views.login, name='login'),
    path('user/logout/', views.logout, name='logout'),
    path('homeInfo/', views.get_home_info, name='home-info'),
    path('getFood', views.get_food,),
    path('insertOrder/', views.insert_user_order, name='home-info'),
    # path('sendOtp/', views.send_otp, name='send-otp'),
    # path('user/updateProfile/', views.update_profile, name='update-profile'),
    # path('user/', views.get_user_and_profile, name='user-profile-info'),
    # path('user/passwordReminder/', views.password_reminder, name='password-reminder'),


    # path('allUser/', admin.get_all_user, name='all-user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
