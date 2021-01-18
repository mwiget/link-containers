#!/usr/bin/env python3

import sys
import time
import os
import docker
from pyroute2 import NetNS, IPRoute
from pprint import pprint
from threading import Event


def create_netns(container):
    client = docker.from_env()
    if not (os.path.exists("/var/run/netns/" + container)):
        # print("path doesn't exists")
        while True:
            try:
                co = client.containers.get(container)
                if co.attrs['State']['Running']:
                    break

            except:
                print("waiting for container {} ...".format(container))
                sys.stdout.flush()
                time.sleep(1)
                pass

        pid = co.attrs['State']['Pid']
        # print("{} has pid={}".format(container, pid))
        os.symlink("/proc/{}/ns/net".format(pid),
                   "/var/run/netns/" + container)


def newifname(container):
    ns = NetNS(container)
    i = 0
    for link in ns.get_links():
        ifname = link.get_attr('IFLA_IFNAME')
        if ifname.startswith('eth'):
            i += 1
    ns.close()
    return('eth{}'.format(i))


def addlink(c1, c2):
    create_netns(c1)
    ifname1 = newifname(c1)
    create_netns(c2)
    ifname2 = newifname(c2)

    ipr = IPRoute()
    ipr.link('add', ifname='veth1', kind='veth', peer='veth2')
    idx1 = ipr.link_lookup(ifname='veth1')[0]
    idx2 = ipr.link_lookup(ifname='veth2')[0]
    ipr.link('set', index=idx1, ifname=ifname1,
             net_ns_fd=c1, state='up', mtu=MTU)
    ipr.link('set', index=idx2, ifname=ifname2,
             net_ns_fd=c2, state='up', mtu=MTU)
    print("link {}:{} <---> {}:{} created".format(c1, ifname1, c2, ifname2))


if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print("usage: {} container1 container2".format(sys.argv[0]))
        exit(1)
    addlink(sys.argv[1], sys.argv[2])
