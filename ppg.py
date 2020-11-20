#!/usr/bin/env python

from argparse import ArgumentParser
from math import log, ceil
import secrets
from string import ascii_uppercase, ascii_lowercase, digits, punctuation


def cloudHashesPerDollar(algorithm):
    hpd = max([card['hps'][algorithm] / card['cost'] for card in cards.values()])
    #print([(name, card['hps'][algorithm] / card['cost']) for name, card in cards.items()])
    #print(hpd)
    return hpd

def wattHashesPerDollar(algorithm):
    # https://www.globalpetrolprices.com/electricity_prices/
    # March 2020
    # The cheapest countries for electricity are around $0.05 / kwh
    # Converted to $/watt
    wattCost = 0.05 / (1000 * 60 * 60)
    hashesPerWatt = max([card['hps'][algorithm] / card['watt'] for card in cards.values()])
    #print([(name, card['hps'][algorithm] / card['watt']) for name, card in cards.items()])
    #print(hashesPerWatt)
    return hashesPerWatt / wattCost


factors = {
    'cloud': cloudHashesPerDollar,
    'watts': wattHashesPerDollar
}


parser = ArgumentParser(description='Generate a password.')
parser.add_argument('--budget', type=int, default=10*1000, metavar='dollars',
                    help='budget for an attack (if attackers could collaborate, then their combined resources)')
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
parser.add_argument('--lifetime', type=int, default=20, metavar='years',
                    help='lifespan of the secret')
parser.add_argument('--service', choices=['fido', 'hello', 'facebook'],
                    help='services which use an HSM or TPM to prevent offline cracking')
parser.add_argument('--minimum-length', type=int, default=0, metavar='characters',
                    help='generate more characters if below the minimum length specified')
parser.add_argument('--format', choices=['add-complexity', 'lowercase', 'digits'],
                    help='output options, the default is to vary character types to meet complexity requirements')
parser.add_argument('--show-entropy', action='store_true',
                    help='display the entropy needed (in bits) without generating a password')


args = parser.parse_args()

rate = 0


if args.service == 'fido':
    # https://fidoalliance.org/how-fido-works/
    # https://fidoalliance.org/specs/fido2/fido-client-to-authenticator-protocol-v2.1-rd-20191217.html#pinretries
    # Assume an attacker can attempt 6 tries and wait 1 hour for the user to unlock the key again
    rate = 6 / (60 * 60)
    defaultFormat = 'lowercase'
elif args.service == 'hello':
    # https://docs.microsoft.com/en-us/windows/security/information-protection/tpm/manage-tpm-lockout
    # Assume an attacker can attempt 32 tries and reboot in the space of 60 seconds
    rate = 32 / 60
    defaultFormat = 'lowercase'
elif args.service == 'facebook':
    # https://security.stackexchange.com/questions/181708/how-facebook-hashes-passwords
    # Unclear what the rate is, but Facebook implements brute-force lockout for up to 24h:
    # https://security.stackexchange.com/questions/84032/how-can-facebook-possibly-stop-a-bruteforce-attack-on-an-account
    rate = 1
    defaultFormat = 'lowercase'
else:
    defaultFormat = 'add-complexity'


if not args.format:
    args.format = defaultFormat


if rate and not args.lifetime:
    exit('Please set lifetime when specifying a service')


