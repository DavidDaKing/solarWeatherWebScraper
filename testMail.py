import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='dabower42069@gmail.com',
    to_emails='EMAIL-HERE',
    subject='TEST EMAIL',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    # sg.set_sendgrid_data_residency("eu")
    # uncomment the above line if you are sending mail using a regional EU subuser
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)