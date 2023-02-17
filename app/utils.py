from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime
from django.template.loader import render_to_string


def send_challan_mail(data,emails):
    subject = f'Challan generated against {data["reg_no"]}'
    message = f'''Dear {data['name']},

A challan for Rs. {int(data['registration'])+int(data['insurance'])+int(data['puc'])} has been generated against {data["reg_no"]} on {datetime.strptime(data['date'],'%Y-%m-%d %H:%M:%S.%f').strftime('%d-%B-%Y %I:%M %p (%A)')}.
Your vehicle was spotted at {data['place']} violating the traffic norms defined by Government of India.
For more details kindly login to https://shubham-anpr.herokuapp.com and pay challan online within 3 month to avoid any legal action against you.

Regards:
Traffic E-Challan System'''
    context = {}
    context['data'] = data
    context['date'] = datetime.strptime(data['date'],'%Y-%m-%d %H:%M:%S.%f').strftime('%d-%B-%Y %I:%M %p (%A)')
    html_msg = render_to_string('email_alert.html',context)
    email_from = 'Traffic E-Challan System <' + settings.EMAIL_HOST_USER + '>'
    recipient_list = [data['email']] + emails
    send_mail( subject, message, email_from, recipient_list,html_message=html_msg)