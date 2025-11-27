__metaclass__ = type


DOCUMENTATION = r'''
---
module: loadbalancer_backend_member
version_added: "0.9.0"
short_description: Manage UpCloud load balancer backend members
description:
    - Modify UpCloud load balancer backend members.
    - Currently only supports updating the weight of a existing backend member.
options:
    loadbalancer_uuid:
        description:
            - UUID of the load balancer.
        required: true
        type: str
    backend_name:
        description:
            - Name of the backend.
        required: true
        type: str
    member_name:
        description:
            - Name of the backend member.
            - Either O(member_name) or O(ip_address) must be provided.
        required: false
        type: str
    ip_address:
        description:
            - IP address of the backend member.
            - Either O(member_name) or O(ip_address) must be provided.
        required: false
        type: str
    weight:
        description:
            - Weight of the backend member (0-100) relative to other members.
            - All members will receive a load proportional to their weight relative to the sum of all weights, so the higher the weight, the higher the load.
            - A value of 0 means the member will not participate in load balancing but will still accept persistent connections.
        required: true
        type: int

author:
    - UpCloud (@UpCloudLtd)
'''

EXAMPLES = r'''
- name: Disable new connections before starting maintenance
  loadbalancer_backend_member:
    loadbalancer_uuid: your-loadbalancer-uuid
    backend_name: your-backend-name
    member_name: your-member-name
    weight: 0

- name: Enable new connections after maintenance has been completed
  loadbalancer_backend_member:
    loadbalancer_uuid: your-loadbalancer-uuid
    backend_name: your-backend-name
    member_name: your-member-name
    weight: 100
'''

RETURN = r'''
loadbalancer_backend_member:
    description:
        - Loadbalancer backend member details.
    returned: always
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.upcloud.cloud.plugins.module_utils.client import initialize_upcloud_client

try:
    from upcloud_api.errors import UpCloudAPIError
except ImportError:
    pass


class LoadBalancerBackendMember:
    def __init__(self, loadbalancer_uuid=None, backend_name=None, member_name=None, ip_address=None):
        self.client = initialize_upcloud_client()

        self.loadbalancer_uuid = loadbalancer_uuid
        self.backend_name = backend_name
        self.member_name = member_name
        self.ip_address = ip_address
        self.weight = None

        if self.member_name is None and self.ip_address is None:
            raise ValueError('Either member_name or ip_address must be provided.')

        self.details = dict()

    @property
    def _url(self):
        return f'/load-balancer/{self.loadbalancer_uuid}/backends/{self.backend_name}/members/{self.member_name}'

    def _get_by_ip(self):
        members = self.client.api.get_request(f'/load-balancer/{self.loadbalancer_uuid}/backends/{self.backend_name}/members')
        for member in members:
            if member.get('ip_address') == self.ip_address:
                self.member_name = member.get('name')
                return member
        raise ValueError(f'Backend member with IP address {self.ip_address} not found.')

    def read(self):
        if self.member_name is None:
            self.details = self._get_by_ip()
        else:
            self.details = self.client.api.get_request(self._url)
        self.weight = int(self.details.get('weight'))

    def update(self, weight):
        payload = {
            'weight': weight
        }
        self.details = self.client.api.patch_request(self._url, payload)
        self.weight = weight


def main():
    argument_spec = dict(
        loadbalancer_uuid=dict(type='str', required=True),
        backend_name=dict(type='str', required=True),
        member_name=dict(type='str', required=False),
        ip_address=dict(type='str', required=False),
        weight=dict(type='int', required=True),
    )

    result = dict(
        changed=False,
        loadbalancer_backend_member={},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    member = LoadBalancerBackendMember(
        loadbalancer_uuid=module.params.get('loadbalancer_uuid'),
        backend_name=module.params.get('backend_name'),
        member_name=module.params.get('member_name'),
        ip_address=module.params.get('ip_address'),
    )
    try:
        result['loadbalancer_backend_member'] = member.read()
    except (UpCloudAPIError, ValueError) as e:
        module.fail_json(msg=str(e))

    weight = module.params.get('weight')
    if member.weight != weight:
        if not module.check_mode:
            try:
                result['loadbalancer_backend_member'] = member.update(weight)
            except UpCloudAPIError as e:
                module.fail_json(msg=str(e))
        result["changed"] = True
    else:
        result["changed"] = False

    module.exit_json(**result)


if __name__ == '__main__':
    main()
