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