# Prices as of 2020-11-18
# https://cloud.google.com/compute/gpus-pricing
# https://aws.amazon.com/ec2/spot/pricing/
cards = {
    # https://hashcat.net/forum/archive/index.php?thread-7990.html
    'gcloud/T4':   { 'hps': { 'MD5':      (21393.2 * 1000 * 1000) / 1 }, 'cost': 0.11  / (60 * 60), 'watt':  75 },
    # No source found for Tesla P4 benchmarks
    #'gcloud.P4':   { 'hps': { 'MD5':          (??? * 1000 * 1000) / 1 }, 'cost': 0.216 / (60 * 60), 'watt':  75 },
    # https://gist.github.com/Chick3nman/4d3c5fd44f33610ddbbf026d46d9e0aa
    # https://github.com/siseci/hashcat-benchmark-comparison/blob/master/8x%20Tesla%20V100%20p3.16xlarge%20Hashcat%20Benchmark
    'gcloud/V100': { 'hps': { 'MD5': (450 * 1000   * 1000 * 1000) / 8 }, 'cost': 0.74  / (60 * 60), 'watt': 250 },
    # https://github.com/someshkar/colabcat/blob/master/benchmarks/Tesla-P100.txt
    'gcloud/P100': { 'hps': { 'MD5':      (26993.7 * 1000 * 1000) / 1 }, 'cost': 0.43  / (60 * 60), 'watt': 300 },
    # https://gist.github.com/koenrh/3a960ab619cb9f5e21b7174793a956ff
    'gcloud/K80':  { 'hps': { 'MD5':      (16908.6 * 1000 * 1000) / 4 }, 'cost': 0.135 / (60 * 60), 'watt': 300 },
    # https://github.com/javydekoning/aws-hashcat
    'g3s.xlarge/M60':       { 'hps': { 'MD5':        11732.8 * 1000 * 1000 }, 'cost': 0.225  / (60 * 60), 'watt': 300 },
    'g4dn.xlarge/T4':       { 'hps': { 'MD5':        20625.3 * 1000 * 1000 }, 'cost': 0.1578 / (60 * 60), 'watt':  75 },
    'g4dn.12xlarge/4xT4':   { 'hps': { 'MD5':        83207.3 * 1000 * 1000 }, 'cost': 1.1736 / (60 * 60), 'watt':  75 * 4 },
    'p3.2xlarge/V100':      { 'hps': { 'MD5':        55715.1 * 1000 * 1000 }, 'cost': 0.918  / (60 * 60), 'watt': 250 },
    'p3.16xlarge/8xV100':   { 'hps': { 'MD5': 451.8 * 1000   * 1000 * 1000 }, 'cost': 7.344  / (60 * 60), 'watt': 250 * 8 },
    'p3dn.24xlarge/8xV100': { 'hps': { 'MD5': 443.4 * 1000   * 1000 * 1000 }, 'cost': 9.3636 / (60 * 60), 'watt': 250 * 8 },
    'p4d.24xlarge/8xA100':  { 'hps': { 'MD5': 523.5 * 1000   * 1000 * 1000 }, 'cost': 9.8318 / (60 * 60), 'watt': 400 * 8 }
}


# https://arxiv.org/pdf/1911.11313.pdf
# energy efficiency (FLOPS per Watt) of GPUs doubles approximately every three to four years
efficiency = 2 ** (args.lifetime / 3.5)

# https://www.irena.org/newsroom/articles/2020/Jun/How-Falling-Costs-Make-Renewables-a-Cost-effective-Investment
scale = 0.81 ** args.lifetime


if rate:
    combinations = (rate * args.lifetime * 365 * 24 * 60 * 60) / args.acceptance
else:
    combinations = ((args.budget / args.acceptance) * factors[args.factor](args.algorithm) * efficiency) / scale


if args.show_entropy:

    if args.format == 'add-complexity':
        minimumLengthCombinations = len(ascii_uppercase) * (len(ascii_lowercase) ** (args.minimum_length - 3)) * len(digits) * len(punctuation)
    elif args.format == 'lowercase':
        minimumLengthCombinations = len(ascii_lowercase) ** args.minimum_length
    elif args.format == 'digits':
        minimumLengthCombinations = len(digits) ** args.minimum_length

    print(ceil(log(max(combinations, minimumLengthCombinations), 2)))
    exit()


password = ''
uniqueness = 1

if args.format == 'add-complexity':
    password += secrets.choice(ascii_uppercase)
    uniqueness *= len(ascii_uppercase)

    password += secrets.choice(digits)
    uniqueness *= len(digits)

    password += secrets.choice(punctuation)
    uniqueness *= len(punctuation)

    while uniqueness < combinations or len(password) < args.minimum_length:
        password = password[:1] + secrets.choice(ascii_lowercase) + password[1:]
        uniqueness *= len(ascii_lowercase)

elif args.format == 'lowercase':
    while uniqueness < combinations or len(password) < args.minimum_length:
        password = password[:1] + secrets.choice(ascii_lowercase) + password[1:]
        uniqueness *= len(ascii_lowercase)

elif args.format == 'digits':
    while uniqueness < combinations or len(password) < args.minimum_length:
        password = password[:1] + secrets.choice(digits) + password[1:]
        uniqueness *= len(digits)


print(password)

