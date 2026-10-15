variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "crypto-tracker"
}

variable "instance_type" {
  description = "t3.micro / t2.micro are free-tier eligible depending on region"
  type        = string
  default     = "t3.micro"
}

variable "public_key_path" {
  description = "Path to your SSH public key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "my_ip_cidr" {
  description = "Your public IP in CIDR form, e.g. 103.5.6.7/32 (locks SSH, Prometheus, Grafana to you)"
  type        = string
}

variable "github_repo" {
  description = "HTTPS URL of your public GitHub repo"
  type        = string
}

variable "dockerhub_user" {
  description = "Your Docker Hub username"
  type        = string
}
