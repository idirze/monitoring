# netdata-binary

Ansible role for installing Netdata using the binary installers from https://github.com/firehol/binary-packages/ instead of from source. Supports configuration via the `netdata_config` variable.

## Variables

* `netdata_version`: The version to install (defaults to `latest`).
* `netdata_installer_options`: Set options passed to the installer such as `--dont-start-it` (defaults to `""`).
* `netdata_config`: A dictionary of the configuration. The top level of the dictionary becomes the headers. See the example below (is undefined by default).

## Example Playbook

Example using all the variables:

```
- hosts: servers
  become: yes
  vars:
    netdata_version: v1.9.0-237-g10561d5a-x86_64-20180120-053010
    netdata_installer_options: --dont-start-it
    netdata_config:
      global:
        history: 7200
      "plugin:apps":
        update every: 1
      "plugin:proc":
        /proc/net/snmp: "no"
        /proc/net/snmp6: "no"
  roles:
    - andyshinn.netdata-binary
```
