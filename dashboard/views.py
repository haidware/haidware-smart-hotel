from django.shortcuts import render
from django.http import HttpResponse
import qrcode, io
WEB_QR_STORE=[
 {'id':'STR-001','name':'Hotel Cap','category':'Merchandise','price':3500,'stock':12,'qr_generated':True,'active':True,'last_scanned':'5 minutes ago'},
 {'id':'STR-002','name':'HAIDWARE Tote Bag','category':'Merchandise','price':4500,'stock':8,'qr_generated':True,'active':True,'last_scanned':'22 minutes ago'},
 {'id':'STR-003','name':'Bottled Water (500ml)','category':'Consumables','price':500,'stock':50,'qr_generated':True,'active':True,'last_scanned':'1 minute ago'},
 {'id':'STR-004','name':'Snack Pack','category':'Consumables','price':1800,'stock':20,'qr_generated':False,'active':False,'last_scanned':'Never'},
 {'id':'STR-005','name':'Toiletry Kit','category':'Personal Care','price':2200,'stock':15,'qr_generated':True,'active':True,'last_scanned':'2 hours ago'},
 {'id':'STR-006','name':'Premium Chocolate','category':'Consumables','price':1200,'stock':0,'qr_generated':True,'active':False,'last_scanned':'Yesterday'}]
KITCHEN=[
 {'id':'KIT-001','name':'Jollof Rice','category':'Local Dishes','price':3500,'available':True,'description':'Smoky rice served with grilled chicken.'},
 {'id':'KIT-002','name':'Fried Rice','category':'Local Dishes','price':3000,'available':True,'description':'Seasoned rice with vegetables.'},
 {'id':'KIT-003','name':'Chicken Alfredo','category':'Intercontinental','price':6200,'available':True,'description':'Creamy pasta with grilled chicken.'},
 {'id':'KIT-004','name':'Pepper Soup','category':'Soups','price':2800,'available':False,'description':'Hot goat-meat pepper soup.'},
 {'id':'KIT-005','name':'Grilled Chicken','category':'Grills','price':4500,'available':True,'description':'Char-grilled chicken with pepper sauce.'},
 {'id':'KIT-006','name':'Chocolate Cake','category':'Desserts','price':2400,'available':False,'description':'Chocolate sponge with ganache.'}]
BAR=[
 {'id':'BAR-001','name':'Chapman','category':'Soft Drinks','price':2500,'available':True,'description':'Classic Nigerian fruit refreshment.'},
 {'id':'BAR-002','name':'Mojito','category':'Cocktails','price':3500,'available':True,'description':'Mint, lime and soda cocktail.'},
 {'id':'BAR-003','name':'Red Wine','category':'Wines','price':4000,'available':True,'description':'Premium red wine by the glass.'},
 {'id':'BAR-004','name':'Heineken','category':'Beers','price':1500,'available':False,'description':'Chilled 330ml bottle.'},
 {'id':'BAR-005','name':'Premium Whisky','category':'Spirits','price':6500,'available':True,'description':'Premium whisky by the glass.'}]
SERVICES=[
 {'id':'SRV-001','name':'Room Cleaning','category':'Housekeeping','price':2500,'available':True,'note':'Complete room cleaning service.'},
 {'id':'SRV-002','name':'Laundry','category':'Housekeeping','price':3000,'available':True,'note':'Wash, dry and fold.'},
 {'id':'SRV-003','name':'Concierge Request','category':'Reception','price':0,'available':True,'note':'Contact reception for assistance.'},
 {'id':'SRV-004','name':'Airport Taxi','category':'Transport','price':15000,'available':False,'note':'Pre-booked airport transfer.'},
 {'id':'SRV-005','name':'Maintenance','category':'Maintenance','price':0,'available':True,'note':'Report a room fault.'},
 {'id':'SRV-006','name':'Spa Session','category':'Wellness','price':18000,'available':False,'note':'One-hour wellness session.'}]
ORDERS=[
 {'id':'ORD-1024','location':'Room 205','department':'Kitchen','items':'Jollof Rice ×2, Chapman ×1','total':9500,'payment':'Paid','status':'Pending','handler':'Kitchen User','updated':'2 minutes ago'},
 {'id':'ORD-1023','location':'Table 7','department':'Bar','items':'Mojito ×2','total':7000,'payment':'Paid','status':'Preparing','handler':'Bar User','updated':'5 minutes ago'},
 {'id':'ORD-1022','location':'Room 118','department':'Housekeeping','items':'Laundry','total':3000,'payment':'Room Billing','status':'Completed','handler':'Housekeeping','updated':'20 minutes ago'},
 {'id':'ORD-1021','location':'Lounge 2','department':'Kitchen','items':'Chicken Alfredo ×1','total':6200,'payment':'Pending','status':'Pending','handler':'Unassigned','updated':'25 minutes ago'}]
