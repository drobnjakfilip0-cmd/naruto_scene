from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path("semantic-search/", views.semantic_search),
    path("scene/<int:scene_id>/", views.scene_detail, name='scene_detail')
]