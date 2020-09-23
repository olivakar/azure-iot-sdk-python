#### MQTT Broker

For this part docker is needed to be installed in your machine.
The mqtt broker being used is in the folder `aedes`. 
This has been configured to run locally in a docker container.
There is no need to run the container as the python script will do so but it is needed to build the image to be run later.

The docker commands to build the appropriate image is :
`docker build -t mqtt-broker . `

The docker command to remove the above image is
`docker image rm mqtt-broker`

#### Script

For this part the python package called `docker` needs to be installed.
This package is needed so that the python script can access the Docker Engine API. 
It enables to do anything the docker command does, but from within python apps.

There is 1 variable that can be changed :-

`FACTOR_OF_KEEP_ALIVE` : the multiplication factor via which keep alive needs to be modified to calculate the amount of time the MQTT Broker will be down.

Other important variables already having values are :-
keep_alive : option for changing the default keep alive for MQTT broker. Currently set at 30 secs.
dead_duration : the amount of time the MQTT broker will be taken down for.
run_duration : the amount of time the MQTT broker will be run for after being started.

There are couple of other variables that should not be changed but are noteworthy :-
`MQTT_BROKER_RESTART_COUNT` : the count of times server will be stopped and started.