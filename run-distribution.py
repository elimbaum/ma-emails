# run-distribution.py
#
# given a TSV copy and pasted from google sheets, output a CSV file which can be
# entered back into a spreadsheet and used to send emails.

from collections import defaultdict
import random
import math
import sys

# TF expected base pay (net pay - strike pay)
from data.config import TF_BASE

rf_donations = {}
tf_support = {}

emails = {}

if len(sys.argv) != 2:
    print("Please provide an input file")

with open(sys.argv[1]) as f:
    for line in f:
        # expects TSV
        name, email, type, amount = line.split('\t')
        # optionally remove $ sign
        if amount.startswith('$'):
            amount = int(amount[1:])
        else:
            amount = int(amount)

        if type == 'RF':
            if amount == 0:
                continue
            
            rf_donations[name] = amount
        if type == 'TF':
            tf_support[name] = amount
        emails[name] = email

n_rf = len(rf_donations)
n_tf = len(tf_support)

total_donation = sum(rf_donations.values())
total_need = sum(tf_support.values())
print(f"Loaded {n_rf} RFs and {n_tf} TFs.")
print(f"  Total RF donations: ${total_donation}")
print(f"  Avg RF donation: ${round(total_donation/n_rf)}")

needed_donation = round(total_need / n_rf)
tf_avg_each = round(total_need / n_tf)

print(f"Required joint avg donation: ${needed_donation}")

xfer = needed_donation * n_rf

scale = needed_donation/total_donation*n_rf

print(f"  RFs send total of ${needed_donation} each = ${xfer}")
print(f"  TFs recv total of ${xfer}, or ${tf_avg_each} each, avg")
print(f"  TF avg income lost = ${TF_BASE} - ${tf_avg_each} = ${TF_BASE - tf_avg_each}")
print(f"  Scale factor: {scale:.2}")

di = []

for k, v in rf_donations.items():
    old_v = v
    # This needs to be `ceil`, because otherwise we could round down too often 
    # and run out of money.
    di.append((k, min(v, math.ceil(v * scale))))

output = defaultdict(list)

num_transfers = 0

# Randomize distribution so it's fair.
random.shuffle(di)

for t, amt in tf_support.items():
    print(f"**** {t} (${amt}) ****")
    recv = 0

    ## equal distro
    # tf_need = TF_BASE
    ## unique distro
    tf_need = amt

    while recv < tf_need:
        next_donor, amount = di.pop(0) # pop_next_closest(support - recv)

        if recv + amount > tf_need:
            leftover = recv + amount - tf_need
            recv = tf_need
            amount -= leftover
            di.append((next_donor, leftover))
        else:
            recv += amount
        
        print(f"{next_donor}, ${amount}, ${recv}")
        num_transfers += 1

        output[next_donor].append(f"{next_donor}, {emails[next_donor]}, sends, {t}, ${amount}")
    print()

    assert recv == tf_need


print(f"{num_transfers} transfers")

print("-------")
print("from,,,to,amount")

for d, s in output.items():
    for l in s:
        print(l)
    print(f"{d},, listed,, ${rf_donations[d]}")
    print()