PAYMENTS=[
 {'reference':'PAY-98102','order':'ORD-1024','customer':'Room 205','amount':9500,'gateway':'Paystack','status':'Paid','date':'Today, 10:31'},
 {'reference':'PAY-98101','order':'ORD-1023','customer':'Table 7','amount':7000,'gateway':'Paystack','status':'Paid','date':'Today, 10:27'},
 {'reference':'PAY-98100','order':'ORD-1021','customer':'Lounge 2','amount':6200,'gateway':'Paystack','status':'Pending','date':'Today, 10:14'},
 {'reference':'PAY-98099','order':'ORD-1019','customer':'Room 301','amount':4000,'gateway':'Paystack','status':'Failed','date':'Today, 09:58'}]
DEVICES=[
 {'id':'DEV-001','location':'Room 205','type':'Room','wifi_ssid':'Hotel_Guest_5G','ip':'192.168.1.23','wifi':True,'online':True,'active':True,'last_seen':'10 seconds ago'},
 {'id':'DEV-002','location':'Table 7','type':'Restaurant Table','wifi_ssid':'Hotel_Restaurant','ip':'192.168.1.24','wifi':True,'online':True,'active':True,'last_seen':'8 seconds ago'},
 {'id':'DEV-003','location':'Room 118','type':'Room','wifi_ssid':'Hotel_Guest_5G','ip':'192.168.1.25','wifi':False,'online':False,'active':False,'last_seen':'18 minutes ago'},
 {'id':'DEV-004','location':'Lounge 2','type':'Lounge','wifi_ssid':'Hotel_Lounge','ip':'192.168.1.26','wifi':True,'online':False,'active':True,'last_seen':'3 minutes ago'}]
STAFF=[
 {'name':'Hotel Manager','email':'manager@hotel.com','role':'Manager','status':'Active'},
 {'name':'Kitchen User','email':'kitchen@hotel.com','role':'Kitchen Staff','status':'Active'},
 {'name':'Bar User','email':'bar@hotel.com','role':'Bar Staff','status':'Active'},
 {'name':'Reception Desk','email':'reception@hotel.com','role':'Reception','status':'Active'},
 {'name':'Night Supervisor','email':'night@hotel.com','role':'Manager','status':'Suspended'}]

def base(title,eyebrow,description): return {'page_title':title,'eyebrow':eyebrow,'description':description,'admin_name':'Admin Handler'}
def overview(request):
 all_items=KITCHEN+BAR+SERVICES; visible=[x for x in all_items if x['available']]
 c=base('Smart Hotel Control Center','ADMIN OVERVIEW','Manage available menu items, payment-confirmed orders, tracking updates, handler workflow, IoT WiFi devices, and customer service requests.')
 c.update(metrics=[{'value':len(all_items),'label':'Total Items'},{'value':len(visible),'label':'Visible on Device'},{'value':len([o for o in ORDERS if o['status']=='Pending']),'label':'Pending Orders'},{'value':len(DEVICES),'label':'IoT Devices'}],preview_items=visible[:7],recent_orders=ORDERS[:3]); return render(request,'dashboard/overview.html',c)
def device_page(request):
 c=base('Device Description Page','SMART HOTEL DEVICE','Public-facing product description and authorized admin entry foundation.'); c['features']=['Kitchen Menu','Bar Menu','Hotel Services','Paystack Payment','WiFi IoT Device','Admin Control']; return render(request,'dashboard/device_page.html',c)
def kitchen(request):
 c=base('Kitchen Menu','SMART HOTEL DEVICE','Available items appear on the guest device; unavailable items remain hidden.'); c.update(items=KITCHEN,categories=['All','Local Dishes','Intercontinental','Soups','Grills','Desserts'],item_type='Food'); return render(request,'dashboard/menu.html',c)
def bar(request):
 c=base('Bar Menu','SMART HOTEL DEVICE','Control which drinks are available for guests to browse and order.'); c.update(items=BAR,categories=['All','Soft Drinks','Cocktails','Wines','Beers','Spirits'],item_type='Drink'); return render(request,'dashboard/menu.html',c)
def services(request):
 c=base('Services','SMART HOTEL DEVICE','Manage guest-facing hotel services and route requests to the correct department.'); c.update(items=SERVICES,categories=['All','Housekeeping','Reception','Transport','Maintenance','Wellness']); return render(request,'dashboard/services.html',c)
