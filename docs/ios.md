# Class IOs

This class exists to be used for a unifying how several classes gather
information from the user and print verbose information. This class exists as a
singleton `ios`, which is in the `src.ios` package.

#### `ios.Severity`

This member is the class of severity Enums that can be supplied to the various
methods that desire severity levels.

- `Severity.DEBUG`
- `Severity.INFO`
- `Severity.WARNING`
- `Severity.ERROR`

#### `str ios.prompt(prompt="", hide_input=False)`

This method is a public wrapper for `ios._prompt`.

#### `void ios.print(print="", hide_input=False)`

This method is a public wrapper for `ios._print`.

#### `str ios.log_and_print(message, severity=Severity.INFO, obj=None)`

This will log the message with its severity and then print that message to
`STDOUT`. The output is the message logged without the datetime, and without
the severity if the severity is INFO.

#### `str ios.log(message, severity=Severity.INFO)`

This method will write the message with the severity level to the log file.
After every write, the buffer is flushed to best ensure an accurate log in the
case of a crash. This log file defaults to `pipeline/output/`, and the file is
named the date with a text file extension.

#### `str ios._prompt(prompt="", hide_input=False)`

This method will prompt `STDOUT` with `prompt` and read from `STDIN` the
returned string. `hide_input` hides the input from appearing in the terminal
as it is typed; this is necessary for sensitive data, such as passwords.

#### `void ios._print(string, obj=None)`

This method will is used to support dialog. If `obj` is supplied, it is printed
after `string`.

#### `void ios.start(filename=None)`

This method is available to outside sources to use but it is also handled
entirely by other methods.  

Open the file supplied for logging. If there is no file supplied, then use the
previously stored filename, or the default value if that is None as well. This
will not open a new file unless the current file is stopped.

#### `void ios.stop()`

This method is available to outside sources to use but it is also handled
entirely by other methods.  

Stop the open logging file. This will not stop a file unless there is no open
file.
