# Rolling update to targets from inventory plugin

This example runs a rolling update to set of servers. The servers are defined in a Terraform configuration in [resources](./resources) directory and used as target nodes via `server_group` option of the inventory plugin.

To run this example, you will need:

- Terraform
- Ansible
- upcloud-ansible-collection and UpCloud python SDK (`upcloud-api>=2.5.0`)

First configure your credentials to UpCloud Terraform provider and Ansible inventory plugin by setting `UPCLOUD_USERNAME` and `UPCLOUD_PASSWORD` environment variables.

Create the servers defined in the Terraform configuration with `terraform apply` command.

```sh
terraform -chdir=resources init
terraform -chdir=resources apply
# Answer yes, when prompted by Terraform to accept the plan
```

Configure a NGINX server with static web page by running the [configure-webserver.yml](./configure-webserver.yml) playbook.

```sh
# For initial configuration, configure all targets in parallel
ansible-playbook configure-webserver.yml --extra-vars "serial_override=0"

# When updating the targets, specify which tag (cow, dog, hello, or tiger) to use
ansible-playbook configure-webserver.yml --extra-vars "animal=tiger"
```

To monitor how the rolling update proceeds, open another terminal window and curl the load-balancer URL. The URL is visible at the output of prevous `terraform apply` command and can be printed by running `terraform output`.

```sh
watch -n 0.75 curl -s $(terraform -chdir=resources output -raw lb_url)
```

Finally, to cleanup the created cloud resources, run `terraform destroy` in the [resources](./resources) directory.

```sh
terraform -chdir=resources destroy
```
