# Graylog Build Harness

I manage a number of Graylog servers at work, and occasionally spin up VM's for various projects. I had a need to quickly push out a new Graylog system with little human intervention. 

Script currently targets [Ubuntu Linux 18.04](https://www.ubuntu.com/)

This script helps automate a two server build-out of Graylog. The components are:

1. __Graylog Application Server__ - Has Graylog and Mongodb installed
2. __Graylog DB Server__ - Has Elasticsearch installed

Plans are to keep tracking the latest version available at [https://www.graylog.org/download](https://www.graylog.org/download).

## Build Target

* Ubuntu 18.04 LTS
* Graylog v3.2
* Mongodb 4
* Elasticsearch 6

## Instructions

In our below example, 192.168.1.1 will be our __app__ server, and 192.168.1.2 will be the __DB__ server. From a fresh install, run the following commands:

### [Step 0] Initial Setup

_run the following commands on both app and db servers_

1. `apt-get install git -y`
2. `git clone https://github.com/idlethreat/graylog-build.git`
3. `cd graylog-build/`

### [Step 1] Setup DB Server

`python3 graylog_build.py <db> <APP IP Address>`

To setup Elasticsearch on the db server, you'll need to give it the IP of the APP server. in our example, that IP is 192.168.1.1. So, on the db server run:

`python3 graylog_build.py db 192.168.1.1`

Auto install takes about 2 minutes. Elasticsearch auto-starts after install and configuration is complete.

### [Step 2] Setup App Server

`python3 graylog_build.py <app> <DB IP Address> <Graylog Web admin password>`

To setup the app server, you'll need to give it the IP of the DB server. In our example, that IP is 192.168.1.2. So, on the app server, run something like this (with a better password):

`python3 graylog_build.py app 192.168.1.2 password1`

It will take about 15 minutes for everything to download and install. Graylog does __not__ automatically start up after install. 

Instructions are printed on the console on how to configure Graylog server to start on boot. Follow them!

### [Step 3] Login and Configure Graylog

Now that the installs are finished, you should be able to browse to `http://192.168.1.1:9000`. Login with the username `admin` and the password you set in __Step 2__.

Check out Graylog's [Online documentation](https://docs.graylog.org/en/3.0/pages/getting_started/web_console.html) to help you set up inputs and finish configuring it. 

Enjoy!


#### Version History

* 0.0 - initial release
* 0.1 - updated script to install latest MongoDB (3.4.7) from mongodb.org instead of using the older default 16.04 packages
* 0.2 - updated script to install latest Graylog (2.3.1) as well as the latest Elasticsearch (5.5.2). ES install routine adjusted, new memory mapping items added, too.
* 0.3 - updated script to install latest Graylog (2.4). No other changes.
* 0.4 - updated script to install latest Graylog (3.2), MongoDB (4) and Elasticsearch (6). Updated installer to handle variable changes in a couple of config files.
