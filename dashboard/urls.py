from django.urls import path
from . import views
app_name='dashboard'
urlpatterns=[
 path('',views.overview,name='overview'),path('device-page/',views.device_page,name='device_page'),
 path('kitchen/',views.kitchen,name='kitchen'),path('bar/',views.bar,name='bar'),
 path('services/',views.services,name='services'),path('orders/',views.orders,name='orders'),
 path('payments/',views.payments,name='payments'),path('workflow/',views.workflow,name='workflow'),
 path('tracking/',views.tracking,name='tracking'),path('devices/',views.devices,name='devices'),
 path('staff/',views.staff,name='staff'),path('settings/',views.settings_page,name='settings'),
 path('web-qr-operation/',views.web_qr_operation,name='web_qr_operation')]
