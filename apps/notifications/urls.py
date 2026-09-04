from django.urls import path
from .views import (
    notification_list_view, mark_notification_read_view, mark_all_notifications_read_view
)

urlpatterns = [
    path('', notification_list_view, name='notification_list'),
    path('<int:pk>/read/', mark_notification_read_view, name='mark_notification_read'),
    path('mark-all-read/', mark_all_notifications_read_view, name='mark_all_notifications_read'),
]
