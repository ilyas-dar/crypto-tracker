#!/bin/bash
# Runs once, as root, when the EC2 instance first boots.
exec > /var/log/user-data.log 2>&1
set -x

dnf update -y
dnf install -y docker git
systemctl enable --now docker
usermod -aG docker ec2-user

# docker compose plugin
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# fetch the project and start everything
sudo -u ec2-user git clone ${github_repo} /home/ec2-user/crypto-tracker
cd /home/ec2-user/crypto-tracker
echo "DOCKERHUB_USER=${dockerhub_user}" > .env
chown ec2-user:ec2-user .env

# pulls the image Jenkins pushed to Docker Hub
docker compose pull || true
docker compose up -d
