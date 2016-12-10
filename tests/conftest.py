import pytest
import testinfra
import time
import dns.resolver
import itertools
import json

check_output = testinfra.get_backend(
    "local://"
).get_module("Command").check_output

def pytest_addoption(parser):
    parser.addoption('--zone', type=str, help="DNS Zone to spawn",
                default="example.invalid", dest="zone")


def pytest_generate_tests(metafunc):
    if 'zone' in metafunc.fixturenames:
        metafunc.parametrize("zone", [metafunc.config.option.zone])

@pytest.fixture
def resolver(Docker):
    my_resolver = dns.resolver.Resolver()
    my_resolver.nameservers = [Docker.get_ip()]
    return my_resolver

@pytest.fixture()
def Docker(request):
    docker = DockerInstance(request)
    def teardown():
        check_output("docker rm -f %s", docker.docker_id)

    request.addfinalizer(teardown)
    return docker

class DockerInstance:
    def __init__(self, request):
        env = '-e "ZONES_DNSSEC=example.invalid"'
        if hasattr(request, 'param'):
            self.args = request.param
            keys = []
            if 'tsig_slave' in request.param:
                keys += request.param['tsig_slave']
            if 'tsig_update' in request.param:
                keys += request.param['tsig_update']
            self.keys = keys
            env += ' -e "TSIG_KEYS='
            i = 1
            tmp_env = ""
            for key in keys:
                tmp_env += "{index}:{key} ".format(index=i, key=key)
                i +=1
            env += tmp_env.strip()
            env += '"'
            i = 1
            if 'tsig_slave' in request.param:
                env += ' -e "TSIG_SLAVES='
                tmp_env = ""
                for key in request.param['tsig_slave']:
                    tmp_env+= "{index}:0.0.0.0/0:{index} ".format(index=i)
                    i +=1
                env += tmp_env.strip()
                env += '"'
            if 'tsig_update' in request.param:
                env += ' -e "TSIG_UPDATES='
                i = 1
                tmp_env = ""
                for key in request.param['tsig_update']:
                    tmp_env+= "{index}:0.0.0.0/0:{index} ".format(index=i)
                    i +=1
                env += tmp_env.strip()
                env += '"'

        docker_id = check_output("docker run --health-interval=2s -d %s nsmaster" % env)
        self.docker_id = docker_id
        while True:
            health =json.loads(check_output("docker inspect --format='{{json .State.Health}}' %s" % docker_id))
            time.sleep(1)
            if health['Status'] == 'healthy':
                break
        self.backend = testinfra.get_backend("docker://" + docker_id)

    def get_ip(self):
        return check_output(
            "docker inspect --format '{{ .NetworkSettings.IPAddress }}' %s",
            self.docker_id)
    
