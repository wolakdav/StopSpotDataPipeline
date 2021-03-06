# End-to-end testing requirments

> StopSpot includes a variety of tests. Though most of them are unit tests that don't need to be configured, end-to-end test needs to be configured to be run succesfully. 

---

**TO RUN**: `python3 -m pytest ete-test/ete.py`


> This test runs separately from other tests (unit tests). In order for pytest not to detect this test during normal `pytest` command, which runs all tests, file is named in a way
> that doesn't allow pytest to catch it automatically. Thus, there is an explicit command to run end-to-end test. 

---

**WARNING**: All the **configurations** must be **prior** to running pytest, and all of them are in **assets/ete_config.json**. 

---

## Overview

*Note*: 
  - `input information` - tables that contain raw information on which analyzers will be ran.
  - `output information` - tables that contain analyzed information. 

End-to-end test verifies correct output by the program. Thus, test file does the following (besides small checks):
1. **Read** test data from csv and **upload** into test aperture (input information)
2. **Create** test hive (output information)
3. **Run** all data (input information) through **analyzers** and save data (output information) 
4. **Pull** data from hive (output information)
5. **Validate** that data from hive (output information) matches desired output
6. **Remove** test aperture (containing test input information) and test hive (containing output information)

## Must have

Since during pytest used input is prohibited, valid information must be supplied prior to testing:

  - `portal_user`					[Username to access server that holds database with input information]
  - `portal_passwd`					[Password to access server that holds database with input information]
  - `portal_hostname`				[URL to the server that holds database with input information]
  - `portal_db_name`				[Name of the database on the server that contain input information]
  - `portal_schema`					[Name of the schema which holds input information. *RECOMMEND*: test_yourInputDbName]
  - `pipeline_user`					[Username to access server that holds database with output information]
  - `pipeline_passwd`				[Password to access server that holds database with output information]
  - `pipeline_hostname`				[URL to the server that holds database with output information]
  - `pipeline_db_name`				[Name of the database on the server that contain output information]
  - `pipeline_schema`				[Name of the schema which holds output information. *RECOMMEND*: test_yourOutputDbName]
  - `output_path`           [Path to csv output. Default is output/csv/]
  - `output_type`           [Where output will be put. Default is aperture. Test changes the output to csv when testing csv output]