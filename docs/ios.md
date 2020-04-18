# Class IOs

This class exists to be used for a unifying how several classes gather
information from the user and print verbose information.

#### `bool self.verbose`

This member contains a boolean reflecting if verbose printing is enabled. For
more, see `self.print()`.

#### `str self.prompt(prompt="", hide_input=False)`

This method is a public wrapper for `self._prompt`. Subclasses that do not want
this available should override it to throw `AttributeError:
self.__class__.__name__  has no attribute 'prompt'`.

#### `str self.print(print="", hide_input=False)`

This method is a public wrapper for `self._print`. Subclasses that do not want
this available should override it to throw `AttributeError: '{subclass}' has no
attribute 'print'`.

#### `str self._prompt(prompt="", hide_input=False)`

This method will prompt STDOUT with `prompt` and read from STDIN the returned
string. `hide_input` hides the input from appearing in the terminal as it is
typed; this is necessary for sensitive data, such as passwords.

#### `void self._print(string, obj=None, force=False)`

This method will is used to support verbose dialog. If `obj` is supplied, it is
printed after `string`. If `force` is `True`, then the message will print
regardless of the value in `self.verbose`.