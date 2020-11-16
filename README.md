# Pragmatic password generator

Generates sensible, secure passwords for everyday use.

```sh
$ ./ppg.py
Ucljiisrwkigdv8~
```

The length of the password is calculated using public data based on the performance and cost of GPU password cracking, making sure it's prohibitively expensive to crack your password at today's prices (extrapolating for energy efficiencies into the future).

The password format ensures an uppercase letter, digit, and symbol are present.
The rest of the characters are lowercase to make them easy to type on mobile.

## Usage

```
usage: ppg [-h] [--budget BUDGET] [--acceptance ACCEPTANCE] [--factor {cloud,watts}]
           [--algorithm {MD5}] [--lifetime LIFETIME]

Generate a password.

optional arguments:
  -h, --help            show this help message and exit
  --budget BUDGET       the full budget in dollars for an attack
  --acceptance ACCEPTANCE
                        acceptable probability of an attack being successful using the
                        full budget
  --factor {cloud,watts}
                        the constraining factor for the attack
  --algorithm {MD5}     the assumed algorithm under attack
  --lifetime LIFETIME   number of years lifespan of the secret
```

Using the default parameters, an attacker 2 years into the future
spending a budget of $10k on Google Cloud would be expected to
have no greater than 1% probability of finding the password.
