# deflatten_networks

## AAP Instructions

[Confluence Page](https://marriottcloud.atlassian.net/wiki/spaces/NTWK/pages/999063741/Network+Deflattening+Tool+Instructions)

## Command Line Instructions

### Standard run

```
ansible-playbook -i localhost, deflatten.yml -e RUNMODE=<dev|prod> [-e WRITEMODE=true] -e GH_FOLDER=<project>
```

### Run with everything stubbed

```
ansible-playbook -i localhost, deflatten.yml -e RUNMODE=<dev|prod> -e SNMP_STUB=true -e SP_STUB=true -e GIT_STUB=true -e NC_STUB=true -e COMMAND_STUB=true -e GH_FOLDER=<project> --skip-tags device_credentials
```
or

```
ansible-playbook -i localhost, deflatten.yml -e RUNMODE=<dev|prod> -e ALL_STUB=true -e GH_FOLDER=<project> --skip-tags device_credentials
```

### Enable "reload after" functionality

- To enable for both AOS and AOSCX, use --tags reload_command_all,all
- To enable for AOS only, use --tags reload_command_aos,all
- To enable for AOSCX only, use --tags reload_command_aoscx,all
