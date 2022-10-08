# Import for sending mail
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# email_context = {
#     'mentor': issue.mentor,
#     'user': requester,
#     'issue_html_url': issue.html_url,
#     'protocol': request.get_raw_uri().split('://')[0],
#     'host': request.get_host(),
#     'subject': "Request for Issue Assignment under ContriHUB-21.",
# }


def send_email(template_path, email_context):
    # print(email_context)
    context = {
        'mentor': email_context['mentor'].username,
        'user': email_context['user'].username,
        'url': email_context['url'],
        'protocol': email_context['protocol'],
        'host': email_context['host']
    }

    html_message = render_to_string(template_path, context=context)
    plain_message = strip_tags(html_message)

    from_email = "noreply@contriHUB-21"
    to = str(email_context['mentor'].email)

    try:
        mail.send_mail(email_context['subject'], plain_message, from_email, [to], html_message=html_message,
                       fail_silently=False)
    except mail.BadHeaderError:
        return mail.BadHeaderError


def send_email_to_admin(template_path, email_context):
    html_message = render_to_string(template_path, context=email_context)
    plain_message = strip_tags(html_message)

    from_email = "noreply@contriHUB-21"
    to = "contrihub.avishkar@gmail.com"

    try:
        mail.send_mail(email_context['subject'], plain_message, from_email, [to], html_message=html_message,
                       fail_silently=False)
    except mail.BadHeaderError:
        return mail.BadHeaderError
