#Docker ns-master

Knot-based master DNS server for my DNS zones.
Zones are located in zones/ folder.

## Env
  * ZONES: list of dns zones
  * ZONES_DNSSEC: list of dns zone to automagically sign
  * TSIG_KEYS: tsig keys to allow transfers. syntax: "id:alg:secret". id will be prefixed by "key_"
  * TSIG_SLAVES: slaves. syntax: id:ip:tsig_key_id

