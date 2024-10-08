from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: hammerdb
    author: Mark Wong
    short_description: Lookup HammerDB server, based on its private_ip
    description:
      - "Lookup HammerDB server, based on its private_ip"
    options:
      _terms:
        description: Private IP of the HammerDB server.
        required: False
      default:
        description: hammerdb_private_ip of the current node.
"""

EXAMPLES = """
- name: Show HammerDB server informations
  debug: msg="{{ lookup('hammerdb') }}"
"""

RETURN = """
_value:
  description:
    - List of HammerDB server nodes
  type: list
  elements:
    - dict: node_type, hostname, ansible_host (public IP address), private_ip
"""

from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):

        myvars = getattr(self._templar, '_available_variables', {})
        inventory_hostname = variables['inventory_hostname']

        # If no terms, we'll used the current HammerDB server private IP
        if len(terms) == 0:
            if 'hammerdb_private_ip' not in myvars['hostvars'][inventory_hostname]:
                # hammerdb_private_ip not set, return None
                return []
            hammerdb_private_ip = myvars['hostvars'][inventory_hostname]['hammerdb_private_ip']
        else:
            hammerdb_private_ip = terms[0]

        # If no hammerdb found in the inventory file, just return None
        if 'hammerdb' not in variables['groups']:
            return []
        if len(variables['groups']['hammerdb']) == 0:
            return []

        # Lookup for hammerdb servers with a matching private_ip
        for host in variables['groups']['hammerdb']:
            hostvars = myvars['hostvars'][host]

            if hostvars['private_ip'] != hammerdb_private_ip:
                continue

            return [
                dict(
                    node_type='hammerdb',
                    ansible_host=hostvars['ansible_host'],
                    hostname=hostvars.get('hostname', hostvars['ansible_hostname']),
                    private_ip=hostvars['private_ip'],
                    inventory_hostname=hostvars['inventory_hostname']
                )
            ]
