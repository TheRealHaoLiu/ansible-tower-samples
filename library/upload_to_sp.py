"""
---
module: upload_to_sp
short_description: Upload file to Sharepoint
version_added: "0.1"
description:
    - This module uploads a file to a Sharepoint site.
author:
    - Peter Rubenstein (@prube194)
options:
    file_path:
        description:
        - Path to the file to upload.
        required: true
    sp_server:
        description:
        - Sharepoint server.
        required: true
    sp_site_url:
        description:
        - Sharepoint site URL.
        required: true
    sp_folder:
        description:
        - Sharepoint folder.
        required: true
    sp_subfolder:
        description:
        - Sharepoint subfolder.
        required: false
    sp_user:
        description:
        - Sharepoint user.
        required: true
    sp_pass:
        description:
        - Sharepoint password.
        required: true
"""
import os

from ansible.module_utils.basic import AnsibleModule
from mind_msofficeapps import Sharepoint


def run_module():

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        file_path=dict(type="str", required=True),
        sp_server=dict(type="str", required=True),
        sp_site_url=dict(type="str", required=True),
        sp_folder=dict(type="str", required=True),
        sp_subfolder=dict(type="str", required=False),
        sp_user=dict(type="str", required=True),
        sp_pass=dict(type="str", required=True),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    try:

        file_path = module.params["file_path"]
        sp_site_url = module.params["sp_site_url"]
        sp_user = module.params["sp_user"]
        sp_pass = module.params["sp_pass"]
        sp_server = module.params["sp_server"]
        sp_folder = module.params["sp_folder"]
        sp_subfolder = module.params["sp_subfolder"]

        sp = Sharepoint(sp_site_url, sp_user, sp_pass, sp_server)

        sp.connect()

        filename = os.path.basename(file_path)
        site_folder = sp_site_url + f"/Shared Documents/{sp_folder}"
        site_subfolder = site_folder + f"/{sp_subfolder}"
        # An idempotent action. Has no effect if folder already existing
        sp.create_folder(site_folder)
        sp.create_folder(site_subfolder)

        with open(file_path, "rb") as IFH:
            content = IFH.read()
            return_json = sp.upload_file(content, filename, site_subfolder, request_return_json=True)

    except Exception as e:
        module.fail_json(msg=f"{e.__class__}: {e}", **result)

    else:
        result["changed"] = True
        result["return_json"] = return_json
        module.exit_json(**result)

def main():
    run_module()


if __name__ == "__main__":
    main()
