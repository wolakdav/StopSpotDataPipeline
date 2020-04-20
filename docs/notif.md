# StopSpot's Notification System

SpotSpot contains an external notification system, represented by class
`_Notif`, which is used to alert user(s) of issues that occur. _Notif is a
singleton, so there is an instance created on import that can be accessed with
the below.  

`from src.notif import notif`  
`notif.email("This is the subject", "This is the message")`  

While _Notif does extend IOs, it has removed `IOs.print()` and `IOs.prompt()`.
For more on IOs, see `docs/ios.md`.

## Methods Provided by _Notif

The notif instance has already taken an instance of Config such that it may
access configuration data. As a result of Config being able to dynamically
update this data, the methods of _Notif will update their member data on each
notification method call.

### `bool email(self, subject="", msg="")`

This method will send an email to the designated address stored in the Config
instance. If there is insufficient data to send the email, then the method will
prompt the user to enter it. The subject line of this email will be in the
following syntax.  

`[StopSpot Pipeline] ${subject} on/at ${datetime.now()}`.  

The parameter `msg` can be an empty string, a non-empty string, or a list of
strings, where the list of strings is `join`ed on a double newline. This method
will return True iff every recipient is successfully emailed.
