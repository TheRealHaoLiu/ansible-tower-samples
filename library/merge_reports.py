"""
---
module: merge_reports
short_description: Merge all of the reports in a SharePoint folder into a single CSV file.
version_added: "0.1"
description:
    - This module merges all of the reports in a SharePoint folder into a single CSV file.
author:
    - Peter Rubenstein (@prube194)
options:
    sp_server:
        description:
        - Sharepoint server.
        required: true
    sp_site_url:
        description:
        - Sharepoint site URL.
        required: true
    sp_user:
        description:
        - Sharepoint user.
        required: true
    sp_pass:
        description:
        - Sharepoint password.
        required: true
"""

import logging

import re
import os
import pandas as pd
from ansible.module_utils.basic import AnsibleModule
from mind_msofficeapps import Sharepoint

os.makedirs("logs", exist_ok=True)
os.makedirs("files/reports", exist_ok=True)

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
    filename="logs/merge_reports.log",
)


def run_module():

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        sp_server=dict(type="str", required=True),
        sp_site_url=dict(type="str", required=True),
        sp_user=dict(type="str", required=True),
        sp_pass=dict(type="str", required=True),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    try:
        sp_site_url = module.params["sp_site_url"]
        sp_server = module.params["sp_server"]
        sp_user = module.params["sp_user"]
        sp_pass = module.params["sp_pass"]
        columns = [
            "date",
            "project",
            "job_id" "marsha",
            "switch_ip",
            "ping_before",
            "snmp",
            "ping_after_lldp",
            "ping_after",
            "interfaces",
            "reload_timer_set",
            "reload_timer_cancelled",
            "ssh_version",
            "do_not_config",
            "failure_reason",
            "success",
            "warnings",
        ]

        all_data = pd.DataFrame(columns=columns)
        test_data = pd.DataFrame(columns=columns)
        local_dir = "files/reports"

        sp = Sharepoint(sp_site_url, sp_user, sp_pass, sp_server)
        sp.connect()

        main_folder = sp_site_url + "/Shared Documents/flat_networks_project/"
        projects = sp.get_folders(main_folder)
        logging.debug(f"Projects: {projects}")

        for project in projects:
            project_folder = main_folder + project
            logging.debug(f"Project folder: {project_folder}")
            site_folders = sp.get_folders(project_folder)
            logging.debug(f"Site folders: {site_folders}")
            for site_folder in site_folders:
                site_path = project_folder + "/" + site_folder
                site_files = sp.get_files(site_path)
                logging.debug(f"Site files: {site_files}")
                if "group_report.csv" in site_files:
                    fcontent = sp.get_file("group_report.csv", site_path)
                    with open(f"{local_dir}/{project}_{site_folder}.csv", "w") as f:
                        f.write(fcontent.decode("utf-8"))
                    site_data = pd.read_csv(f"{local_dir}/{project}_{site_folder}.csv")
                    # if project in ["lab", "test_project"]:
                    if re.match(r"lab|test_project", project):
                        test_data = pd.concat([test_data, site_data], ignore_index=True)
                    else:
                        all_data = pd.concat([all_data, site_data], ignore_index=True)

        if not all_data.empty:
            all_data.to_csv(f"{local_dir}/all_reports.csv", index=False)
            sp.upload_file(
                open(f"{local_dir}/all_reports.csv", "rb").read(),
                "all_reports.csv",
                main_folder,
            )

        if not test_data.empty:
            test_data.to_csv(f"{local_dir}/all_reports_test.csv", index=False)
            sp.upload_file(
                open(f"{local_dir}/all_reports_test.csv", "rb").read(),
                "all_reports_test.csv",
                main_folder,
            )

        if all_data.empty and test_data.empty:
            result["msg"] = "No reports found."
            result["changed"] = False
        else:
            result["msg"] = "Reports merged."
            result["changed"] = True

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"{e.__class__}: {e}", **result)

    else:
        result["return_json"] = return_json  # type: ignore
        module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
