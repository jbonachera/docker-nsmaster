#Docker ns-master

Knot-based master DNS server for my DNS zones.
Zones are located in zones/ folder.

## License

MIT

## Env
  * ZONES_DNSSEC: list of dns zone to automagically sign
  * TSIG_KEYS: tsig keys to allow transfers. syntax: "id:alg:secret". id will be prefixed by "key_"
  * TSIG_SLAVES: slaves. syntax: id:allowed_ip:tsig_key_id
  * TSIG_UPDATES: those keys are allowed to update all zones. syntax: id:allowed_ip:tsig_key_id
  * DNSTAP_SOCKET: dnstap socket path. Disabled if empty.

## Example

Spawn a Knot DNS Server hosting the "example.invalid" zone, and déclares 2 TSIG keys. 

One will be allowed to transfert the zone from 203.0.113.1, and the other will be allowed to update the zone using for example `nsupdate`.

```
docker run -it -e 'ZONES_DNSSEC=example.invalid' -e 'TSIG_KEYS=1:hmac-sha512:blablalblabla 2:hmac-sha512:blablalbalblabla' -e 'TSIG_SLAVES=1:203.0.113.1:1' -e 'TSIG_UPDATES=2:0.0.0.0/0:2'
```

## Tests

This project can be tested with testinfra (https://github.com/philpep/testinfra), by running `make test`.

Testinfra is configured to spawn a docker container for each test, and to remove it after.

Launch configuration (environment var) are passed by pytest parameters.

## TODO

  * Clean the testinfra configuration (I don't like all the mess around `docker run` in conftest.py)
  * Test DNSSEC signature (before, and after updating the zone)

