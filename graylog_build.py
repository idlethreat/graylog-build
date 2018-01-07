#!/usr/bin/env python3

import codecs
import hashlib
import sys
import os
import subprocess
import shutil
import socket

####################################################################################################################################################
# Variables!

graylogRepoUrl = "https://packages.graylog2.org/repo/packages/graylog-2.4-repository_latest.deb"
graylogArchiveName = "graylog-2.4-repository_latest.deb"

####################################################################################################################################################

####################################################################################################################################################
# Quick and dirty way to get the IP address of the host
def getIpAddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

####################################################################################################################################################

def configureDB(myIP):
    print ("### Configuring your Graylog Database Server now")
    
    # make a copy before any changes
    shutil.copyfile('/etc/elasticsearch/elasticsearch.yml','/etc/elasticsearch/orig.elasticsearch.yml')
    
    # Read in the file
    with open('/etc/elasticsearch/elasticsearch.yml', 'r', encoding='utf-8', errors='ignore') as file:
        filedata = file.read()
    
    # Replace the target string
    filedata = filedata.replace('#cluster.name: my-application','cluster.name: graylog')
    
    # Replace the target string
    myNetworkHost = getIpAddress()
    myNetworkHostInsert = 'network.host: {0}'.format(myNetworkHost)
    filedata = filedata.replace('#network.host: 192.168.0.1', myNetworkHostInsert)
        
    filedata = filedata.encode('ascii',errors='ignore')
    
    filedata = filedata.decode('ascii')
    
    with open('/etc/elasticsearch/elasticsearch.yml', 'w') as file:
        file.write(str(filedata))
    
    print ('### Configuring system memory')
    subprocess.call('sysctl -w vm.max_map_count=262144',shell=True)
    subprocess.call('echo "vm.max_map_count=262144" >> /etc/sysctl.conf',shell=True)
    
    print ('### Setting up Elasticsearch to start on boot')
    subprocess.call('systemctl daemon-reload',shell=True)
    subprocess.call('systemctl enable elasticsearch.service',shell=True)
    subprocess.call('systemctl restart elasticsearch.service',shell=True)
    

####################################################################################################################################################

def installDB(myIP):
    print ("### Setting up Database Server. Application server is {0}. If this is incorrect, hit CTRL+C now. Otherwise, hit ENTER".format(myIP))
    input()
    
    aptGetUpdate = subprocess.call('apt-get update', shell=True)
    if aptGetUpdate !=0:
        sys.exit("### apt-get update failed! Check out the errors above!")
    
    aptGetInstallPackages = subprocess.call('apt-get install apt-transport-https openjdk-8-jre-headless uuid-runtime -y', shell=True)
    if aptGetInstallPackages !=0:
        sys.exit("### apt-get install packages failed! Check out the errors above!")
    
    print ("### Setting up Elasticsearch...")
    
    # Elasticsearch 5 Install
    subprocess.call('wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -',shell=True)
    subprocess.call('echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-5.x.list',shell=True)
    subprocess.call('apt-get update && sudo apt-get install elasticsearch',shell=True)
    subprocess.call('systemctl daemon-reload',shell=True)
    subprocess.call('systemctl enable elasticsearch.service',shell=True)  
    
    configureDB(myIP)


