#!/usr/bin/env python

from argparse import ArgumentParser
from math import log, ceil
import secrets
from string import ascii_uppercase, ascii_lowercase, digits, punctuation


def cloudHashesPerDollar():
    hpd = max([card['hps']['MD5'] / card['cost'] for card in cards.values()])
    #print([(name, card['hps']['MD5'] / card['cost']) for name, card in cards.items()])
    #print(hpd)
    return hpd

def wattHashesPerDollar():
    # https://www.globalpetrolprices.com/electricity_prices/
    # March 2020
    # The cheapest countries for electricity are around $0.05 / kwh
    # Converted to $/watt
    wattCost = 0.05 / (1000 * 60 * 60)
    hashesPerWatt = max([card['hps']['MD5'] / card['watt'] for card in cards.values()])
    #print([(name, card['hps']['MD5'] / card['watt']) for name, card in cards.items()])
    #print(hashesPerWatt)
    return hashesPerWatt / wattCost


factors = {
    'cloud': cloudHashesPerDollar,
    'watts': wattHashesPerDollar
}


parser = ArgumentParser(description='Generate a password.')

# For highly valuable passwords an attacker might allocate $10k
# On the other hand, however I would guess that an attacker with a budget of $100k
# might instead put it towards something spear phishing or 0day attack.
#
# Additionally if an attacker would spend $100k on hashing then the service
# would likely have MFA as an option to mitigate the impact.
#
# For most people the threat is untargeted cracking attack,
# which is typically not going to expend anything more than $1000 per account
parser.add_argument('--budget', type=int, default=10 * 1000, metavar='dollars',
                    help='budget for an attack (or if several attackers could collaborate, then their combined resources)')

# 1% is slim enough to deter most attacks, while 10% feels like it may be a bit too dicey
parser.add_argument('--acceptance', type=float, default=0.01, metavar='probability',
                    help='acceptable probability of an attack being successful using the full budget')

# Assume the attack is constrained by cloud costs, or electricity usage alone?
# At the moment cloud cracking is not too much more resource heavy than dedicated hardware.
# Typically the two differ by 1 character in length
parser.add_argument('--factor', choices=factors.keys(), default='cloud',
                    help='the constraining resource factor for the attack')

# Lots of people use the same password(s) for very long stretches of time
parser.add_argument('--lifetime', type=int, default=10, metavar='years',
                    help='lifespan of the secret')

parser.add_argument('--service', choices=['fido', 'ios', 'ios-with-erase', 'hello', 'facebook'],
                    help='services which use an HSM or TPM to prevent offline cracking')

parser.add_argument('--minimum-length', type=int, default=0, metavar='characters',
                    help='generate more characters if below the minimum length specified')

# More and more services seem to be cottoning on that only lowercase and length 16 is actually fairly good
# interestingly, if users do just the bare minimum to meet an complexity requirement, the entropy actually decreases
# because a digit has fewer possible combinations than a lowercase letter
parser.add_argument('--output', choices=['lowercase', 'complex', 'digits'])

parser.add_argument('--show-entropy', action='store_true',
                    help='display the entropy needed (in bits) without generating a password')


args = parser.parse_args()

rate = 0


defaultOutput = 'lowercase'


if args.service == 'fido':
    # https://fidoalliance.org/how-fido-works/
    # https://fidoalliance.org/specs/fido2/fido-client-to-authenticator-protocol-v2.1-rd-20191217.html#pinretries
    # Assume an attacker attempts 6 tries each night and waits until the next day for the user to unlock the key again
    rate = 6 / (60 * 60 * 24)

elif args.service == 'ios':
    # https://support.apple.com/en-gb/guide/security/sec20230a10d/web
    # Assume the device is lost or stolen and an automated pin entry system is used on the device
    # https://youtu.be/9R_D-zX3yP8
    rate = (4 + 1 + 1 + 2 + 1) / ((0 + 1 + 5 + 15 + 60) * 60)

elif args.service == 'ios-with-erase':
    rate = 10 / (args.lifetime * 365 * 24 * 60 * 60)
    defaultOutput = 'digits'

elif args.service == 'hello':
    # https://docs.microsoft.com/en-us/windows/security/information-protection/tpm/manage-tpm-lockout
    # Assume the device is lost or stolen and an automated pin entry system is used on the device
    # https://youtu.be/9R_D-zX3yP8
    # Assume the attacker can repeatedly reboot and attempt 32 tries in the space of 60 seconds
    # https://www.pcgamer.com/this-windows-10-pc-has-an-insanely-fast-boot-time-of-just-49-seconds/
    rate = 32 / (32 + 4.9)

elif args.service == 'facebook':
    # https://security.stackexchange.com/questions/181708/how-facebook-hashes-passwords
    # Unclear what the rate is, but Facebook implements brute-force lockout for up to 24h:
    # https://security.stackexchange.com/questions/84032/how-can-facebook-possibly-stop-a-bruteforce-attack-on-an-account
    rate = 1


if rate and not args.lifetime:
    exit('Please set lifetime when specifying a service')


if not args.output:
    args.output = defaultOutput


# Prices as of 2020-11-18
# https://cloud.google.com/compute/gpus-pricing
# https://aws.amazon.com/ec2/spot/pricing/
# Generally MD5 is good as a minimum computation benchmark.
# It may be tempting to factor down for bcrypt/scrypt et al. for lower performance on GPU,
# but when taking into account FPGA the performance difference is greatly reduced:
# https://scatteredsecrets.medium.com/bcrypt-password-cracking-extremely-slow-not-if-you-are-using-hundreds-of-fpgas-7ae42e3272f6
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
    combinations = ((args.budget / args.acceptance) * factors[args.factor]() * efficiency) / scale


if args.show_entropy:

    if args.output == 'lowercase':
        minimumLengthCombinations = len(ascii_lowercase) ** args.minimum_length
    elif args.output == 'complex':
        minimumLengthCombinations = len(ascii_uppercase) * (len(ascii_lowercase) ** (args.minimum_length - 3)) * len(digits) * len(punctuation)
    elif args.output == 'digits':
        minimumLengthCombinations = len(digits) ** args.minimum_length

    print(ceil(log(max(combinations, minimumLengthCombinations), 2)))
    exit()


password = ''
uniqueness = 1

if args.output == 'lowercase':
    while uniqueness < combinations or len(password) < args.minimum_length:
        password = password[:1] + secrets.choice(ascii_lowercase) + password[1:]
        uniqueness *= len(ascii_lowercase)

elif args.output == 'complex':
    password += secrets.choice(ascii_uppercase)
    uniqueness *= len(ascii_uppercase)

    password += secrets.choice(digits)
    uniqueness *= len(digits)

    password += secrets.choice(punctuation)
    uniqueness *= len(punctuation)

    while uniqueness < combinations or len(password) < args.minimum_length:
        password = password[:1] + secrets.choice(ascii_lowercase) + password[1:]
        uniqueness *= len(ascii_lowercase)

elif args.output == 'digits':
    while uniqueness < combinations or len(password) < args.minimum_length:
        password = password[:1] + secrets.choice(digits) + password[1:]
        uniqueness *= len(digits)


print(password)

