#!/usr/bin/env python3

import inspect
import sys
from datetime import datetime
import time

from smtplib import SMTP_SSL as SMTP

# TFs should be listed in here. See README for details
from data.tfs import tf_info

connection = None
def smtp_login():
    global connection, from_addr
    SMTP_CONFIG_FILE = "data/smtp.conf"

    configuration = {}
    with open(SMTP_CONFIG_FILE) as cfg:
        for line in cfg:
            line = line.strip()
            if line.startswith("#"):
                continue
            splits = line.split('=')

            if len(splits) < 2:
                continue

            configuration[splits[0]] = splits[1]

    from_addr = configuration['AuthUser']
    password = configuration['AuthPass']

    # Connect to gmail SMTP relay
    connection = SMTP("smtp.gmail.com", 465)
    # connection.set_debuglevel(True)
    connection.login(from_addr, password)

def send_confirmation_email(name, address, amount):
    if connection is None:
        smtp_login()

    message = inspect.cleandoc(
    f"""
    To: {address}
    From: CS Mutual Aid
    Subject: 26 Apr -- Confirming Mutual Aid Contributions
    
    Hi {name},

    We want to confirm your contribution to mutual aid for this week (paycheck April 26th).
    
    We currently have you down as being able to contribute ${amount}. Please let us know by *Thursday at 6pm* if that has changed. If we don't hear back from you, we will assume your ability to contribute this week is the same. If this information is correct, there is no need to respond.

    We'll be in touch in a few days with new distributions for this week.

    We appreciate your contribution to our successful strike!

    Best,

    CS Mutual Aid Team
    """)

    print("\n" * 10)
    print(message)
    input("Send? ")

    message.replace('\n', '\r\n')
    connection.sendmail(from_addr, address, message)

def confirmation_emails(FILE):
    print(f"Sending confirmation emails from file {FILE}")
    with open(FILE) as f:
        num_sent = 0
        for line in f:
            # skip comments
            if line.startswith('#'):
                continue

            name, address, amount = line.split('\t')
            if amount.startswith('$'):
                amount = amount[1:]
            amount = int(amount)

            send_confirmation_email(name.strip(), address.strip(), amount)
            num_sent += 1

    print(f"Done. sent {num_sent} emails!")

def send_distro_email(rf, rf_email, donations):
    if connection is None:
        print("Logging in to gmail.")
        smtp_login()

    donation_str = ""

    for tf, amount in donations:
        _info = tf_info[tf]

        _info_str = '\n'.join(f'      {k}: {v}' for k, v in _info.items())

        donation_str += \
f"""
{amount} to {tf}. Their info is:
{_info_str}
"""

    print('\n' * 10 + "========\n")

    message = inspect.cleandoc(
f"""
To: {rf_email}
From: CS Mutual Aid
Subject: 3 May Mutual Aid Distribution

Hi {rf},

Thank you for contributing to mutual aid! Your money will be supporting the following TF(s) for the April 22-28 week (May 3rd paycheck).
{donation_str}

If you can send the money now, please do so using one of the payment methods listed above. Otherwise, send an email to the TF letting them know you can send your contribution once you get paid for this week.

Let us know if you have any difficulties or delays. We're also happy to answer any other questions you may have.

Note that this is the *final* mutual aid distribution of the spring semester. Over the coming weeks we will discuss the best way to operate over the summer.

Best,
CS Mutual Aid Team

""")
    print(message)

    input()

    message.replace('\n', '\r\n')
    connection.sendmail(from_addr, rf_email, message)

def distribution_emails(FILE):
    num_sent = 0
    print(f"Sending confirmation emails from file {FILE}")
    input()
    with open(FILE) as f:
        rf = tf = email = None
        donations = []
        for line in f:
            line = line.strip()

            # next tf
            if not line:
                rf = None
                donations = []
                continue

            rf_, email_, verb, tf, amount = line.split('\t')

            if rf is not None:
                assert rf == rf_
            else:
                rf = rf_
                email = email_

            if verb == 'listed':
                send_distro_email(rf, email, donations)
                num_sent += 1
            else:
                donations.append((tf, amount))

    print(f"Sent {num_sent} emails!")

func = distribution_emails
# func = confirmation_emails

if len(sys.argv) != 2:
    print("please provide an input file")


f = sys.argv[1]

input(f"Press enter to start: {func.__name__} with input {f} > ")


start = time.time()
func(f)
print(f"{time.time() - start:.1f} sec")