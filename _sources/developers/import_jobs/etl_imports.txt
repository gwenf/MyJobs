===========
ETL Imports
===========

There are two main types of failures for etl imports.  General failures which affect all or a asignificant number of imports, or individual failures which affect only one business unit.  The former usually point to an issue in our codebase or our backend systems.  The latter most often result from receiving malformed xml when we attempt to import a job.   

ETL Import Process:
===================

#. Create BusinessUnit and Company

#. Get ZIP file from jobsfs

#. Get XML documents from zip file

#. Filter out jobs that shouldn't go onto our site

#. Convert from XML to dict for uploading to solr.  Also transform import data to common output.

#. Add redirects for jobs to database.

#. Add jobs to solr

#. Remove old jobs from solr.

#. Update business unit job count.



Debugging General Failures:
===========================

Determine root cause of failures.  Typically, there are 4 places where it can fail.  Determining where it is failing will generally point you into the right direction for fixing it.

#. **Failing while trying to download the ZIP file**.  This points to issues with the network or JobsFS.  The first step should be to attempt to download a zip file from jobsfs.directemployers.org/.  You will need a username and password that is available in the secrets file.  

    #. **If you cannot access that server**, this points to an issue with the server itself.  Check with Mario and/or Kyle to see if they can access the system over samba.  Speak with Lou about network access and checking on the network proxy.  Continue to work with them and debug as a server issue.

    #. **If you can access the server locally**, ssh to a worker box, and attempt to download a file via wget.  If that fails, compare ping addresses for jobsfs.directemployers.org between your box and the worker box, to ensure you're not having DNS resolution issues.  Attempt to download a general file or webpage from somewhere to ensure you have general network connectivity.  If you are able to download a file via wget, as user ubuntu '``cd /home/web/MyJobs/MyJobs/``' and `run a task manually`_.  Review the exception raised at this point, and begin to debug.  You've reached the end of predictable failures.

#. **Failing while trying to load XML documents**.  This points to an issue with the contents of the ZIP files.  This may be that the zipfiles themselves are malformed, or that we are unable to handle some common piece of data from the XML files.  

    #. **Validate the ZIP file is well formed**.  Download a ZIP file locally and validate that you can open and browse the files in the ZIP file.  If this fails, let Mario or Kyle know about the failure, and let them examine the ZIP file.

    #. **Validate the XML documents are well formed**.  If the failure is affecting multiple business units, but the ZIP file appears to be well formed when you download it, run one of the xml files through a XML validator. If this fails, let Mario or Kyle know about the failure, and ask them to review the XML document.  

    #. **Review error raised by lxml**.  If it validates successfully, `run a task manually`_ and review the exception raised during XML parsing.  Sometimes lxml, the python xml library fails to handle things correctly.  Review the results of running the task to determine the file, and examine it manually for anything that seems out of place.  

#. **Failure to parse XML documents**.  After we've successfully built an ElementTree Object from the XML document, we parse it to build a dictionary object to send to solr.  During this process, we extract several pieces of data from the ElementTree, cast some of them to other data types, and then do a variety of manipulations on them to build the solr document.  

    #. **Review errors raised during transformation**.  locally, `run a task manually`_ and review errors during transformation.  If there are xml access errors, compare to the original XML document, and ask if content acquisition has changed their format recently.  if there are casting errors, review the data in the original XML document again asking Content Acquisition if they've changed that field or element recently.  

#. **Failure to create Redirects**.  As part of imports, we create redirects for the jobs.  This involves contacting the database and inserting or updating a record.

    #. **Database Failures**. Ensure the worker is able to access the database by using the shell to query for redirects.  If this fails, debug network issues contacting the database.  Otherwise, `run a task manually`_ and debug from exceptions.

#. **Failure to Save Jobs**.  We upload the jobs to solr via json.  The upload process involves taking a list of dictionaries, chunking them into groups of 1024, casting them to json, and posting them to solr.

    #. **Check that the solr server is up** and responding to requests at {{solr_server}}:8983/solr.  If it is down, investigate solr instances.

    #. **Check access to solr from worker**.  Via wget, check that wget http://solr_server:8983/solr/seo/select?q=*%3A*&wt=json&indent=true returns.   

    #. **Check error messages from solr**.  If solr is up and accessible from the worker, `run a task manually`_ on the worker to see the error message during solr.  



Debugging Individual Failures:
==============================

Individual failures are much more likely to be due to the results of malformed XML than anything on our side.  With that in mind, the first step is typically to check **failures while trying to load XML documents** above, and **failing to parse XML documents** above.  Most of the time, the correct resolution for this is to identify the business unit and job that has failed, and then ask mario or Kyle to review it.  You can try `run a task manually`_ on your local box, and look at errors generated from that.  



.. _run a task manually:

Running a Task Manually:
========================

#. start a shell via '``python manage.py shell``',

#. execute '``from tasks import task_etl_to_solr``'

#. execute '``task_etl_to_solr(...)``' with the parameters from a failing task.  