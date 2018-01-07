# Graylog Build Harness

I manage a number of Graylog servers at work, and occasionally spin up VM's for various projects. So, I had a need to quickly push out a new Graylog system with little human intervention.

This script helps automate a two server build-out of Graylog. The components are:

1. Graylog Application Server - Has Graylog and Mongodb
2. Graylog DB Server - Has Elasticsearch supported by Graylog

Plans are to keep tracking the latest version available at [https://www.graylog.org/download](https://www.graylog.org/download).

## Build Target

* Ubuntu 16.04 LTS
* Graylog v2.4
* Mongodb 3.4.7
* Elasticsearch 5.5.2

## Instructions

In our example, 192.168.1.1 will be our app server, and 192.168.1.2 will be the DB server. From a fresh install, run the following commands:

### Initial Setup (run on both app and db servers)
1. `apt-get install git -y`
2. `git clone git clone https://github.com/idlethreat/graylog-build.git`
3. `cd graylog-build/`

### Setup App Server

`python3 graylog_build.py <app> <DB IP Address> <Graylog Web admin password>`

To setup the app server, you'll need to give it the IP of the DB server. In our example, that IP is 192.168.1.2. So, on the app server, run:

`python3 graylog_build.py app 192.168.1.2 password1`

It will take about 15 minutes for everything to download and install. Graylog does __not__ automatically start up after install. Instructions are printed on the console on how to configure Graylog server to start on boot.

### Setup DB Server

`python3 graylog_build.py <db> <APP IP Address>`

To setup Elasticsearch on the db server, you'll need to give it the IP of the APP server. in our example, that IP is 192.168.1.1. So, on the db server run:

`python3 graylog_build.py db 192.168.1.1`

Auto install takes about 2 minutes. Elasticsearch auto-starts after install and configuration is complete.

### Version History

* 0.0 - initial release
* 0.1 - updated script to install latest MongoDB (3.4.7) from mongodb.org instead of using the older default 16.04 packages
* 0.2 - updated script to install latest Graylog (2.3.1) as well as the latest Elasticsearch (5.5.2). ES install routine adjusted, new memory mapping items added, too.
* 0.3 - updated script to install latest Graylog (2.4). No other changes.