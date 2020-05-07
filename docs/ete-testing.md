# End-to-end testing requirments

StopSpot includes a variety of tests. Though most of them are unit tests that don't need to be configured, end-to-end test needs to be configured to be run succesfully. 
**WARNING**: All the configurations must be prior to running pytest, and all of them are in `assets/config.json`. 

## Overview
End-to-end test verifies correct output by the program. Thus, test file does the following (besides small checks):
`Step 1: ` - Read test data from csv and upload into test schema
`Step 2: ` - Create hive (schema and tables) for output data
`Step 3: ` - Run all data through analyzers and save data (use client process_data function)
`Step 4: ` - Pull data from the previous step
`Step 5: ` - Validate that output from the program matches desired output

## Must have
*Note*: 
- `input information` - tables that contain raw information on which analyzers will be ran.
- `output information` - tables that contain analyzed information. 

Since during pytest used input is prohibited, valid information must be supplied prior to testing:

- `portal_user`			[Username to access server that holds database with input information]
- `portal_passwd`		[Password to access server that holds database with input information]
- `portal_hostname`		[URL to the server that holds database with input information]
- `portal_db_name`		[Name of the database on the server that contain input information]
- `portal_schema`		[Name of the schema which holds input information. *RECOMMEND*: test_yourInputDbName]
- `pipeline_user`		[Username to access server that holds database with output information]
- `pipeline_passwd`		[Password to access server that holds database with output information]
- `pipeline_hostname`	[URL to the server that holds database with output information]
- `pipeline_db_name`	[Name of the database on the server that contain output information]
- `pipeline_schema`		[Name of the schema which holds output information. *RECOMMEND*: test_yourOutputDbName]