HTTPS Proxy
===========
A transparent HTTP proxy server designed to run on Raspberri Pi and
redirect requests based on EFF's HTTPS Everywhere ruleset.

This project is in a working state, but still largely unfinished.

Installation
============
```
sudo apt install python-sqlite python-lxml python-regex nginx-light
```

Apply the `nginx.conf` snippet from this project somewhere in your
nginx configuration.

Set up iptables so that outgoing HTTP requests are routed through
the proxy. Example commands for an external router (10.0.1.1) routing
to a raspi running the proxy on port 81 (10.0.1.53).

```
iptables -t nat -A PREROUTING -s 10.0.1.0/24 -p tcp --dport 80 \
    -j DNAT --to 10.0.1.53:81
iptables -t nat -A POSTROUTING -s 10.0.1.0/24 -d 10.0.1.53 -p tcp \
    --dport 81 -j SNAT --to 10.0.1.1
```


Configuration
=============
The configuration file `https-proxy.cfg` is read on startup.

The following settings are available
```
rules = ./https-everywhere/rules
database = /dev/shm/https-proxy.sqlite
database_persist = /var/lib/https-proxy.sqlite
rule_extensions = .xml,.XML
```
