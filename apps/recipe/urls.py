"""
Urls for the Recipe APIs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.recipe import views, views_blob

router = DefaultRouter()
router.register('recipe', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
    path('blob/upload/', views_blob.handle_blob_upload, name='blob-upload'),
    path('blob/list/', views_blob.list_blobs, name='blob-list'),
    path('blob/delete/', views_blob.delete_blob, name='blob-delete'),
    path('blob/generate-url/', views_blob.generate_upload_url, name='blob-generate-url'),
]