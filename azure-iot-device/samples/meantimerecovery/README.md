#### MQTT Broker

For this part docker is needed to be installed in your machine.
The mqtt broker being used is in the folder `aedes`. 
This has been configured to run locally in a docker container.
There is no need to run the container as the python script will do so 
but it is needed to build the image to be run later.

The docker commands to build the appropriate image is :
`docker build -t mqtt-broker . `

The docker command to remove the above image is
`docker image rm mqtt-broker`

#### Script for Mean Time to Recover

The main script for tracking mean time to recover is `mean_time_recover.py`.
For this part the python package called `docker` needs to be installed.
`pip install docker` will do this. 

This package is needed so that the python script can access the Docker Engine API. 
It enables to do anything the docker command does, but from within python apps.

There are some variables that can be changed :-

`FACTOR_OF_KEEP_ALIVE` : the multiplication factor via which keep alive needs to be modified to calculate the amount of time the MQTT Broker will be down.

Other important variables already having values are :-

`KEEP_ALIVE` : option for changing the default keep alive for MQTT broker. Currently set at 15 secs.
`KEEP_RUNNING` : the amount of time the server needs to keep running for.
dead_duration : the amount of time the MQTT broker will be taken down for.
`KEEP_DEAD` : The amount of time the MQTT broker will be non responsive.
`MQTT_BROKER_RESTART_COUNT` : the count of times server will be stopped and started.

Before running the the `mean_time_recover.py` script make sure your docker engine is running.

#### Cert creation

There is another script which will create some self signed certificates for use in the `aedes` server.
The certificates currently in the `aedes` server have validity but if validity expires the certificates need to be regenerated using this script.