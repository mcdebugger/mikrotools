# mikrotools

A set of tools to automate operation with Mikrotik devices

## Tools

- mikromanager

## Installation

`pip install mikrotools` (using pip) or `pipx install mikrotools` (using pipx)

## Usage

### mikromanager
mikromanager by default searches for settings.yaml in current working directory. You can specify path to config using -c option.

For example to list hosts from hosts.txt file using config from my_settings.yaml use the following command:

`mikromanager list -c my_settings.yaml -i hosts.txt`

For further help use mikromanager with -h or --help flag.

`mikromanager -h`

or

`mikromanager [command] -h`
