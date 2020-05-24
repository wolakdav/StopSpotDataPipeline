#!/bin/bash
# This script will start the pipeline and give the user access to the text-based menu options.

# The created container is named pipeline. This name overlaps with the GUI container name as well, to prevent multiple from running at once.
# The container starts a bash session.
# The container has the "pipeline" folder mounted, and is made accessible at location "StopSpot_Data_Pipeline"
# The container will be deleted when it stops running.
# The tag "gui" is searched for as a base image for creating this container.

docker run -d -it \
	-p 5000:5000	\
	--name pipeline \
	--mount type=bind,source="$(pwd)"/pipeline,target=/pipeline \
	--rm \
	gui

# customize this line to run flask
# Flask webpage should be accessible when the container is run, based on the command in the dockerfile
# If not, add whats needed here.
# sudo docker exec -it pipeline 

# Unsure how closing the container is going to work
# sudo docker stop pipeline