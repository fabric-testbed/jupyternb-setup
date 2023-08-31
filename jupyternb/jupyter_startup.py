#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 FABRIC Testbed
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Author: Komal Thareja (kthare10@renci.org)
import json
import os
import traceback
from datetime import datetime

from fss_utils.sshkey import FABRICSSHKey
from atomicwrites import atomic_write
import wget
import tarfile
import re
import pip


class JupyterStartup:
    DEFAULT_URL = "default"
    DEFAULT_NOTEBOOK_LOCATION = "/home/fabric/work/"
    DEFAULT_FABRIC_CONFIG_LOCATION = "/home/fabric/work/fabric_config"
    DEFAULT_REQUIREMENTS_LOCATION = "/home/fabric/work/fabric_config/requirements.txt"
    DEFAULT_FABRIC_CONFIG_JSON_LOCATION = "/home/fabric/work/fabric_config/fabric_config.json"
    TOKENS_LOCATION = "/home/fabric/.tokens.json"
    TAGS = "rel1.3"
    REPO_URL = "https://github.com/fabric-testbed/jupyter-examples/archive/refs/tags/"
    EXAMPLES = "examples"
    URL = "url"
    LOCATION = "location"
    REFRESH_TOKEN = "refresh_token"
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    CREATED_AT = "created_at"
    DEFAULT_PRIVATE_SSH_KEY = "/home/fabric/.ssh/id_rsa"
    DEFAULT_PUBLIC_SSH_KEY = "/home/fabric/.ssh/id_rsa.pub"
    DEFAULT_FABRIC_LOG_LEVEL = "INFO"
    DEFAULT_FABRIC_LOG_FILE = "/tmp/fablib/fablib.log"

    FABRIC_CREDMGR_HOST = "FABRIC_CREDMGR_HOST"
    FABRIC_ORCHESTRATOR_HOST = "FABRIC_ORCHESTRATOR_HOST"
    FABRIC_TOKEN_LOCATION = "FABRIC_TOKEN_LOCATION"
    FABRIC_PROJECT_ID = "FABRIC_PROJECT_ID"
    FABRIC_NOTEBOOK_LOCATION = "FABRIC_NOTEBOOK_LOCATION"
    FABRIC_NOTEBOOK_TAGS = "FABRIC_NOTEBOOK_TAGS"
    FABRIC_NOTEBOOK_REPO_URL = "FABRIC_NOTEBOOK_REPO_URL"
    FABRIC_CONFIG_LOCATION = "FABRIC_CONFIG_LOCATION"
    FABRIC_REQUIREMENTS_LOCATION = "FABRIC_REQUIREMENTS_LOCATION"
    FABRIC_CONFIG_JSON_LOCATION = "FABRIC_CONFIG_JSON_LOCATION"
    FABRIC_BASTION_HOST = "FABRIC_BASTION_HOST"
    FABRIC_BASTION_USERNAME = "FABRIC_BASTION_USERNAME"
    FABRIC_BASTION_KEY_LOCATION = "FABRIC_BASTION_KEY_LOCATION"
    FABRIC_SLICE_PRIVATE_KEY_FILE = "FABRIC_SLICE_PRIVATE_KEY_FILE"
    FABRIC_SLICE_PUBLIC_KEY_FILE = "FABRIC_SLICE_PUBLIC_KEY_FILE"
    FABRIC_SLICE_PRIVATE_KEY_PASSPHRASE = "FABRIC_SLICE_PRIVATE_KEY_PASSPHRASE"
    FABRIC_BASTION_PRIVATE_KEY_NAME = "FABRIC_BASTION_PRIVATE_KEY_NAME"
    FABRIC_SLICE_PRIVATE_KEY_NAME = "FABRIC_SLICE_PRIVATE_KEY_NAME"
    FABRIC_SLICE_PUBLIC_KEY_NAME = "FABRIC_SLICE_PUBLIC_KEY_NAME"
    FABRIC_LOG_FILE = "FABRIC_LOG_FILE"
    FABRIC_LOG_LEVEL = "FABRIC_LOG_LEVEL"

    def __init__(self):
        self.notebook_location = os.environ.get(self.FABRIC_NOTEBOOK_LOCATION)
        if self.notebook_location is None:
            self.notebook_location = self.DEFAULT_NOTEBOOK_LOCATION

        self.token_location = os.environ.get(self.FABRIC_TOKEN_LOCATION)
        if self.token_location is None:
            self.token_location = self.TOKENS_LOCATION

        self.tags = os.environ.get(self.FABRIC_NOTEBOOK_TAGS)
        if self.tags is None:
            self.tags = self.TAGS

        self.repo_url = os.environ.get(self.FABRIC_NOTEBOOK_REPO_URL)
        if self.repo_url is None:
            self.repo_url = self.REPO_URL

        self.config_location = os.environ.get(self.FABRIC_CONFIG_LOCATION)
        if self.config_location is None:
            self.config_location = self.DEFAULT_FABRIC_CONFIG_LOCATION

        self.requirements_location = os.environ.get(self.FABRIC_REQUIREMENTS_LOCATION)
        if self.requirements_location is None:
            self.requirements_location = self.DEFAULT_REQUIREMENTS_LOCATION

        self.config_json_location = os.environ.get(self.FABRIC_CONFIG_JSON_LOCATION)
        if self.config_json_location is None:
            self.config_json_location = self.DEFAULT_FABRIC_CONFIG_JSON_LOCATION

    def create_config_dir(self):
        try:
            os.mkdir(self.config_location)
            environment_vars = {
                self.FABRIC_CREDMGR_HOST: os.environ[self.FABRIC_CREDMGR_HOST],
                self.FABRIC_ORCHESTRATOR_HOST: os.environ[self.FABRIC_ORCHESTRATOR_HOST],
                self.FABRIC_BASTION_HOST: os.environ[self.FABRIC_BASTION_HOST],
                self.FABRIC_PROJECT_ID: '<Update Project Id>',
                self.FABRIC_BASTION_USERNAME: '<Update User Name>',
                self.FABRIC_BASTION_KEY_LOCATION: f'{self.config_location}/{os.environ[self.FABRIC_BASTION_PRIVATE_KEY_NAME]}',
                self.FABRIC_SLICE_PRIVATE_KEY_FILE: f'{self.config_location}/{os.environ[self.FABRIC_SLICE_PRIVATE_KEY_NAME]}',
                self.FABRIC_SLICE_PUBLIC_KEY_FILE: f'{self.config_location}/{os.environ[self.FABRIC_SLICE_PUBLIC_KEY_NAME]}',
                self.FABRIC_SLICE_PRIVATE_KEY_PASSPHRASE: '<Update Passphrase>',
                self.FABRIC_LOG_LEVEL: self.DEFAULT_FABRIC_LOG_LEVEL,
                self.FABRIC_LOG_FILE: self.DEFAULT_FABRIC_LOG_FILE
            }
            string_to_write = ""
            for key, value in environment_vars.items():
                if '<' in value and '>':
                    string_to_write += f"#export {key}={value}\n"
                else:
                    string_to_write += f"export {key}={value}\n"

            with atomic_write(f'{self.config_location}/fabric_rc', overwrite=True) as f:
                f.write(string_to_write)

            string_to_write = f"UserKnownHostsFile /dev/null\n" \
                              f"StrictHostKeyChecking no\n" \
                              f"ServerAliveInterval 120 \n" \
                              f"Host bastion-?.fabric-testbed.net\n" \
                              f"User <Update Bastion User Name>\n" \
                              f"ForwardAgent yes\n" \
                              f"Hostname %h\n" \
                              f"IdentityFile {self.config_location}/{os.environ[self.FABRIC_BASTION_PRIVATE_KEY_NAME]}\n" \
                              f"IdentitiesOnly yes\n" \
                              f"Host * !bastion-?.fabric-testbed.net\n" \
                              f"ProxyJump <Update Bastion User Name>@{os.environ[self.FABRIC_BASTION_HOST]}:22\n"
            with atomic_write(f'{self.config_location}/ssh_config', overwrite=True) as f:
                f.write(string_to_write)
        except Exception as e:
            print("Failed to create config directory and default environment file")
            print("Exception: " + str(e))
            traceback.print_exc()

    @staticmethod
    def get_url_file_name(*, url: str):
        url = url.split("#")[0]
        url = url.split("?")[0]
        return os.path.basename(url)

    def __download_file(self, file_name_release: str, location: str):
        try:
            print(f"Downloading the {file_name_release}")
            file_name = wget.download(file_name_release, location)
            print(f"Extracting the tarball for the Downloaded code: {file_name}")
            with tarfile.open(file_name) as f:
                f.extractall(path=location)
            print(f"Removing the downloaded tarball")
            os.remove(file_name)
        except Exception as e:
            print(f"Failed to download file: {file_name_release} at location: {location}")
            print("Exception: " + str(e))
            traceback.print_exc()

    def download_notebooks(self):
        try:
            with open(self.config_json_location) as f:
                config_json = json.load(f)

            if config_json is None or len(config_json) == 0:
                print("Nothing to download! empty config_json")
                return

            examples = config_json.get(self.EXAMPLES)
            if examples is None or len(examples) == 0:
                print("Nothing to download! empty examples")
                return

            for e in examples:
                url = e.get(self.URL)
                location = e.get(self.LOCATION)

                if url is None or location is None:
                    continue

                release_url_dict = {}

                if url == self.DEFAULT_URL:
                    tag_list = self.tags.split(",")
                    for tag in tag_list:
                        release_url_dict[f"{location}/jupyter-examples-{tag}"] = f"{self.repo_url}/{tag}.tar.gz"

                else:
                    file_name = self.get_url_file_name(url=url)
                    tag = re.sub('.tar.gz|.zip', '', file_name)
                    release_url_dict[f"{location}/jupyter-examples-{tag}"] = url

                index = 0
                for release, url in release_url_dict.items():
                    if os.path.exists(release):
                        continue
                    print(f"Downloading examples: {url} at {location}")
                    self.__download_file(file_name_release=url, location=location)
                    index += 1
        except Exception as e:
            print("Failed to download github repository for notebooks")
            print("Exception: " + str(e))
            traceback.print_exc()

    def create_tokens_file(self):
        try:
            tokens_json = {self.REFRESH_TOKEN: os.environ.get("CILOGON_REFRESH_TOKEN"),
                           self.CREATED_AT: datetime.strftime(datetime.utcnow(), self.TIME_FORMAT)}

            with atomic_write(self.token_location, overwrite=True) as f:
                json.dump(tokens_json, f, indent=4)
        except Exception as e:
            print("Failed to create tokens file")
            print("Exception: " + str(e))
            traceback.print_exc()

    def create_requirements_file(self):
        try:
            with atomic_write(self.requirements_location, overwrite=True) as f:
                f.write("")
        except Exception as e:
            print("Failed to create tokens file")
            print("Exception: " + str(e))
            traceback.print_exc()

    def create_config_file(self):
        try:
            config_json = {
                self.EXAMPLES: [{
                    self.URL: self.DEFAULT_URL,
                    self.LOCATION: self.notebook_location
                }]
            }

            with atomic_write(self.config_json_location, overwrite=True) as f:
                json.dump(config_json, f, indent=4)
        except Exception as e:
            print("Failed to create tokens file")
            print("Exception: " + str(e))
            traceback.print_exc()

    def custom_install_packages(self):
        try:
            if os.path.exists(self.requirements_location):
                pip.main(["install", "-r", self.requirements_location])
        except Exception as e:
            print("Failed to install user specified packages!")
            print("Exception: " + str(e))
            traceback.print_exc()

    def update_permissions(self):
        """
        Find the location of the key files and change their permission
        :return:
        """
        if not os.path.exists(f"{self.config_location}/fabric_rc"):
            return
        # Open the file in read mode
        with open(f"{self.config_location}/fabric_rc", 'r') as file:
            # Read the content of the file
            content = file.read()

        # Split the content into lines
        lines = content.splitlines()

        # Process each line to extract the environment variable and its value
        for line in lines:
            # Ignore empty lines or lines starting with '#' (comments)
            if line.strip() == '' or line.strip().startswith('#'):
                continue

            # Split each line into variable and value using the first occurrence of '='
            variable, value = line.split('=', 1)
            variable = variable.replace("export", "")

            # Remove leading/trailing whitespaces from the variable and value
            variable = variable.strip()
            value = value.strip()

            if variable in [self.FABRIC_BASTION_KEY_LOCATION, self.FABRIC_SLICE_PRIVATE_KEY_FILE]:
                if os.path.exists(value):
                    os.chmod(value, 0o600)
            elif variable in [self.FABRIC_SLICE_PUBLIC_KEY_FILE]:
                if os.path.exists(value):
                    os.chmod(value, 0o644)

    def initialize(self):
        """
        Initialize Jupyter Notebook Container
        """
        if not os.path.exists(self.token_location):
            # New jupyternb container has been created
            # Create a token file
            print("Creating token file")
            self.create_tokens_file()

        if not os.path.exists(self.config_location):
            print("Creating config directory and all files")
            self.create_config_dir()

        if not os.path.exists(self.requirements_location):
            print("Creating default requirements.txt")
            self.create_requirements_file()

        if not os.path.exists(self.config_json_location):
            print("Creating default fabric_config.json")
            self.create_config_file()

        # Download the notebooks
        self.download_notebooks()

        # Create SSH Keys
        ssh_key = FABRICSSHKey.generate(comment="fabric@localhost", algorithm="rsa")
        with atomic_write(f'{self.DEFAULT_PRIVATE_SSH_KEY}', overwrite=True) as f:
            f.write(ssh_key.private_key)
        with atomic_write(f'{self.DEFAULT_PUBLIC_SSH_KEY}', overwrite=True) as f:
            f.write(f'{ssh_key.name} {ssh_key.public_key} {ssh_key.comment}')

        # Default key in config directory
        default_slice_priv_key_config = f'{self.config_location}/{os.environ[self.FABRIC_SLICE_PRIVATE_KEY_NAME]}'
        default_slice_pub_key_config = f'{self.config_location}/{os.environ[self.FABRIC_SLICE_PUBLIC_KEY_NAME]}'
 
        if not os.path.exists(default_slice_priv_key_config):
            with atomic_write(default_slice_priv_key_config, overwrite=True) as f:
                f.write(ssh_key.private_key)

        if not os.path.exists(default_slice_pub_key_config):
            with atomic_write(default_slice_pub_key_config, overwrite=True) as f:
                f.write(f'{ssh_key.name} {ssh_key.public_key} {ssh_key.comment}')

        os.chmod(self.DEFAULT_PRIVATE_SSH_KEY, 0o600)
        os.chmod(self.DEFAULT_PUBLIC_SSH_KEY, 0o644)
        os.chmod(default_slice_priv_key_config, 0o600)
        os.chmod(default_slice_pub_key_config, 0o644)

        self.update_permissions()
        self.custom_install_packages()


class Main:
    @staticmethod
    def run():
        js = JupyterStartup()
        js.initialize()


if __name__ == "__main__":
    Main.run()

