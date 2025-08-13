
Email:

- STMP connection needs to be encrypted to protect credentials
- SSL (secure sockets layer) and TLS (transport layer security) are two protocols that can be used to encrypt an SMTP connection

#### smtplib
---
built-in library for python to send emails to any machine with SMTP/ESMTP listener


**key parts of SMTP**
- SMTP.starttls() or smtplib.SMTP_SSL for security
	- SMTP_SSL behaves the same as SMTP with same methods
	- just initialized with SSL context
- SMTP.connect(): run automatically when initialized
- SMTP.helo()/ehlo() are to identify yourself to server; run automatically with sendmail()
- SMTP.verity(address): verifies address/many sites disabled
- SMTP.login() will helo/ehlo
	- log in to SMTP servers that require authentification
	- runs SMTP.auth implicitly
- SMTP.sendmail(): sends mail with RFC 822 standards
	- send_message() sends a msg from email package
- SMTP.quit() exists SMTP session
	- run automatically with context manager