####################################################################################################################################################
def configureApp(myIP,myPass):
    print ("### Configuring your Graylog Application Server now")
    
    # make a copy before any changes
    shutil.copyfile('/etc/graylog/server/server.conf','/etc/graylog/server/orig.server.conf') 
    
    # Read in the file
    with open('/etc/graylog/server/server.conf', 'r', encoding='utf-8', errors='ignore') as file:
        filedata = file.read()
    
    # Replace the target string
    myPasswordSecret = subprocess.check_output(['/usr/bin/pwgen', '-N', '1', '-s', '96']).decode("utf-8")
    myPasswordSecretInsert = 'password_secret = {0}'.format(myPasswordSecret)
    filedata = filedata.replace('password_secret =', myPasswordSecretInsert)
    
    # Replace the target string
    myRootPasswordSha2 = hashlib.sha256(str(myPass).encode('utf-8')).hexdigest()
    myRootPasswordSha2Insert = 'root_password_sha2 = {0}'.format(myRootPasswordSha2)
    filedata = filedata.replace('root_password_sha2 =', myRootPasswordSha2Insert)
    
    # Replace the target string
    myRestListenUri = getIpAddress()
    myRestListenUriInsert = 'rest_listen_uri = http://{0}:9000/api/'.format(myRestListenUri)
    filedata = filedata.replace('rest_listen_uri = http://127.0.0.1:9000/api/', myRestListenUriInsert)
    
    # Replace the target string
    myRestTransportUri = getIpAddress()
    myRestTransportUriInsert = 'rest_transport_uri = http://{0}:9000/api/'.format(myRestTransportUri)
    filedata = filedata.replace('#rest_transport_uri = http://192.168.1.1:9000/api/', myRestTransportUriInsert)

    # Replace the target string
    myWebListenUri = getIpAddress()
    myWebListenUriInsert = 'web_listen_uri = http://{0}:9000/'.format(myWebListenUri)
    filedata = filedata.replace('#web_listen_uri = http://127.0.0.1:9000/', myWebListenUriInsert)
    
    # Replace the target string
    filedata = filedata.replace('elasticsearch_shards = 4','elasticsearch_shards = 1')
    
    # Replace the target string
    myElasticsearchServer = myIP
    myElasticsearchServerInsert = 'elasticsearch_hosts = http://{0}:9200'.format(myElasticsearchServer)
    filedata = filedata.replace('#elasticsearch_hosts = http://node1:9200,http://user:password@node2:19200', myElasticsearchServerInsert)
           
    filedata = filedata.encode('ascii',errors='ignore')
    
    filedata = filedata.decode('ascii')
    
    with open('/etc/graylog/server/server.conf', 'w') as file:
        file.write(str(filedata))

    
####################################################################################################################################################
def installApp(myIP,myPass):
    print ("### Setting up Application Server. Database server is {0}. If this is incorrect, hit CTRL+C now. Otherwise, hit ENTER".format(myIP))
    input()
    
    aptTransportHttpsResult = subprocess.call('apt-get install apt-transport-https', shell=True)
    if aptTransportHttpsResult !=0:
        sys.exit("### Install failed! Check out the errors above!")
    
    repoWgetDownloadBuild = "wget {0} -O /tmp/{1}".format(graylogRepoUrl,graylogArchiveName)
    repoWgetDownload = subprocess.call( repoWgetDownloadBuild, shell=True)
    if repoWgetDownload !=0:
        sys.exit("### Download failed! Check out the errors above!")
    
    dpkgInstallBuild = "dpkg -i /tmp/{0}".format(graylogArchiveName)
    dpkgInstall = subprocess.call(dpkgInstallBuild, shell=True)
    if dpkgInstall !=0:
        sys.exit("### Graylog package install failed! Check out the errors above!")
        
    
    ###
    # MongoDB 3.4 Install and setup
    print ("### Setting up MongoDB...")
    subprocess.call('sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6', shell=True)
    subprocess.call('echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list',shell=True)
    subprocess.call('apt-get update', shell=True)
    subprocess.call('apt-get install -y mongodb-org', shell=True)
    subprocess.call('systemctl enable mongod.service', shell=True)
    subprocess.call('service mongod start', shell=True)   
    print ("### MongoDB setup complete!")
    ###
        
    aptGetInstallRequirements = subprocess.call('apt-get install openjdk-8-jre-headless pwgen -y', shell=True)
    if aptGetInstallRequirements !=0:
        sys.exit("### install requirements failed! Check out the errors above!")
        
    aptInstallGraylog = subprocess.call('apt-get install graylog-server -y', shell=True)
    if aptInstallGraylog !=0:
        sys.exit("### install of Graylog failed! Check out the errors above!")
    
    configureApp(myIP,myPass)
       
####################################################################################################################################################

###
# Argument check
###
if (len(sys.argv) < 3):
    print ("### ./graylog_build (app|db) <remote.ip> <password>")
    print ("### app: You wish to install Graylog application server and MongoDB on the local system")
    print ("### db: You wish to install Elasticsearch on the local system")
    print ("### <remote.ip>: IP address of the other device to connect with (database or application)")
    print ("### <password>: will set the default admin password to the <password> you enter here (application only)")
    sys.exit()

if not os.geteuid() == 0:
    sys.exit('Sorry. Script must be run as root')

if sys.argv[1] == "app":
    myIP = sys.argv[2]
    myPass = sys.argv[3]
    installApp(myIP, myPass)

if sys.argv[1] == "db":
    myIP = sys.argv[2]
    installDB(myIP)