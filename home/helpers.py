# Import for sending mail
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import threading


class EmailThread(threading.Thread):
    def __init__(self, template_path, email_context):
        self.template_path = template_path
        self.email_context = email_context
        threading.Thread.__init__(self)

    def run(self):
        context = {
            'mentor': self.email_context['mentor'].username,
            'user': self.email_context['user'].username,
            'url': self.email_context['url'],
            'protocol': self.email_context['protocol'],
            'host': self.email_context['host'],
            'issue': self.email_context['issue'],
            'action': self.email_context['action'],
            'receiver': self.email_context['receiver'].username,
        }

        html_message = render_to_string(self.template_path, context=context)
        plain_message = strip_tags(html_message)

        from_email = "noreply@contriHUB-21"
        to = str(self.email_context['receiver'].email)

        try:
            mail.send_mail(self.email_context['subject'], plain_message,
                           from_email, [to], html_message=html_message,
                           fail_silently=False)
        except mail.BadHeaderError:
            return mail.BadHeaderError


class EmailThread_to_admin(threading.Thread):
    def __init__(self, template_path, email_context):
        self.template_path = template_path
        self.email_context = email_context
        threading.Thread.__init__(self)

    def run(self):
        html_message = render_to_string(self.template_path,
                                        context=self.email_context)
        plain_message = strip_tags(html_message)

        from_email = "noreply@contriHUB-21"
        to = "contrihub.avishkar@gmail.com"

        try:
            mail.send_mail(self.email_context['subject'], plain_message,
                           from_email, [to], html_message=html_message,
                           fail_silently=False)
        except mail.BadHeaderError:
            return mail.BadHeaderError
