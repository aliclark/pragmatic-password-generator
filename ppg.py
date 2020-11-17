#!/usr/bin/env python

import secrets
import string
import argparse


def cloudHashesPerDollar(algorithm):
    return max([card['hps'][algorithm] / card['cost'] for card in cards.values()])


def wattHashesPerDollar(algorithm):
    # https://www.globalpetrolprices.com/electricity_prices/
    # March 2020
    # The cheapest countries for electricity are around $0.05 / kwh
    # Converted to $/watt
    wattCost = 0.05 / (1000 * 60 * 60)
    hashesPerWatt = max([card['hps'][algorithm] / card['watt'] for card in cards.values()])
    return hashesPerWatt / wattCost


factors = {
    'cloud': cloudHashesPerDollar,
    'watts': wattHashesPerDollar
}


parser = argparse.ArgumentParser(description='Generate a password.')
parser.add_argument('--budget', type=int, default=10*1000, metavar='dollars',
                    help='the full budget for an attack')
parser.add_argument('--acceptance', type=float, default=0.01, metavar='probability',
                    help='acceptable probability of an attack being successful using the full budget')
parser.add_argument('--factor', choices=factors.keys(), default='cloud',
                    help='the constraining resource factor for the attack')
# Generally MD5 is good as a minimum computation benchmark.
# It may be tempting to factor down for bcrypt/scrypt et al. for lower performance on GPU,
# but taking into account FPGA the performance difference is greatly reduced:
# https://scatteredsecrets.medium.com/bcrypt-password-cracking-extremely-slow-not-if-you-are-using-hundreds-of-fpgas-7ae42e3272f6
parser.add_argument('--algorithm', choices=['MD5'], default='MD5',
                    help='the assumed algorithm under attack')
parser.add_argument('--lifetime', type=int, default=2, metavar='years',
                    help='lifespan of the secret')
onlineRateDefault = 10
parser.add_argument('--online', type=int, nargs='?', const=onlineRateDefault, metavar='rate-per-second',
                    help='assume only online bruteforcing at rate/s')
# https://security.stackexchange.com/questions/181708/how-facebook-hashes-passwords
parser.add_argument('--service', choices=['facebook'],
                    help='services which use HSM to prevent offline cracking')


args = parser.parse_args()


if args.service:
    args.online = onlineRateDefault


# Prices as of 2020-11-16
# https://cloud.google.com/compute/gpus-pricing
# todo: check if AWS come out with something cheaper
# https://aws.amazon.com/ec2/spot/pricing/
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


# https://arxiv.org/pdf/1911.11313.pdf
# energy efficiency (FLOPS per Watt) of GPUs doubles approximately every three to four years
efficiency = 2 ** (args.lifetime / 3.5)

# https://www.irena.org/newsroom/articles/2020/Jun/How-Falling-Costs-Make-Renewables-a-Cost-effective-Investment
scale = 0.81 ** args.lifetime


if args.online:
    combinations = (args.online * args.lifetime * 365 * 24 * 60 * 60) / args.acceptance
else:
    combinations = ((args.budget / args.acceptance) * factors[args.factor](args.algorithm) * efficiency) / scale


password = ''
uniqueness = 1

password += secrets.choice(string.ascii_uppercase)
uniqueness *= len(string.ascii_uppercase)

password += secrets.choice(string.digits)
uniqueness *= len(string.digits)

password += secrets.choice(string.punctuation)
uniqueness *= len(string.punctuation)

while uniqueness < combinations or len(password) < 8:
    password = password[:1] + secrets.choice(string.ascii_lowercase) + password[1:]
    uniqueness *= len(string.ascii_lowercase)


print(password)

