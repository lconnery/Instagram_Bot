import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

emails = ["lconnery@purdue.edu", "milogreenmilo@gmail.com"]


def notify_email(email_message):

    email_file = open('./emailServices/email_template.html', 'r')
    html_content = email_file.read()

    html_content_final = html_content.replace("{{/message}}", email_message)

    for email in emails:

        message = Mail(from_email='lconnery61@gmail.com',
                       to_emails=email,
                       subject='Instagram Bot Message: Silvia Brown',
                       html_content=html_content_final)

        try:
            api_key = os.getenv('SENDGRID_API_KEY', "none")
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
        except Exception as e:
            print(e)