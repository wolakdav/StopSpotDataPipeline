# StopSpot WebUI

```
./LaunchUI.sh
```
Navigate to 0.0.0.0:5000 (or the IP of the server running the pipeline if accessing over the network)

The UI will attempt to load the log file for the current day, or display a message indicating it was not found. 

"Edit Config" will display a text editor allowing the config file to be updated and saved.

"Shutdown UI" will send a shutdown command to the docker containe. (the browser window will need to be manually closed).