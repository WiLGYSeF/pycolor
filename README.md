# pycolor

1. [Example Usage](#example-usage).
2. [Configuration](#configuration).

A Python wrapper program that executes commands to perform real-time terminal output coloring using ANSI color codes.
Color formatting can be added to program output using JSON configuration files and regular expressions to improve readability of the output.

# Example Usage

pycolor can be used explicitly on the command line:

__Before:__

![sample df output](/docs/images/sample-df-output.png)

__After:__

![sample colored df output](/docs/images/sample-df-output-colored.png)

----

pycolor can also be aliased in `~/.bashrc` like so:
```bash
alias rsync='pycolor rsync'
```
__Before:__

![sample rsync output](/docs/images/sample-rsync-output.png)

__After:__ (note pycolor omitted lines with trailing slashes in addition to coloring output for better readability)

![sample colored rsync output](/docs/images/sample-rsync-output-colored.png)

# Configuration
