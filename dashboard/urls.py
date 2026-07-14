from django.urls import path
from . import views
from . import auth_views
app_name='dashboard'
urlpatterns=[
 path('',auth_views.admin_entry,name='admin_entry'),
 path('admin-login/',auth_views.admin_login,name='admin_login'),
 path('admin-signup/',auth_views.admin_signup,name='admin_signup'),
 path('admin-logout/',auth_views.admin_logout,name='admin_logout'),
 path('dashboard/',views.overview,name='overview'),path('device-page/',views.device_page,name='device_page'),
 path('app-web/',views.app_web,name='app_web'),
 path('kitchen/',views.kitchen,name='kitchen'),path('bar/',views.bar,name='bar'),
 path('services/',views.services,name='services'),path('orders/',views.orders,name='orders'),
 path('payments/',views.payments,name='payments'),path('workflow/',views.workflow,name='workflow'),
 path('tracking/',views.tracking,name='tracking'),path('devices/',views.devices,name='devices'),
 path('staff/',views.staff,name='staff'),path('settings/',views.settings_page,name='settings'),
 path('web-qr-operation/',views.web_qr_operation,name='web_qr_operation'),
 path('api/web-qr/bootstrap/',views.web_qr_sync_bootstrap,name='web_qr_sync_bootstrap'),
 path('qr/<str:room_id>/',views.qr_code,name='qr_code'),
 path('guest/<str:room_id>/',views.guest_device,name='guest_device')]
