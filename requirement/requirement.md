# Requirements of Project

## Frontend
* Provide UI for users to upload target exectuable, signatures files and configure parameters. 
* The parameters of pharos tools are complex and with strict limitation. A good UI may help user to set all these parameters in correct way.
* Allow user to control and exec tools on server.
* Allow user to observe and download any output of Pharos tools.
* Possible techniques(popular frontend framework): Angular.js Vue.js

## Backend
* A server which could run all the Pharos tools on target exectuable.
* Save the user's target exectuable, signatures files and output of tools in a database for persistency.
* Python-base framework(Django) would be better to support command line interface.

## Database
* The input format would be JSON and number of clients is low, a noSQL light-weighted database(MongoDB) might be better to use.
* Providing data consistency if we have server cluster

## Dataformat
* RESTful communication between frontend and backend to separate them for flexibility.
* Pharos tools could output TEXT or JSON under user's demand, need to convert them to JSON before saving to database.

## Dataflow
* User-uploaded exectuable, signatures files go through backend into database.
* User's configure parameters and backend uses Pharos tools and save output to database.
* User look at outputs in database and download them.
