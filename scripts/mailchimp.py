#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
import sqlite3


def transfer(api_key, db_voyage):
    transfered_mails = get_mailchimp_mails(api_key)
    ghost_mails = get_ghost_mails(db_voyage)
    mails_to_tranfer = ghost_mails - transfered_mails
    add_mails_to_mailchimp(api_key, mails_to_tranfer)


def get_mailchimp_mails(api_key):
    print("[1/3] Get mails from mailchimp")
    mails = requests.get("https://us14.api.mailchimp.com/3.0/lists/3d9abf3837/members",
                        auth=("pouet", api_key)).json()
    return set([member["email_address"] for member in mails["members"]])


def get_ghost_mails(db_voyage):
    print("[2/3] Get mails from blog subscribers")
    ghost = sqlite3.connect(db_voyage)
    ghost_cur = ghost.cursor()
    ghost_cur.execute("SELECT email FROM subscribers")
    return set([str(mail[0]) for mail in ghost_cur.fetchall()])


def add_mails_to_mailchimp(api_key, mails):
    print("[3/3] Transfer to mailchimp")
    print("%s mails to transfer" % len(mails))
    for mail in mails:
        r = requests.post("https://us14.api.mailchimp.com/3.0/lists/3d9abf3837/members",
                          auth=("pouet", api_key),
                          data=json.dumps({"email_address": mail,
                                           "status": "subscribed"}))
        print("Subscribed %s; code: %s" % (mail, r.status_code))
