import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_tls_email(smtp_host, smtp_port, smtp_user, smtp_password, sender_email, receiver_email, subject):
    retorno = ""

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(subject, 'plain'))

    # Configura a conexão SMTP
    try:
        with smtplib.SMTP(smtp_host, 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            retorno = server.sendmail(sender_email, receiver_email, msg.as_string())
    except smtplib.SMTPException as e:
        retorno = e

    return retorno

def send_ssl_email(smtp_host, smtp_port, smtp_user, smtp_password, sender_email, receiver_email, subject, body):
    retorno = ""

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))


    # Configura a conexão SMTP
    try:
        with smtplib.SMTP_SSL(smtp_host, 465) as server:
            server.login(smtp_user, smtp_password)
            retorno = server.sendmail(sender_email, receiver_email, msg.as_string())
    except smtplib.SMTPException as e:
        retorno = e

    return retorno