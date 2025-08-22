# qtrade-tradebot


#### next steps:
- [x] create a class to manage QuestTrade API requests
- [x] other class to manage stocks and database
- [ ] WIP: provide a user interface to be able to add tracked stocks, show stock charts, and set configurations such as emails to alert when stoploss is reached
- [ ] WIP: add other notification/alert types such as telegram/sms
- ~~modify TokenManager to be more general: currently implements QuestTrade API logic~~



#### resources:
- https://docs.python.org/3/library/smtplib.html
- https://docs.python.org/3/library/email.examples.html
- https://docs.sqlalchemy.org


#### limitations:
- sqlite database allows only for one concurrent writer which may conflict if multiple threads are active
- email_utils module currently uses gmail API which requires user to possess log-in credentials on google workspace for bot to function
    - will move google api logic to seperate email whilst adding simpler smtplib logic for broader use
- refresh token must be seeded manually through an environment variable: if it expires the user must manually retrieve another from their account
