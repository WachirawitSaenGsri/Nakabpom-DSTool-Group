from django.urls import path
from demo import views

urlpatterns = [
    path('', views.plot_view, name='plot_view'),
]