from django.shortcuts import render,redirect
from .forms import Login,Register,FindChallan,FindTransaction,Subscribe
from django.contrib.auth import authenticate,login,logout as logOut
from django.views.decorators.csrf import csrf_exempt
from .models import Challan,Transaction,Subscription
import paytmchecksum
import uuid
from datetime import datetime
from django.http import HttpResponse
from .utils import send_challan_mail
from verify_email.email_handler import send_verification_email
from django.contrib import messages

PAYTM_MID = '[REMOVED]'
PAYTM_KEY = '[REMOVED]'
WEBSITE = 'DEFAULT'
PAYTM_URL = 'https://securegw-stage.paytm.in/order/process'
#CALLBACK_URL = 'http://127.0.0.1:8000/paymemtstatus'
CALLBACK_URL = 'https://shubham-anpr.herokuapp.com/paymemtstatus'



# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'GET':
        form = Login(None)
        return render(request, 'index.html', {'form' : form})

    if request.method == 'POST':
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                print(user.email)
                login(request, user)
                return redirect('dashboard')
            else:
                form.errors.password = 'Invalid username or password'
                return render(request, 'index.html', {'form' : form})
        return render(request, 'index.html', {'form' : form})

def register(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'GET':
        form = Register(None)
        context['form'] = form
        return render(request, 'register.html', context)

    if request.method == 'POST':
        form = Register(request.POST)
        context['form'] = form
        if form.is_valid():
            inactive_user = send_verification_email(request, form)
            sent = inactive_user.email
            message = f'Email verification link has been sent to {sent}. Verify your account to login'
            messages.add_message(request, messages.INFO, message,extra_tags='alert alert-info text-center')
            return redirect('/')
        return render(request, 'register.html', context)


def logout(request):
    logOut(request)
    return redirect('/')

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html', {'user' : request.user})
    return redirect('/')    

def viewchallan(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == 'GET':
            form = FindChallan(None)
            context['form'] = form
            return render(request, 'viewchallan.html',context)
        if request.method == 'POST':
            form = FindChallan(request.POST)
            if form.is_valid():
                if request.POST['filter'] == 'all':
                    challan = Challan.objects.filter(reg_no=request.POST['reg_no']).order_by('-date')
                elif request.POST['filter'] == 'paid':
                    challan = Challan.objects.filter(reg_no=request.POST['reg_no'],is_paid=True).order_by('-date')
                elif request.POST['filter'] == 'closed':
                    challan = Challan.objects.filter(reg_no=request.POST['reg_no'],is_closed=True).order_by('-date')
                else:
                    challan = Challan.objects.filter(reg_no=request.POST['reg_no'],is_paid=False).order_by('-date')
                context['challan'] = challan
            context['form'] = form
            return render(request, 'viewchallan.html', context)
    return redirect('/')

def challandetails(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                challan_id = request.GET['challan_id']
                reg_no = request.GET['no']
            except:
                return redirect('error')
            try:
                challan = Challan.objects.get(id=challan_id,reg_no=reg_no)
                context['challan'] = challan
            except:
                return redirect('error')
            return render(request, 'challandetails.html', context)
    return redirect('error')

def makepayment(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                challan_id = request.GET['challan_id']
                reg_no = request.GET['no']
            except:
                return redirect('error')
            try:
                challan = Challan.objects.get(id=challan_id,reg_no=reg_no)
                if challan.is_paid or challan.is_closed:
                    return redirect('error')
                order_id = str('ANPR' + str(uuid.uuid1()))
                challan.txn_id = order_id
                challan.txn_date = datetime.now()
                challan.txn_account = request.user.email
                challan.save()

                param_dict={
                    'MID': PAYTM_MID,
                    'ORDER_ID': order_id,
                    'TXN_AMOUNT': str(challan.insurance+challan.puc+challan.registration),
                    'CUST_ID': request.user.email,
                    'INDUSTRY_TYPE_ID': 'Retail',
                    'WEBSITE': WEBSITE,
                    'CHANNEL_ID': 'WEB',
                    'CALLBACK_URL': CALLBACK_URL,
                }
                param_dict['CHECKSUMHASH'] = paytmchecksum.generateSignature(param_dict,PAYTM_KEY)
                context['param_dict'] = param_dict
                context['paytm_url'] = PAYTM_URL
            except:
                return redirect('error')
            return render(request, 'makepayment.html', context)
    return redirect('error')

def error(request):
    return render(request, 'error.html')

@csrf_exempt
def paymemtstatus(request):
    if request.method == 'POST':
        context = {}
        response_dict = {}
        for i in request.POST:
            response_dict[i] = request.POST[i]
        context['response_dict'] = response_dict
        result = paytmchecksum.verifySignature(response_dict, PAYTM_KEY, response_dict['CHECKSUMHASH'])
        if result:
            transaction = Transaction()
            challan = Challan.objects.get(txn_id=response_dict['ORDERID'])
            transaction.email = challan.txn_account
            transaction.reg_no = challan.reg_no
            transaction.challan = challan.id
            transaction.order_id = response_dict['ORDERID']
            try:
                transaction.date = response_dict['TXNDATE']
                transaction.bank_name = response_dict['BANKNAME']
                transaction.txn_mode = response_dict['PAYMENTMODE']
            except:
                transaction.date = datetime.now()
                transaction.bank_name = ''
                transaction.txn_mode = ''
            transaction.resp_msg = response_dict['RESPMSG']
            transaction.resp_code = response_dict['RESPCODE']
            transaction.txn_amt = response_dict['TXNAMOUNT']
            transaction.txn_id = response_dict['TXNID']
            transaction.txn_status = response_dict['STATUS']
            transaction.bank_txn_id = response_dict['BANKTXNID']
            try:
                transaction.save()
            except:
                return redirect('error')
            if response_dict['RESPCODE'] == '01':
                challan.is_paid = True
                challan.save()
            return render(request, 'paymemtstatus.html', context)
        return redirect('error')

def paymenthistory(request):
    context = {}
    if request.user.is_authenticated:
        form = FindTransaction(request.POST or None)
        if request.method == 'POST' and request.POST['filter'] == 'failed':
            transaction = Transaction.objects.filter(email=request.user.email).exclude(resp_code = '01').order_by('-date')
        elif request.method == 'POST' and request.POST['filter'] == 'success':
            transaction = Transaction.objects.filter(email=request.user.email,resp_code = '01').order_by('-date')
        else:
            transaction = Transaction.objects.filter(email=request.user.email).order_by('-date')
        context['form'] = form
        context['transaction'] = transaction
        return render(request, 'paymenthistory.html', context)
    return redirect('/')

def paymentdetails(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                txn_id = request.GET['txn_id']
            except:
                return redirect('error')
            try:
                transaction = Transaction.objects.get(order_id=txn_id,email=request.user.email)
                context['transaction'] = transaction
            except:
                return redirect('error')
            return render(request, 'paymentdetails.html', context)
    return redirect('error')

@csrf_exempt
def createchallan(request):
    if request.method == 'POST':
        try:
            challan = Challan()
            challan.reg_no = request.POST['reg_no']
            challan.plate = request.FILES['file']
            challan.date = request.POST['date']
            challan.place = request.POST['place']
            challan.insurance = request.POST['insurance']
            challan.puc = request.POST['puc']
            challan.registration = request.POST['registration']
            challan.save()
            subscriber = Subscription.objects.filter(reg_no=request.POST['reg_no'])
            subscribers = []
            if subscriber:
                subscribers = [s.email for s in subscriber]
            send_challan_mail(request.POST,subscribers)
            return HttpResponse('success',status=200)
        except Exception as e:
            print(e)
            return HttpResponse('Access Denied',status=403)
    return HttpResponse('Access Denied',status=403)  

def subscribe(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == 'GET':
            form = Subscribe()
            subscriptions = Subscription.objects.filter(email=request.user.email)
            context['subscriptions'] = subscriptions
            context['form'] = form
            return render(request, 'subscribe.html', context)
        if request.method == 'POST':
            form = Subscribe(request.POST)
            if form.is_valid():
                reg_no = form.cleaned_data.get('reg_no')
                currentsub = Subscription.objects.filter(email=request.user.email,reg_no=reg_no)
                if currentsub:
                    form.add_error('reg_no',f'{reg_no} is already subscribed')
                    subscriptions = Subscription.objects.filter(email=request.user.email)
                    context['subscriptions'] = subscriptions
                    context['form'] = form
                    return render(request, 'subscribe.html', context)
                currentsub = Subscription()
                currentsub.email = request.user.email
                currentsub.reg_no = reg_no
                currentsub.save()
            subscriptions = Subscription.objects.filter(email=request.user.email)
            context['subscriptions'] = subscriptions
            context['form'] = form
            return render(request, 'subscribe.html', context)

def unsubscribe(request):
    if request.method == 'POST':
        try:
            reg_no = request.POST['reg_no']
            currentsub = Subscription.objects.filter(email=request.user.email,reg_no=reg_no)
            if currentsub:
                currentsub.delete()
                return redirect('subscribe')
            return redirect('error')
        except:
            return redirect('error')
    return redirect('error')


