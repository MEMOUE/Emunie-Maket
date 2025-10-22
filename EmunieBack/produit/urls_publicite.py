from django.urls import path
from . import views

app_name = 'publicite'

urlpatterns = [
    path('', views.AdvertisementListView.as_view(), name='advertisement_list'),
    path('create/', views.AdvertisementCreateView.as_view(), name='advertisement_create'),
    path('my/', views.MypubliciteView.as_view(), name='my_publicite'),
    path('<int:pk>/', views.AdvertisementDetailView.as_view(), name='advertisement_detail'),
    path('<int:pk>/statistics/', views.advertisement_statistics, name='advertisement_statistics'),
    path('<int:pk>/impression/', views.track_ad_impression, name='track_ad_impression'),
    path('<int:pk>/click/', views.track_ad_click, name='track_ad_click'),
]
