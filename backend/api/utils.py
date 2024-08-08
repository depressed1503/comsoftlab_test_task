def email_adress_to_imap_server(email_address):
    e_to_imap = {
        "yandex.ru": "imap.yandex.ru",
        "gmail.com": "imap.gmail.com",
        "mail.ru": "imap.mail.ru",
    }
    return e_to_imap[email_address.split("@")[-1]]
