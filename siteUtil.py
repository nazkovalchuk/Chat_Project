import requests
import random
import string
import smtplib
import ssl
from email.message import EmailMessage
import re


def get_gpt3_response(message):
    url = 'http://localhost:8000/v1/chat/completions'  # Replace with your API endpoint

    # Define the JSON data
    data = {
        "messages": [
            {
                "content": "You are a helpful assistant.",
                "role": "system"
            },
            {
                "content": message,
                "role": "user"
            }
        ],
        "max_tokens": 40
    }

    # Send a POST request with the JSON data
    response = requests.post(url, json=data)
    str = response.json()['choices'][0]['message']['content']

    # Use regular expression to find text within curly braces
    result = re.search(r'\{(.*?)}', str, re.DOTALL)

    if result:
        extracted_text = "{" + result.group(1) + "}"
        return extracted_text
    else:
        return str


def generateCodeEmail():
    result = ""
    for i in range(0, 6, 1):
        result += result.join(random.choice(string.digits))
    return result

def validEmail(email):
    result = True
    if not str.__contains__(email, "@") or not str.__contains__(email, ".") :
        result = False

    return result

def strongPass(password):
    result = True

    if not any(chr.isdigit() for chr in password) or not any(chr.islower() for chr in password) or not any(chr.isupper() for chr in password):
        result = False
    if str.__contains__(password, " "):
        result = False
    if not any(not c.isalnum() for c in password):
        result = False

    return result

def sendCodeToEmail(email, code):
    email_sender = 'enormous048@gmail.com'
    email_password = 'sazibxlnpwbqxpxw'
    email_receiver = email

    subject = 'Nolan.ai Verification Code'
    body = 'Hi '+email+',\n\nYour Nolan.ai verification code is: '+code+'\n\nIf you did not request this code, it is possible that someone else is trying to access your Nolan.ai account.\nDo not forward or give this code to anyone.\n\nSincerely yours,\nNolan.ai Team'

    em = EmailMessage()
    em['From'] = 'Nolan AI <'+email_sender+'>'
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

def username_is_in_Database(email):
    return True