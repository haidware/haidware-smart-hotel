from django.db import models


class MenuItem(models.Model):
 id=models.CharField(max_length=32,primary_key=True)
 section=models.CharField(max_length=32)  # Kitchen or Bar
 name=models.CharField(max_length=120)
 category=models.CharField(max_length=64)
 price=models.PositiveIntegerField(default=0)
 available=models.BooleanField(default=True)
 description=models.TextField(blank=True)


class ServiceItem(models.Model):
 id=models.CharField(max_length=32,primary_key=True)
 name=models.CharField(max_length=120)
 category=models.CharField(max_length=64)
 price=models.PositiveIntegerField(default=0)
 available=models.BooleanField(default=True)
 note=models.TextField(blank=True)


class Device(models.Model):
 id=models.CharField(max_length=32,primary_key=True)
 location=models.CharField(max_length=120)
 type=models.CharField(max_length=64)
 wifi_ssid=models.CharField(max_length=120)
 ip=models.CharField(max_length=64)
 wifi=models.BooleanField(default=True)
 online=models.BooleanField(default=True)
 active=models.BooleanField(default=True)
 last_seen=models.CharField(max_length=64,default='just now')


class BankAccount(models.Model):
 bank=models.CharField(max_length=64,unique=True)
 name=models.CharField(max_length=120)
 number=models.CharField(max_length=32)
 icon=models.CharField(max_length=8,default='B')
 bg=models.CharField(max_length=32,default='#f1e8f8')
 fg=models.CharField(max_length=32,default='#2a0b46')
 active=models.BooleanField(default=True)
 display_order=models.PositiveIntegerField(default=1)

 class Meta:
  ordering=['display_order','bank']


class PaymentRecord(models.Model):
 reference=models.CharField(max_length=64,unique=True)
 order=models.CharField(max_length=64)
 customer=models.CharField(max_length=120)
 amount=models.PositiveIntegerField(default=0)
 method=models.CharField(max_length=64)
 account=models.CharField(max_length=32)
 status=models.CharField(max_length=64,default='Pending Confirmation')
 date=models.CharField(max_length=64,blank=True)
 created_at=models.DateTimeField(auto_now_add=True)

 class Meta:
  ordering=['-created_at']
