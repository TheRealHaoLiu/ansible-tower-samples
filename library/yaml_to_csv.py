"""
---
module: yaml_to_csv
short_description: Convert YAML file to CSV file
version_added: "0.1"
description:
  - This module converts a YAML file to a CSV file.
author:
  - Peter Rubenstein (@prube194)
options:
    yaml_file_path:
        description:
        - Path to the YAML file.
        required: true
    csv_file_path:
        description:
        - Path to the CSV file.
        required: true
    outer_key:
        description:
        - Outer key in the YAML file. Removed before conversion to CSV.
        required: false
        default: ""
"""

import pandas as pd
import yaml
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        yaml_file_path=dict(type="str", required=True),
        csv_file_path=dict(type="str", required=True),
        outer_key=dict(type="str", required=False, default=""),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    COLUMNS = [
        "date",
        "project",
        "job_id",
        "switch_ip",
        "switch_name",
        "switch_os",
        "ssh_version",
        "marsha",
        "ping_before",
        "snmp",
        "ping_after_lldp",
        "do_not_config",
        "ping_after",
        "interfaces",
        "reload_timer_set",
        "reload_timer_cancelled",
        "failure_reason",
        "success",
        "warnings",
    ]

    try:

        yaml_file_path = module.params["yaml_file_path"]
        csv_file_path = module.params["csv_file_path"]
        outer_key = module.params["outer_key"]

        with open(yaml_file_path) as stream:
            try:
                data = yaml.safe_load(stream)
                if outer_key:
                    data = data[outer_key]
                df = pd.DataFrame(data, columns=COLUMNS)
            except yaml.YAMLError as exc:
                raise Exception(exc)

        df.fillna("no_data", inplace=True)
        df.to_csv(csv_file_path, index=False)

    except Exception as e:
        module.fail_json(msg=f"{e.__class__}: {e}", **result)

    else:
        result["changed"] = True
        module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
