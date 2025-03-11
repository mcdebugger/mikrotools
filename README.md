# mikrotools

A set of tools to automate operation on Mikrotik devices

## Tools

- mikromanager

## Installation

Using pip:

```
pip install mikrotools
```

Using pipx:

```
pipx install mikrotools
```

## Usage

### mikromanager
mikromanager by default searches for settings.yaml in current working directory. You can specify path to config using -c option. Example settings file can be found at [settings.default.yaml](settings.default.yaml).

For example to list hosts from hosts.txt file using config from my_settings.yaml use the following command:

```
mikromanager list -c my_settings.yaml -i hosts.txt
```

For further help use mikromanager with -h or --help flag.

```
mikromanager -h
```

or

```
mikromanager [command] -h
```
