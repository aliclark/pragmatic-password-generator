# Pragmatic password generator

Generates sensible, secure passwords for everyday use.

```sh
$ ./ppg.py
Zsxxbjfsvoxbh3.
```

The length of the password is calculated using public data based on the performance and pricing of GPU password cracking, making sure it's prohibitively expensive to crack your password at today's prices.

The password format ensures an uppercase letter, digit, and symbol are present.
The rest of the characters are lowercase to make them easy to type on mobile.

## Usage

```
usage: ppg.py [-h] [--budget BUDGET] [--acceptance ACCEPTANCE] [--factor {cloud,watts}] [--algorithm {MD5}]

Generate a password.

optional arguments:
  -h, --help            show this help message and exit
  --budget BUDGET       the full budget in dollars for an attack
  --acceptance ACCEPTANCE
                        acceptable probability of an attack being successful using the full budget
  --factor {cloud,watts}
                        the constraining factor for the attack
  --algorithm {MD5}     the assumed algorithm under attack
```
