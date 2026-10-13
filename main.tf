terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "5.100.0" }
  }
}
provider "aws" { region = "ap-south-1" }
variable "operator_cidr" { type = string }
variable "ssh_public_key" { type = string }
variable "lab_name" { default = "vle-789-complete-proof" }
data "aws_caller_identity" "current" {}
data "aws_vpc" "default" { default = true }
data "aws_subnets" "default" {
  filter {
    name = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
data "aws_ami" "ubuntu" {
  most_recent = true
  owners = ["099720109477"]
  filter {
    name = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name = "architecture"
    values = ["x86_64"]
  }
}
resource "aws_security_group" "lab" {
  name = "${var.lab_name}-sg"
  description = "Temporary experiment tools limited to the operator IPv4"
  vpc_id = data.aws_vpc.default.id
  dynamic "ingress" {
    for_each = toset([22,443,3000,7681,8025,8080,8081,8082,8083,9000,9090,9093])
    content {
      from_port = ingress.value
      to_port = ingress.value
      protocol = "tcp"
      cidr_blocks = [var.operator_cidr]
      description = "Lab tool from operator IP only"
    }
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${var.lab_name}-sg", Project = "VLE-7-8-9" }
}
resource "aws_instance" "lab" {
  ami = data.aws_ami.ubuntu.id
  instance_type = "m7i-flex.large"
  subnet_id = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.lab.id]
  associate_public_ip_address = true
  user_data = "#cloud-config\nssh_authorized_keys:\n  - ${var.ssh_public_key}\nwrite_files:\n  - path: /etc/ssh/sshd_config.d/lab.conf\n    content: |\n      Port 22\n      Port 443\nruncmd:\n  - systemctl restart ssh\n"
  user_data_replace_on_change = true
  root_block_device {
    volume_type = "gp3"
    volume_size = 40
    encrypted = true
    delete_on_termination = true
  }
  metadata_options { http_tokens = "required" }
  tags = { Name = var.lab_name, Project = "VLE-7-8-9", Purpose = "complete-live-proof" }
}
output "account_id" { value = data.aws_caller_identity.current.account_id }
output "instance_id" { value = aws_instance.lab.id }
output "public_ip" { value = aws_instance.lab.public_ip }
output "security_group_id" { value = aws_security_group.lab.id }
output "volume_id" { value = aws_instance.lab.root_block_device[0].volume_id }
