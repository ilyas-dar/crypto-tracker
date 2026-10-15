output "public_ip" {
  value = aws_eip.app.public_ip
}

output "app_url" {
  value = "http://${aws_eip.app.public_ip}:5000"
}

output "grafana_url" {
  value = "http://${aws_eip.app.public_ip}:3000"
}

output "prometheus_url" {
  value = "http://${aws_eip.app.public_ip}:9090"
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/id_rsa ec2-user@${aws_eip.app.public_ip}"
}
