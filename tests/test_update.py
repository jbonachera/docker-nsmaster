import dns.resolver
import dns.tsigkeyring
import dns.zone
import dns.update
import dns.query
import pytest

@pytest.mark.parametrize("Docker", [
    {"tsig_update": ["hmac-sha1:gXO8dNxnNIvc0/1lsueGkQ=="]},
    {"tsig_update": ["hmac-sha256:laSOdIAZ4MZUj3gXdkjG2ZGe2JhVM+L2yjn7XyJD8SQ="]},
    {"tsig_update": ["hmac-sha512:7NiBYmcL04UxudNLr6jySDd7B4ZNy+rbDC7rOnpzov+VxPbSfwXWVkAt3Q/F0gl4bJyf+MYxtyrxkXj410aCTQ=="]},
    {"tsig_update": ["hmac-sha512:7NiBYmcL04UxudNLr6jySDd7B4ZNy+rbDC7rOnpzov+VxPbSfwXWVkAt3Q/F0gl4bJyf+MYxtyrxkXj410aCTQ==", 
                    "hmac-sha256:laSOdIAZ4MZUj3gXdkjG2ZGe2JhVM+L2yjn7XyJD8SQ="]}
    ], indirect=True)
def test_dns_auth_update(Docker, resolver, zone):
    update_keys = Docker.args['tsig_update']
    i = len(Docker.args.get('tsig_slave', [])) + 1
    for update_key in update_keys:
        keyring = dns.tsigkeyring.from_text({
            "key_%s" % i : update_key.split(':')[1]
        })
        update = dns.update.Update(zone, keyring=keyring, keyalgorithm=update_key.split(':')[0], keyname='key_%s' % i)
        update.add('test', 0, 'A', '10.0.0.1')
        response = dns.query.tcp(update, Docker.get_ip(), timeout=10)

        answers = resolver.query('test.%s' % zone, 'A')
        assert (answers[0].address == '10.0.0.1')
        i += 1

def test_dns_unauth_update(Docker, resolver, zone):
    update = dns.update.Update(zone)
    update.add('test', 0, 'A', '10.0.0.1')
    response = dns.query.tcp(update, Docker.get_ip(), timeout=10)

    try:
        answers = resolver.query('test.%s' % zone, 'A')
    except dns.resolver.NXDOMAIN as err:
        assert err.message == "None of DNS query names exist: test.%s., test.%s." % (zone, zone)
