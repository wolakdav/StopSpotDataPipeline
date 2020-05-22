#!/bin/bash
# This script will start the pipeline and give the user access to the text-based menu options.

# The created container is named pipeline. This name overlaps with the GUI container name as well, to prevent multiple from running at once.
# The container starts a bash session.
# The container has the "pipeline" folder mounted, and is made accessible at location "StopSpot_Data_Pipeline"
# The container will be deleted when it stops running.
# The tag "cli" is searched for as a base image for creating this container.

docker run -d -it \
	--name pipeline \
	--entrypoint "/bin/bash" \
	--mount type=bind,source="$(pwd)"/pipeline,target=/pipeline \
	--rm \
	cli

sudo docker exec -it pipeline python3 main.py

sudo docker stop pipeline
