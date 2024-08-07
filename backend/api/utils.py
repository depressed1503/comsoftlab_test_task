import imaplib
import email
from email.header import decode_header
import base64
from bs4 import BeautifulSoup
import re
from .models import CustomUser


def email_adress_to_imap_server(email_address):
    e_to_imap = {
        "yandex.ru": "imap.yandex.ru",
        "gmail.com": "imap.gmail.com",
        "mail.ru": "imap.mail.ru",
    }
    return e_to_imap[email_address.split("@")[-1]]


def find_last_letter(user: CustomUser):
    user_messsages = user.email_letters
    email_password = user.email_password
    username = user.email
    imap_server = email_adress_to_imap_server(username)
    try:
        imap = imaplib.IMAP4_SSL(imap_server)
        print(imap, email_adress_to_imap_server(username), username, email_password)
        login_resp = imap.login(username, email_password)
        print("Login response:", login_resp)
    except imaplib.IMAP4.error as error:
        print('Authentication failed', str(error))