def orders(request):
 c=base('Orders','ORDERS','Review guest orders by room or table, department, payment state and fulfilment status.'); c.update(orders=ORDERS,metrics=[{'value':len(ORDERS),'label':'Total Orders'},{'value':len([o for o in ORDERS if o['status']=='Pending']),'label':'Pending'},{'value':len([o for o in ORDERS if o['status']=='Preparing']),'label':'Preparing'},{'value':len([o for o in ORDERS if o['status']=='Completed']),'label':'Completed'}]); return render(request,'dashboard/orders.html',c)
def payments(request):
 paid=[p for p in PAYMENTS if p['status']=='Paid']; pending=[p for p in PAYMENTS if p['status']=='Pending']; failed=[p for p in PAYMENTS if p['status']=='Failed']
 c=base('Payment Management','ORDERS','Track Paystack records, pending transactions and confirmed revenue.'); c.update(payments=PAYMENTS,metrics=[{'value':f"₦{sum(p['amount'] for p in paid):,}",'label':'Confirmed'},{'value':f"₦{sum(p['amount'] for p in pending):,}",'label':'Pending'},{'value':len(failed),'label':'Failed'},{'value':f"₦{sum(p['amount'] for p in paid):,}",'label':'Today'}]); return render(request,'dashboard/payments.html',c)
def workflow(request):
 c=base('Handler Workflow','HANDLER WORKFLOW','Standard operating flow from payment confirmation to service delivery.'); c['steps']=[('Payment Confirmed','Order details enter the admin portal.'),('Department Assignment','Kitchen, bar, housekeeping or reception receives the request.'),('Preparation','Staff processes the request and updates its status.'),('Delivery / Completion','The handler marks the order or request as completed.')]; return render(request,'dashboard/workflow.html',c)
def tracking(request):
 c=base('Tracking Updates','TRACKING UPDATES','Monitor order movement and department responsibility.'); c['orders']=ORDERS; return render(request,'dashboard/tracking.html',c)
def devices(request):
 c=base('Device Management','IOT DEVICE SYSTEM','Monitor each IoT WiFi device, connection state, operating permission and heartbeat.'); c.update(devices=DEVICES,metrics=[{'value':len(DEVICES),'label':'Total Devices'},{'value':len([d for d in DEVICES if d['wifi']]),'label':'WiFi Connected'},{'value':len([d for d in DEVICES if d['active']]),'label':'Active Devices'},{'value':len([d for d in DEVICES if not d['online']]),'label':'Offline / Faulty'}]); return render(request,'dashboard/devices.html',c)
def staff(request):
 c=base('Staff Access','STAFF ACCESS','Manage hotel staff roles and future access permissions.'); c['staff_members']=STAFF; return render(request,'dashboard/staff.html',c)
def web_qr_operation(request):
 rooms=[{'id':d['id'],'location':d['location'],'type':d['type'],'online':d['online'],'active':d['active']} for d in DEVICES]
 active=[r for r in rooms if r['active']]
 c=base('Web QR Operation','WEB QR OPERATION','Each room has a unique QR code that links guests directly to the web device page — where they can browse menus, order, and pay.')
 c.update(rooms=rooms,metrics=[{'value':len(rooms),'label':'Total Rooms'},{'value':len(active),'label':'Active Rooms'},{'value':len([r for r in rooms if r['online']]),'label':'Online Now'},{'value':len([r for r in rooms if not r['active']]),'label':'QR Disabled'}]); return render(request,'dashboard/web_qr_operation.html',c)

def qr_code(request, room_id):
 room_id_clean=room_id.replace('..','/').strip()
 guest_url=request.build_absolute_uri(f'/guest/{room_id_clean}/')
 img=qrcode.make(guest_url)
 buf=io.BytesIO(); img.save(buf,'PNG'); buf.seek(0)
 return HttpResponse(buf.read(),content_type='image/png')

def guest_device(request, room_id):
 room=next((d for d in DEVICES if d['id']==room_id),None)
 all_menu=KITCHEN+BAR; available_menu=[x for x in all_menu if x['available']]
 available_services=[s for s in SERVICES if s['available']]
 c={'page_title':f"{room['location'] if room else room_id} — Guest Device",'room':room,'room_id':room_id,'menu_items':available_menu,'services':available_services}
 return render(request,'dashboard/guest_device.html',c)
def settings_page(request): return render(request,'dashboard/settings.html',base('Settings','SYSTEM SETTINGS','Configure hotel identity, future integrations and IoT operating rules.'))
