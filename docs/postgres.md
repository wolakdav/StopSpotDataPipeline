You can get pgadmin4 from here: https://www.pgadmin.org/download/

If anyone is trying to install pgAdmin4 on ubuntu (think there’s some links to other based distros), I found this guide worked well: https://computingforgeeks.com/how-to-install-pgadmin-4-on-ubuntu/

Or get datagrip:
https://www.jetbrains.com/datagrip/

To add the server, in pgadmin4, go to "add new server" on the dashboard.

![pic here](https://i.imgur.com/mIyeVkm.png)
![pic here](https://i.imgur.com/bYLBolL.png)

- Under the "general" tab, the name can be anything you want. Nothing else needs to be input under that tab.
- Under the "connection" tab, fill it out like the above screenshot.
- Hostname/address is `westbot.westus.cloudapp.azure.com`
- Username and password is your first name and last initial, so DavidW for example.

The source data is located in the database “Aperture”, under the schema “Aperture”. You can write the output of your test data to the database setup for you, which is FirstnameLastinitial_db. David would be DavidW_db, for example.

