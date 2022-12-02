# jupyternb-setup
Software responsible for setting up Jupyter Hub Container for a FABRIC user.

## Overview
This package installs a startup script on the JH Container and configures the container as below:
NOTE: All files/directories created inside `/home/fabric/work` persist across container restarts.
### Tokens: `.tokens.json`
Creates a token file using the CI LOGON Refresh Token environment variable. This file is then used by Fablib to get tokens from the Credential Manager. The file is only created if it does not exist.
``` 
{
  "refresh_token": "<refresh_token>", 
  "created_at": "2022-12-01 21:34:56"
}
```
### Config Directory: `fabric_config`
- Creates the `fabric_config` directory at the location: `/home/fabric/work` if does not exist already.
```
$ ls -ltr fabric_config
total 20
-rw-------. 1 fabric users  650 Dec  1 21:48 fabric_rc
-rw-------. 1 fabric users  363 Dec  1 21:48 ssh_config
-rw-------. 1 fabric users    0 Dec  1 21:48 requirements.txt
-rw-------. 1 fabric users   68 Dec  1 21:48 fabric_config.json
-rw-------. 1 fabric users 2575 Dec  1 21:48 slice_key
-rw-r--r--. 1 fabric users  569 Dec  1 21:48 slice_key.pub
```
#### FABRIC Environment: `fabric_rc`
- Creates a `fabric_rc` file if it does not exist and sets the environment variables to the default values. User can overide te defaults by updating the `fabric_rc` file. 
```
export FABRIC_CREDMGR_HOST=cm.fabric-testbed.net
export FABRIC_ORCHESTRATOR_HOST=orchestrator.fabric-testbed.net
export FABRIC_BASTION_HOST=bastion-1.fabric-testbed.net
#export FABRIC_PROJECT_ID=<Update Project Id>
#export FABRIC_BASTION_USERNAME=<Update User Name>
export FABRIC_BASTION_KEY_LOCATION=/home/fabric/work/fabric_config/fabric-bastion-key
export FABRIC_SLICE_PRIVATE_KEY_FILE=/home/fabric/work/fabric_config/slice_key
export FABRIC_SLICE_PUBLIC_KEY_FILE=/home/fabric/work/fabric_config/slice_key.pub
#export FABRIC_SLICE_PRIVATE_KEY_PASSPHRASE=<Update Passphrase>
export FABRIC_LOG_LEVEL=INFO
export FABRIC_LOG_FILE=/tmp/fablib/fablib.log
```
NOTE: Defaults are configurable via the environment variables passed to the container on JH install as below:
```
singleuser:
  image:
    name: fabrictestbed/jupyter-notebook
    tag: 1.3.2
  extraEnv:
    FABRIC_CREDMGR_HOST: cm.fabric-testbed.net
    FABRIC_ORCHESTRATOR_HOST: orchestrator.fabric-testbed.net
    FABRIC_TOKEN_LOCATION: /home/fabric/.tokens.json
    FABRIC_NOTEBOOK_LOCATION: /home/fabric/work
    FABRIC_NOTEBOOK_TAGS: rel1.3.3
    FABRIC_NOTEBOOK_REPO_URL: https://github.com/fabric-testbed/jupyter-examples/archive/refs/tags/
    FABRIC_CONFIG_LOCATION: /home/fabric/work/fabric_config
    FABRIC_BASTION_HOST: bastion-1.fabric-testbed.net
    FABRIC_BASTION_PRIVATE_KEY_NAME: fabric-bastion-key
    FABRIC_SLICE_PRIVATE_KEY_NAME: slice_key
    FABRIC_SLICE_PUBLIC_KEY_NAME: slice_key.pub
```
#### Custom Python Packages: `requirements.txt`
- Creates an empty `requirements.txt` file if it does not exist. Any packages specified in this file are installed when the user container is spawned.
#### Jupyter Examples: `fabric_config.json`
- Creates `fabric_config.json` file if it does not exist with a default entry. This file is used to download the specific version of the Jupyter Hub Examples at the location specified. The default entry ensures release default version would be downloaded inside the container.
```
{
  "examples": [
                {"url": "default", "location": "/home/fabric/work/"}
              ]
}
```
Additional entries can be specified to download specific versions at a specified location such as below:
```
{"examples": [
        {"url": "default", "location": "/home/fabric/work/"},
        {"url": "https://github.com/fabric-testbed/jupyter-examples/archive/refs/tags/rel1.3.6.tar.gz", "location": "/home/fabric/"}
]}
```
For the below configuration, `jupyter-examples-rel1.3.6` would be downloaded at the location `/home/fabric`.
```
$ ls -ltr ~
total 4
drwxrwxr-x. 3 fabric users  147 Dec  1 21:28 jupyter-examples-rel1.3.6
drwxrwsrwx. 7 nobody users 4096 Dec  1 21:48 work
```

## Requirements
Python 3.9+

## Installation
Multiple installation options possible. For development the recommended method is to install from GitHub `main` branch:
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

NOTE: Any of the virtual environment tools ([venv], [virtualenv], or [virtualenvwrapper]) should work.

### Pre-requisites for the example above
Ensure that following are installed
```
virtualenv
virtualenvwrapper
```