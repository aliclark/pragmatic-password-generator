#!/usr/bin/env python

import secrets
import string


# Conservative choice, assume the site saved passwords as plain MD5
hash = 'MD5'

# Assume the operation is running on the commercial cloud
infrastructure = 'cloud'

# Protect against an attack using a $10k budget
budget = 10 * 1000

# Maximum acceptable probability of compromise
probability = 1/100


# Prices as of 2020-11-16
# https://cloud.google.com/compute/gpus-pricing
cards = {
    # https://gist.github.com/Chick3nman/4d3c5fd44f33610ddbbf026d46d9e0aa
    # https://github.com/siseci/hashcat-benchmark-comparison/blob/master/8x%20Tesla%20V100%20p3.16xlarge%20Hashcat%20Benchmark
    'V100': { 'watt': 250, 'cost': 0.74  / (60 * 60), 'hps': { 'MD5': (450 * 1000 * 1000 * 1000) / 8 } },
    # https://hashcat.net/forum/archive/index.php?thread-7990.html
    'T4':   { 'watt': 75,  'cost': 0.11  / (60 * 60), 'hps': { 'MD5': (21393.2 * 1000 * 1000) / 1 } },
    # https://gist.github.com/koenrh/3a960ab619cb9f5e21b7174793a956ff
    'K80':  { 'watt': 300, 'cost': 0.135 / (60 * 60), 'hps': { 'MD5': (16908.6 * 1000 * 1000) / 4 } },
    # https://github.com/someshkar/colabcat/blob/master/benchmarks/Tesla-P100.txt
    'P100': { 'watt': 300, 'cost': 0.43  / (60 * 60), 'hps': { 'MD5': (26993.7 * 1000 * 1000) / 1 } }
    # No source found for Tesla P4 benchmarks
}


# todo: check if AWS come out with something cheaper
# https://aws.amazon.com/ec2/spot/pricing/
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

