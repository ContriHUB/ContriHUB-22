# Import for sending mail
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import threading
# email_context = {
#     'mentor': issue.mentor,
#     'user': requester,
#     'issue_html_url': issue.html_url,
#     'protocol': request.get_raw_uri().split('://')[0],
#     'host': request.get_host(),
#     'subject': "Request for Issue Assignment under ContriHUB-21.",
# }


class EmailThread(threading.Thread):
    def __init__(self, template_path, email_context):
        self.template_path=template_path
        self.email_context=email_context
        threading.Thread.__init__(self)
        
    def run(self):
        # print(email_context)
        context = {
            'mentor': self.email_context['mentor'].username,
            'user': self.email_context['user'].username,
            'url': self.email_context['url'],
            'protocol': self.email_context['protocol'],
            'host': self.email_context['host']
        }

        html_message = render_to_string(self.template_path, context=context)
        plain_message = strip_tags(html_message)

        from_email = "noreply@contriHUB-21"
        to = str(self.email_context['mentor'].email)

        html_message = render_to_string(self.template_path, context=context)
        plain_message = strip_tags(html_message)

        from_email = "noreply@contriHUB-21"
        to = str(self.email_context['mentor'].email)

        try:
            mail.send_mail(self.email_context['subject'], plain_message, from_email, [to], html_message=html_message,
                           fail_silently=False)
        except mail.BadHeaderError:
            return mail.BadHeaderError
