terraform {
  required_providers {
    upcloud = {
      source  = "UpCloudLtd/upcloud"
      version = "~> 2.4"
    }
  }
}

variable "prefix" {
  type    = string
  default = "ansible-inventory-example-"
}

variable "zone" {
  type    = string
  default = "pl-waw1"
}

locals {
  publickey_filename = one(fileset(pathexpand("~/.ssh/"), "*.pub"))
  publickey          = file("~/.ssh/${local.publickey_filename}")
}

resource "upcloud_network" "network" {
  name = "${var.prefix}net"
  zone = var.zone

  ip_network {
    family  = "IPv4"
    address = "10.100.1.0/24"
    dhcp    = true
  }
}

resource "upcloud_server" "webservers" {
  count    = 3
  hostname = "${var.prefix}server-${count.index}"
  title    = "${var.prefix}server-${count.index}"
  zone     = var.zone
  plan     = "1xCPU-1GB"

  metadata = true

  login {
    user = "admin"
    keys = [
      local.publickey,
    ]
  }
  template {
    storage = "Ubuntu Server 22.04 LTS (Jammy Jellyfish)"
    size    = 25
    title   = "${var.prefix}storage-${count.index}"
  }

  # In production, the public interface should be (in most cases) omitted:
  # - Use a jump-host in the same network to control the application nodes.
  # - Use a NAT gateway to provide internet access for the application nodes.
  network_interface {
    type = "public"
  }

  network_interface {
    type = "utility"
  }

  network_interface {
    type    = "private"
    network = upcloud_network.network.id
  }
}

resource "upcloud_server_group" "webservers" {
  title = "${var.prefix}servergroup"
  anti_affinity_policy = "yes"
  members = upcloud_server.webservers[*].id
}

module "load_balancer" {
  source = "UpCloudLtd/basic-loadbalancer/upcloud"

  name                = "${var.prefix}lb"
  zone                = var.zone
  network             = upcloud_network.network.id
  backend_servers     = [for v in upcloud_server.webservers : v.network_interface.2.ip_address]
  backend_server_port = 80

  frontend_port = 80
}

output "lb_url" {
  value = module.load_balancer.dns_name
}
