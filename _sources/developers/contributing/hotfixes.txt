======================
How to Create a Hotfix
======================

Start your PR from the branch closest to production that you wish to deploy to
out of sequence.  Then create PRs against that branch and all the more recent
ones.  If you like, look at #1906 #1908 #1909 on MyJobs.  I based the branch on
master since that was the furthest I wanted to push the changes.  This assumes
that you know it'll be a hotfix when you start work.  
