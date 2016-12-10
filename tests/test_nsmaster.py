import dns.resolver
import dns.tsigkeyring
import dns.zone
import dns.update
import dns.query
import pytest


def test_knotd_running(Docker):
    assert Docker.backend.get_module("Process").get(user="knot", comm="knotd")

def test_dns_resolution(Docker, resolver, zone):
    assert (len(resolver.query(zone, 'SOA')) > 0)

def test_dns_unauth_transfert(Docker, zone):
    try:
        z = dns.zone.from_xfr(dns.query.xfr(Docker.get_ip(), zone))
        assert False
    except dns.exception.FormError as err:
        assert err.message == "No answer or RRset not for qname"

@pytest.mark.parametrize("Docker", [
    {"tsig_slave": ["hmac-sha1:gXO8dNxnNIvc0/1lsueGkQ=="]},
    {"tsig_slave": ["hmac-sha256:laSOdIAZ4MZUj3gXdkjG2ZGe2JhVM+L2yjn7XyJD8SQ="]},
    {"tsig_slave": ["hmac-sha512:7NiBYmcL04UxudNLr6jySDd7B4ZNy+rbDC7rOnpzov+VxPbSfwXWVkAt3Q/F0gl4bJyf+MYxtyrxkXj410aCTQ=="]},
    {"tsig_slave": ["hmac-sha512:7NiBYmcL04UxudNLr6jySDd7B4ZNy+rbDC7rOnpzov+VxPbSfwXWVkAt3Q/F0gl4bJyf+MYxtyrxkXj410aCTQ==", 
                    "hmac-sha256:laSOdIAZ4MZUj3gXdkjG2ZGe2JhVM+L2yjn7XyJD8SQ="]}
    ], indirect=True)
def test_dns_auth_supported_transfert(Docker, zone):
    slave_keys = Docker.args['tsig_slave']
    i = 1
    for slave_key in slave_keys:
      keyring = dns.tsigkeyring.from_text({
          "key_%s" % i : slave_key.split(':')[1]
      })
      z = dns.zone.from_xfr(dns.query.xfr(Docker.get_ip(), zone, keyring=keyring, keyalgorithm=slave_key.split(':')[0], keyname='key_%s' % i))
      i +=1

@pytest.mark.parametrize("Docker", [
    {"tsig_slave": ["hmac-md5:cdIJ51NrNX81XYzCmc2vRyyxAR+PP7b5vpGqThvYHXkig1lOTgKnMxNVLKgvBtpfmqpFaqj2g9c9D3o8Zi78Kw=="]}
    ],indirect=True)
def test_dns_auth_unsupported_md5_transfert(Docker, zone):
    slave_keys = Docker.args['tsig_slave']
    i = 1
    for slave_key in slave_keys:
      keyring = dns.tsigkeyring.from_text({
          "key_%s" % i : slave_key.split(':')[1]
      })
      try:
          z = dns.zone.from_xfr(dns.query.xfr(Docker.get_ip(), zone, keyring=keyring, keyalgorithm=slave_key.split(':')[0], keyname='key_%s' % i))
          assert False
      except NotImplementedError as err:
          assert err.message == "TSIG algorithm hmac-md5. is not supported"

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
