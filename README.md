# Pragmatic password generator

Generates sensible, secure passwords for everyday use.

```sh
$ ./ppg.py
Ucljiisrwkigdv8~
```

The length of the password is calculated using public data based on the performance and cost of GPU password cracking, making sure it's prohibitively expensive to crack your password at today's prices (extrapolating for energy efficiencies into the future).

The password format ensures an uppercase letter, digit, and symbol are present.
The rest of the characters are lowercase to make them easy to type on mobile.

If password compromise is within your threat model (eg. you use MFA) <sup>1</sup> <sup>2</sup> <sup>3</sup>
or the service incorporates measures against offline cracking attacks <sup>4</sup> <sup>5</sup>,
then consider using `./ppg.py --online` instead.

MFA is recommended wherever possible when using passwords.

## Usage

```
usage: ppg [-h] [--budget dollars] [--acceptance probability] [--factor {cloud,watts}]
           [--algorithm {MD5}] [--lifetime years] [--online [rate-per-second]]
           [--service {facebook}] [--minimum-length characters] [--show-entropy]

Generate a password.

optional arguments:
  -h, --help            show this help message and exit
  --budget dollars      the full budget for an attack
  --acceptance probability
                        acceptable probability of an attack being successful using the
                        full budget
  --factor {cloud,watts}
                        the constraining resource factor for the attack
  --algorithm {MD5}     the assumed algorithm under attack
  --lifetime years      lifespan of the secret
  --online [rate-per-second]
                        assume only online bruteforcing at rate/s
  --service {facebook}  services which use HSM to prevent offline cracking
  --minimum-length characters
                        generate more characters if below the minimum length specified
  --show-entropy        display the entropy needed (in bits) without generating a password
```

Using the default parameters, an attacker 2 years into the future
spending a budget of $10k on Google Cloud would be expected to
have no greater than 1% probability of recovering your password from
a leaked database which is secured by any kind of hashing.

1. https://en.wikipedia.org/wiki/Multi-factor_authentication
2. https://nakedsecurity.sophos.com/2019/05/23/google-stored-some-passwords-in-plain-text-for-14-years/#:~:text=The%20way%20Google%20typically%20handles,before%20being%20saved%20to%20disk.
3. https://nakedsecurity.sophos.com/2019/04/19/facebook-we-logged-100x-more-instagram-plaintext-passwords-than-we-thought/
4. https://security.stackexchange.com/questions/181708/how-facebook-hashes-passwords
5. https://dropbox.tech/security/how-dropbox-securely-stores-your-passwords
