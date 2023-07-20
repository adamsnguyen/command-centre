from django.contrib import admin
from django.urls import path, include
from device_scheduler.views import AppViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', AppViews.HomeView.as_view(), name='home'),
    path('login/', AppViews.CustomLoginView.as_view(), name='login'),
    path('logout/', AppViews.CustomLogoutView.as_view(), name='logout'),
    path('devices/', AppViews.DeviceListView.as_view(), name='device-list'),
    path('devices/create/', AppViews.device_create, name='device-create'),
    path('devices/<str:name>/', AppViews.DeviceDetailView.as_view(), name='device-detail'),
    path('devices/<str:name>/update/', AppViews.device_update, name='device-update'),
    path('devices/<str:name>/on/', AppViews.device_on, name='device-on'),
    path('devices/<str:name>/off/', AppViews.device_off, name='device-off'),
    path('devices/<str:name>/delete/', AppViews.device_delete, name='device-delete'),
    path('alarms/', AppViews.AlarmListView.as_view(), name='alarm-list'),
    path('alarms/create/', AppViews.alarm_create, name='alarm-create'),
    path('alarms/<int:pk>/', AppViews.AlarmDetailView.as_view(), name='alarm-detail'),
    path('alarms/<int:pk>/update/', AppViews.alarm_update, name='alarm-update'),
    path('alarms/<int:pk>/delete/', AppViews.alarm_delete, name='alarm-delete'),
    path('api/active_alarms/', AppViews.active_alarms, name='active-alarms'),
    path('api/acknowledge_alarms/', AppViews.acknowledge_alarms, name='acknowledge-alarms'),
    path('api/acknowledge_disable/', AppViews.acknowledge_disable, name='acknowledge-disable'),
    path('api/get_devices/', AppViews.get_devices, name='get-devices'),
    path('api/update_device_status/<str:name>', AppViews.update_device_status, name='update-device-status'),
]
