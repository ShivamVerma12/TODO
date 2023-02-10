from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('add-todo/', views.add_todo, name='add-todo'),
    path('update-todo/<int:id>/', views.update_todo, name='update'),
    path('delete-todo/<int:id>/', views.delete_todo),
    path('change-status/<int:id>/<str:status>/', views.change_status),
    path('logout/', views.signout),
    path('changepass/', views.change_password, name='changepass'),
    path('Resend_Otp/', views.Resend_otp, name='Resend_Otp'),
    path('verify/', views.verify, name='verify'),
    path('forget_password/', views.forgetPassword, name='forget_password'),
    path('verify1/', views.verify1, name='verify1'),
    path('password_reset/', views.password_reset, name='password_reset'),

]
