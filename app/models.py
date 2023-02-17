from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.html import escape, mark_safe
# Create your models here.

class User(AbstractUser):
    is_user = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

class Challan(models.Model):
    reg_no = models.CharField(max_length=12)
    plate = models.FileField(upload_to='plates/',blank=True)
    date = models.DateTimeField()
    place = models.CharField(max_length=100)
    insurance = models.IntegerField(default=0)
    puc = models.IntegerField(default=0)
    registration = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    txn_id = models.CharField(max_length=100,blank=True)
    txn_date = models.DateTimeField(blank=True,null=True)
    txn_account = models.EmailField(max_length=50,blank=True)

class Transaction(models.Model):
    email = models.CharField(max_length=50)
    reg_no = models.CharField(max_length=15)
    challan = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100,unique=True)
    date = models.DateTimeField()
    resp_msg = models.CharField(max_length=200)
    resp_code = models.CharField(max_length=4)
    bank_name = models.CharField(max_length=20)
    txn_mode = models.CharField(max_length=3)
    txn_amt = models.CharField(max_length=10)
    txn_id = models.CharField(max_length=100)
    txn_status = models.CharField(max_length=20)
    bank_txn_id = models.CharField(max_length=20)

class Subscription(models.Model):
    email = models.CharField(max_length=50)
    reg_no = models.CharField(max_length=15)



