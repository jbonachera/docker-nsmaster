import dns.resolver
import dns.tsigkeyring
import dns.zone
import dns.query
import pytest

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


