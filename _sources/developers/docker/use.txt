===========================================
Setting Up and Using Docker for Development
===========================================


What to Expect
==============

* Creates a known good working environment.

* Creates a local reverse proxy which is able to serve microsites in a manner
  consistent with production, including http vs. https handling.

* There will be permissions issues. The user running tools in the docker
  container will not have the same uid as the developer's own uid. This will
  result in occasional problems. This tends to affect pyc files, (not a big
  deal) and node_modules (occasionally annoying).

Preparation
===========

* Clone MyJobs repo.
* Add these to the root of the repo (get from another developer):

  * Permanently:

    * Settings.py

    * Dev_settings.py

    * Secrets.py

  * Temporarily:

    * Dump of development MySQL database (named dbbackup.sql). For example::

          mysqldump -u root -p db > dbbackup.sql;

      If you make a dump from a newer version of MySQL than what is in production
      you're going to have a bad time.

    * An archive of a working Solr configuration. For example::

          cp -r /usr/local/Cellar/solr/5.3.1/server/solr ~/projects/MyJobs

      If you make a dump from a newer version of Solr than what is in production
      you're going to have a bad time.

Getting Docker and the MyJobs Convenience Aliases Working
=========================================================

Our goal here is to get Docker installed and our shell aliases working.

First Time (OSX)
----------------

Install `Docker for Mac <https://download.docker.com/mac/stable/Docker.dmg>`_.

Open the dmg file and place the application in your Applications folder.

Follow the prompts to install.

Open the application. An icon of a whale will apear in the top bar and will
animate until docker has successfully started.

Once the animation has stopped, run ``docker ps`` in a terminal.
It should run without errors.

Know your local ip address. We'll call it $myip from now on.

First Time (Linux)
------------------

Install docker from your distro.

Make sure your user is added to the docker group.  

docker should be shown when you run ``groups``

Know your local ip address. We'll call it $myip from now on.

Terminal Setup (Both)
---------------------

``cd $myjobs`` where myjobs is wherever you checked out the MyJobs code.

``. dk2/env.sh`` This makes the ``dk`` convenience function available.

Initialize the Data Volumes and Certs
=====================================

This sets aside some volumes which will not be deleted when containers are
removed.

It also initializes some self signed ssl certificates for the reverse proxy.

``dk init``

Build the Development Image
===========================

Rerun this any time we change requirements.txt.

``dk rebuilddev`` Also takes a long time. [If it hits a glitch run this command again]

Build the Background Containers
===============================

MyJobs needs Solr, and MySQL, and we will also set up a reverse proxy here.

From the MyJobs directory and with ``dk2/env.sh`` sourced:

``dk pull`` Takes a long time. Downloads some Docker images for local use.

``export MYSQL_ROOT_PASSWORD="somepassword"`` This should only be needed when
running MySQL for the first time.

``dk background`` First run takes a long time.

``dk backgroundstop`` If you have problems here, restart docker itself or the
docker virtual machine.

If needed on Linux: ``systemctl restart docker``

If needed on OSX: Click the whale icon and press "reset" on the drop down.

Keep trying until ``docker ps`` shows no running machines.

Load Data into MySQL and Solr
=============================

``dk background`` At this point possibly only MySql and the reverse proxy will 
stay running.

``dk maint mysql:5.5`` Start an interactive container based on MySQL

``cp -a solr_config/* /var/solr/data`` assuming you have ``solr.xml`` and
friends in ``solr_config/``

``mysql -u root -p -h $myip``

``mysql> SET GLOBAL max_allowed_packet=1073741824;``

``exit``

``mysql -u root -p -h $myip db <dbbackup.sql`` assuming that your database
backup file is ``dbbackup.sql``

``exit`` Exits the interactive container.

``dk backgroundstop``

``docker ps`` Verify no running containers.

``dk background``

``docker ps`` Should show MySQL, Solr, and revproxy running.

Configure MyJobs to Run in Docker Containers
============================================

Appropriate settings, obtained from other developers, go in these files:

* ``secrets.py``

* ``settings_myjobs/settings.py``

* ``settings_dseo/settings.py``

* ``dev_settings.py``

Verify that Django Works
========================

``dkm test myjobs`` same as ``python manage.py test myjobs``.

Run Django Containers
=====================

We run these services in the interactively in the foreground as it's convenient
to have instant scrollable/searchable access to their logs.

Start a new terminal.

``dk runsecure``

Start a new terminal

``dk runmicrosites``

Access Local Containers with a Browser
======================================

Add to ``/etc/hosts``::

    $myip secure.my.jobs www.my.jobs

Add other microsites as needed.

Go to http://secure.my.jobs. You should have to click through a security
warning.

Run Webpack Dev Server
======================

Add to dev_settings.py::

    WEBPACK_DEV_SERVER_BASE_URL = "https://secure.my.jobs:8080"
    TEMPLATE_CONTEXT_PROCESSORS += (
        'myjobs.context_processors.webpack_dev_setting',
    )

Run::

    dkg npm run devserver

Visit the webpack base url above in a browser. Accept the certificate.

Visit a url using one of our JS bundles with a browser.

Change a ``.jsx`` file displayed in the browser. It should auto-reload.


Run Tests in the Background
===========================

From the root::

    dkgg watch-tasks watch

Set Up Docker with VM of Windows
================================

To use a Windows or other VM in conjunction with Docker (IE Testing, etc)

* Import a valid image into Virtual Box. Below are steps for a Windows VM are
    below

    * Download image from https://dev.windows.com/en-us/microsoft-edge/tools/vms/

    * Extract OVA file from downloaded zip file

    * Launch VirtualBox

    * Navigate File -> Import Appliance.. Select extracted OVA File

* Right click new VM image, Settings -> Network -> Attached To -> NAT

* From the console, run ``VBoxManage modifyvm "VM name" --natdnshostresolver1 on``

    * Replace "VM Name" with the name of the image you created

* From VirtualBox GUI, Select "Snapshots" and create a snapshot of the Image

    * This is useful for temporary licenses such as those for Windows. To reload
        the snapshot later, simply right-click and "Restore Snapshot"

* DNS entries in the host computers hosts file are available on Windows VM
