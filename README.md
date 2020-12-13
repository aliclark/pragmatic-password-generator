# Pragmatic password generator

Generates sensible, secure passwords for everyday use.

```sh
$ ./ppg.py
jzgfdllpeaujvzdaol
```

The length of the password is calculated using public data based on the performance and cost of GPU password cracking, making sure it's prohibitively expensive to crack your password at today's prices (extrapolating for energy efficiencies into the future).

The password format ensures an uppercase letter, digit, and symbol are present.
The rest of the characters are lowercase to make them easy to type on mobile.

Enable MFA wherever possible addition to passwords.

## Usage

```
usage: ppg [-h] [--budget dollars] [--acceptance probability] [--factor {cloud,watts}] [--algorithm {MD5}] [--lifetime years] [--service {fido,hello,facebook}] [--minimum-length characters]
           [--output {lowercase,complexity,digits}] [--show-entropy]

Generate a password.

optional arguments:
  -h, --help            show this help message and exit
  --budget dollars      budget for an attack (if attackers could collaborate, then their combined resources)
  --acceptance probability
                        acceptable probability of an attack being successful using the full budget
  --factor {cloud,watts}
                        the constraining resource factor for the attack
  --algorithm {MD5}     the assumed algorithm under attack
  --lifetime years      lifespan of the secret
  --service {fido,hello,facebook}
                        services which use an HSM or TPM to prevent offline cracking
  --minimum-length characters
                        generate more characters if below the minimum length specified
  --format {add-complexity,lowercase,digits}
                        output options, the default is to vary character types to meet complexity requirements
  --show-entropy        display the entropy needed (in bits) without generating a password
```

Using the default parameters, an attacker 20 years into the future
spending a budget of $10k (inflation adjusted) on the Cloud would be expected to
have no greater than 1% probability of recovering your password from
a leaked database hashed using any algorithm.
