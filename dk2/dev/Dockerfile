from ubuntu:trusty

env DEBIAN_FRONTEND=noninteractive

run apt-get update
run apt-get --yes install \
    wget curl software-properties-common \
    apt-transport-https \
    && apt-get clean
run add-apt-repository -ys 'deb https://deb.nodesource.com/node_5.x trusty main'
run curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add -
run apt-get update

run apt-get --yes build-dep libgeos-dev && apt-get clean
run apt-get --yes install python-setuptools python-dev apache2 python-pip \
    mysql-client libxml2 libxml2-dev libxslt-dev libmysqlclient-dev\
    phantomjs python-ipdb strace nodejs && apt-get clean


# My.Jobs

run apt-get --yes install git-core inotify-tools

add requirements.txt /requirements.txt
run pip install -r requirements.txt
run pip install django-debug-toolbar sphinx

run mkdir /home/dev
run chmod 0777 /home/dev

volume /MyJobs
volume /deployment

env DEVSERVER_HTTPS=1
env HOME=/home/dev
