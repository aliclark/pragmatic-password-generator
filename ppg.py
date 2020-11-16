#!/usr/bin/env python

import secrets
import string

from cards import cards


# Conservative choice, assume the site saved passwords as plain MD5
hash = 'MD5'

# Assume the operation is running on the commercial cloud
infrastructure = 'cloud'

# Protect against an attack using a $10k budget
budget = 10 * 1000

# Maximum acceptable probability of compromise
probability = 1/100


def cloudHashesPerDollar(hash):
    return max([card['hps'][hash] / card['cost'] for card in cards.values()])


def wattHashesPerDollar(hash):
    # https://www.globalpetrolprices.com/electricity_prices/
    # March 2020
    # The cheapest countries for electricity are around $0.05 / kwh
    # Converted to $/watt
    wattCost = 0.05 / (1000 * 60 * 60)
    hashesPerWatt = max([card['hps'][hash] / card['watt'] for card in cards.values()])
    return hashesPerWatt / wattCost


infrastructures = {
    'cloud': cloudHashesPerDollar,
    'hosted': wattHashesPerDollar
}


combinations = (budget / probability) * infrastructures[infrastructure](hash)


password = ''
uniqueness = 1

password += secrets.choice(string.ascii_uppercase)
uniqueness *= len(string.ascii_uppercase)

password += secrets.choice(string.digits)
uniqueness *= len(string.digits)

password += secrets.choice(string.punctuation)
uniqueness *= len(string.punctuation)

while uniqueness < combinations:
    password = password[:1] + secrets.choice(string.ascii_lowercase) + password[1:]
    uniqueness *= len(string.ascii_lowercase)


print(password)

