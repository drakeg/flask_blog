from flask import current_app
from flask_mailman import EmailMessage

def send_email(recipient, subject, body):
    active_system = current_app.config['EMAIL_SYSTEM']
    print(f"The active_system is: {active_system}")
    if active_system == 'smtp':
        msg = EmailMessage(subject=subject,
                           to=[recipient],
                           body=body
        )
        msg.send(fail_silently=False)
    elif active_system == 'mailgun':
        # Example: Send email using Mailgun API
        import requests
        return requests.post(
            f"https://api.mailgun.net/v3/{current_app.config['EMAIL_SYSTEMS'][active_system]['DOMAIN']}/messages",
            auth=("api", current_app.config['EMAIL_SYSTEMS'][active_system]['API_KEY']),
            data={"from": f"noreply@{current_app.config['EMAIL_SYSTEMS'][active_system]['DOMAIN']}",
                  "to": [recipient],
                  "subject": subject,
                  "text": body})
    elif active_system =='resend':
        # Use Resend's API to send the email
        import requests
        response = requests.post(
            f"https://api.resend.io/v1/accounts/{email_config['resend']['DOMAIN']}/messages",
            auth=("api", email_config['resend']['API_KEY']),
            data={"from": f"noreply@{email_config['resend']['DOMAIN']}",
                "to": [recipient],
                "subject": subject,
                "text": body})
        if response.status_code != 200:
            raise Exception("Failed to send email via Resend")
    else:
        # Handle other email systems or throw an error
        raise NotImplementedError(f"Email system {active_system} is not implemented")
