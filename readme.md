This script updates alerts DB and show some manipulations and insights.

**files doc**

1. alerts_data.db - sqllite DB
2. script_log.txt - log file
3. test.py - unit test for the API function
4. requirements.txt - dependencies of external libraries 

**Assumptions;**

1.  if the API call result is empty, it returns 404
2.  data is valid since 1.12.23
3.  data is updated manually in this stage by running script(we can use some
    orchestrator tool to run it in future)
4.  data is being saved into local db(SQLlite), hence alerts_data.db need to be included
5.  only new data is being saved to the DB(incremental run), program checks to max date
    that was reported.
6.  if API call doesn't work for some reason, script will be terminated.

**Conclusions from the data based on dashboards(based on data since 1.12.23 and might be changed);**

1. 17 is the hottest hour, most of the alerts were triggered there
2. between 23 to 5AM, there are no alerts, it's safe interval to take shower and sleep.
3. Sderot, Ivim, Nir-Am are top 3 dangerous places
