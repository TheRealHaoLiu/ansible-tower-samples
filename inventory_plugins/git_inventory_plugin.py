import csv
import os
import requests
from requests.auth import HTTPBasicAuth
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.errors import AnsibleError

__metaclass__ = type
DOCUMENTATION = r"""
name: git_inventory_plugin
author: Peter Rubenstein (@prube194)
short_description: Ansible dynamic inventory plugin
description:
    - This plugin generates an Ansible dynamic inventory from a CSV file stored in a GitHub repository.
options:
    plugin:
        description: Name of the plugin, "git_inventory_plugin.py"
        required: true
        type: str
    csv_url_prefix:
        description: URL prefix for the CSV file
        required: true
        type: str
    github_token:
        description:
            - GitHub token
            - If the value is not specified, the environment variable "github_token" is used
        required: false
        type: str
        env:
            - name: github_token
"""


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = "git_inventory_plugin"

    def verify_file(self, path):
        return path.endswith("git_inventory_plugin.yml")

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        # Load the configuration file
        config = self._read_config_data(path)

        # Get the URL of the CSV file from the configuration
        csv_url_prefix = config.get("csv_url_prefix")
        if not csv_url_prefix:
            raise AnsibleError(
                "csv_url_prefix is not defined in the configuration file"
            )

        # Get the GitHub token from env
        github_token = os.getenv("github_token")
        if not github_token:
            raise AnsibleError("github_token is not available in the environment")
        github_folder = os.getenv("GH_FOLDER")
        if not github_folder:
            raise AnsibleError("GH_FOLDER is not available in the environment")

        # Fetch the CSV file from the GitHub repository
        full_csv_url = f"{csv_url_prefix}/{github_folder}/inventory_seed.csv"
        self.display.display(f"Fetching CSV file from {full_csv_url}")

        basic_auth = HTTPBasicAuth(username=None, password=github_token)
        response = requests.get(f"{full_csv_url}", auth=basic_auth)
        self.display.display(f"Status Code: {response.status_code}")
        self.display.vv(f"response.text: {response.text}")
        if response.status_code != 200:
            raise AnsibleError(f"Failed to fetch CSV file from {full_csv_url}")

        # Parse the Project CSV file
        response_text = response.text.replace("\ufeff", "")  # remove BOM
        project_data = response_text.splitlines()
        self.display.display(f"Got {len(project_data)} lines from the CSV file")
        reader = csv.DictReader(project_data)

        # Create the inventory structure
        for row in reader:
            group = row.get("marsha")
            host = row.get("device_ip")
            ansible_host = row.get("device_ip")
            do_not_config_flag = row.get("do_not_config", "false").lower() == "true"
            system_hostname = "unknown"

            if group and host:
                # group_name = self._sanitize_group_name(group_name)
                # Modified for new_test_many branch
                combined_hostname = f"{host}.{group}"
                self.inventory.add_group(group)
                self.inventory.add_host(combined_hostname, group)
                self.inventory.set_variable(
                    combined_hostname, "ansible_host", ansible_host
                )
                self.inventory.set_variable(
                    combined_hostname, "do_not_config_flag", do_not_config_flag
                )
                self.inventory.set_variable(
                    combined_hostname, "system_hostname", system_hostname
                )


if __name__ == "__main__":
    print("This is a plugin file and cannot be executed directly")
