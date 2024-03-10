import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BETTER_STACK_KEY = os.environ.get('BETTER_STACK_KEY')
    EMAIL_SYSTEM='smtp'

    # Uncomment the proper configuration
    # Depending on what email system used
    # Mailgun Configuration
    #MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    #MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')

    # SMTP Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_FILE_PATH = os.environ.get('MAIL_FILE_PATH')

    # Resend Configuration
    #RESEND_API_KEY = os.environ.get('RESEND_KEY')
    #RESEND_DOMAIN = os.environ.get('RESEND_DOMAIN')