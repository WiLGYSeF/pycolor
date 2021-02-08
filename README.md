# Pycolor

1. [Example Usage](#example-usage).
2. [Configuration](#configuration).
3. [Formatting Strings](#formatting-strings).

A Python wrapper program that executes commands to perform real-time terminal output coloring using ANSI color codes.
Color formatting can be added to program output using JSON configuration files and regular expressions to improve readability of the output.

# Example Usage

Pycolor can be used explicitly on the command line:

__Before:__

![sample df output](/docs/images/sample-df-output.png)

__After:__

![sample colored df output](/docs/images/sample-df-output-colored.png)

[Sample df configuration file.](/docs/sample-config/df.json)

----

Pycolor can also be aliased in `~/.bashrc` like so:
```bash
alias rsync='pycolor rsync'
```

__Before:__

![sample rsync output](/docs/images/sample-rsync-output.png)

__After:__ (note Pycolor omitted lines with trailing slashes in addition to coloring output for better readability)

![sample colored rsync output](/docs/images/sample-rsync-output-colored.png)

[Sample rsync configuration file.](/docs/sample-config/rsync.json)

# Configuration
Pycolor will first try to load configuration from `~/.pycolor.json` before loading files found in `~/.pycolor/` in filename order.

When looking for a profile to use, pycolor will select the last matching profile based on the `name` or `which` property.

Patterns are applied first-to-last for each profile.

Configuration file template:
```json
{
    "profiles": [
        {
            "name": "ls",
            "profile_name": "ls",
            "which": "/bin/ls"
        }
    ]
}
```

# Formatting Strings
