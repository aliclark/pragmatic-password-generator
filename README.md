# Pragmatic password generator

Generates sensible, secure passwords for everyday use.

```sh
$ ./ppg.py
jzgfdllpeaujvzdaol
```

The length of the password is calculated using public data based on the
performance and cost of GPU password cracking, making sure that it's
prohibitively expensive to crack your password at today's prices, and
extrapolating into the future based on energy efficiency trend data.

Using the default parameters, an attacker with
 * a $10k budget
 * on the Cloud
 * 20 years' time from now
 * should only have a 1% chance of recovering your password even if it's protected using a weak hash

(This currently corresponds to 82 bits of entropy)

It's still a good idea to also enable 2FA on accounts wherever possible in
addition to using a secure password.

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
