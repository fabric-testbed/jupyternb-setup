# jupyternb-setup
Software responsible for setting up Jupyter Hub Container for a FABRIC user.

## Overview
This package installs a startup script on the JH Container and configures the container as below:
- **Tokens**:
  <p>
  Creates a token file using the CI LOGON Refresh Token environment variable. This file is then used by Fablib to get tokens from the Credential Manager. The file is only created if it does not exist.
  </p>
- **Config Directory** `fabric_config`:
  <p>Creates the **fabric_config** directory if does not exist already. A default **fabric_rc** file is also created in the config directory with all the environment variables set to the defaults</p>
- **Requirements** `requirements.txt`
- **Config** `fabric_config.json`
- **Notebooks**
- **SSH Keys**
- **Custom Python Packages**
## Requirements
Python 3.9+

## Pre-requisites
Ensure that following are installed
```
virtualenv
virtualenvwrapper
```
## Installation
Multiple installation options possible. For CF development the recommended method is to install from GitHub MASTER branch:
```
$ mkvirtualenv jh-nb
$ workon jh-nb
$ pip install git+https://github.com/fabric-testbed/jupyternb-setup.git
```
For inclusion in tools, etc, use PyPi
```
$ mkvirtualenv jh-nb
$ workon jh-nb
$ pip install jupyternb-setup
```
