=====================
Imports Documentation
=====================

Our Job imports for direct_seo sites tend to follow the idea of the Extract, 
Transform, Load (ETL) process.  What this means is that to load jobs we 
generally start with getting the source files, extract the pertinent data for 
each job from them, transform it from the source format to something solr 
understands, and then batch insert it into solr.  

There are three sources for loading jobs.  The first corresponds with 
`tasks.task_update_solr` and is primarily used to load data from state job 
banks.  It gets it's data from `http://seoxml.directemployers.com/` and the 
data is retrieved as a single large XML document. 

The second, `tasks.task_etl_to solr` and `tasks.task_priority_etl_to_solr` is 
used to load individual companies data.  It retrieves a zipfile from 
`http://jobsfs.directemployers.org/`.  The reason that this is not used for 
state job banks is due to the fact the current format does not support having 
multiple companies in a single zipfile, which a state job bank requires.

The final source is the myjobs postajob system, and doesn't follow the standard 
import process, as the jobs are not imported using a typical batch ETL process, 
but are rather inserted and/or updated synchronously via the webservers.

.. toctree::
  :maxdepth: 2
  
  etl_imports