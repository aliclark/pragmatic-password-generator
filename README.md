# pragmatic-password-generator

Generates sensible, secure passwords for everyday use.

```sh
$ ./ppg.py
Zsxxbjfsvoxbh3.
```

### Not suitable for encryption keys

This tool is not meant for generating encryption keys, because the lifetime of
encryption keys is typically much longer, even up to 100 years for confidential
information.

Use this command to generate encryption keys instead:

```sh
(tr -dc 0-9a-f </dev/urandom | head -c 32; echo)
```
