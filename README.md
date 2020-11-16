# pragmatic-password-generator

Generates sensible, secure passwords for everyday use.

```sh
$ ./ppg.py
Zsxxbjfsvoxbh3.
```

The length of the password is calculated using public data based on the performance and pricing of cloud GPU password cracking to make sure it's prohibitively expensive to crack at today's prices.

The password format ensures an uppercase letter, digit, and symbol are present.
The rest of the characters are lowercase to make them easy to type on mobile.

### Not suitable for encryption keys

This tool is not meant for generating encryption keys since the lifetime of
an encryption key is typically much longer than a password, eg. up to 100 years or so, instead of a couple.

You could use this command to generate encryption keys instead:

```sh
(tr -dc 0-9a-f </dev/urandom | head -c 32; echo)
```

### Dedicated cluster

There is also an algorithm to generate a password which is secure against an attacker using
their own GPU cluster and wholesale energy pricing. If you believe this fits your threat model,
then set `infrastructure = 'hosted'` and rerun the program.

At the time of writing, this makes the passwords 1 character longer.
