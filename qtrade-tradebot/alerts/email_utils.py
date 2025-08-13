import smtplib
import ssl


context = ssl.create_default_context()

with smtplib.SMTP_SSL("test@gmail.com", context = context, port=465) as server:
    server.login
