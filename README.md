# Crypto Live Tracker: DevOps Project

Flask app that polls CoinGecko, stores prices in SQLite, fires alerts, and exposes Prometheus metrics.
Deployed with Docker, Docker Hub, Jenkins, Terraform, AWS EC2, Prometheus and Grafana.

```
GitHub -> Jenkins (test, build, push) -> Docker Hub -> EC2 (made by Terraform) -> Prometheus -> Grafana
```

## Folder layout
| Path | What it is |
|---|---|
| `app/` | Flask app (fetcher, db, alerts, notifier, metrics, dashboard) |
| `tests/` | Unit tests (API is mocked) |
| `Dockerfile`, `docker-compose.yml` | Container + full stack (app, Prometheus, Grafana, node-exporter) |
| `Jenkinsfile` | CI/CD pipeline |
| `terraform/` | AWS infrastructure as code |
| `monitoring/` | Prometheus config + Grafana datasource and dashboard |

---
## STEP 1: Run locally (no Docker)
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest -q                         # all tests should pass
python -m flask --app wsgi run --port 5000
```
Open http://localhost:5000 and http://localhost:5000/metrics

## STEP 2: GitHub
```bash
git init
git add .
git commit -m "Initial commit: crypto tracker"
git branch -M main
git remote add origin https://github.com/YOUR_USER/crypto-tracker.git
git push -u origin main
```
Make the repo **public** (so the EC2 server can clone it without a token).

## STEP 3: Docker build and run
```bash
docker build -t YOUR_DOCKERHUB_USER/crypto-tracker:latest .
docker run -d -p 5000:5000 --name crypto-app YOUR_DOCKERHUB_USER/crypto-tracker:latest
docker ps
```
Test, then `docker rm -f crypto-app`.

## STEP 4: Docker Hub
```bash
docker login
docker push YOUR_DOCKERHUB_USER/crypto-tracker:latest
```
Also create a Docker Hub **access token** (Account Settings > Security) for Jenkins.

## STEP 5: Full stack locally (app + Prometheus + Grafana)
```bash
cp .env.example .env              # edit DOCKERHUB_USER
docker compose up -d --build
```
- App: http://localhost:5000
- Prometheus: http://localhost:9090 (Status > Targets, all should be UP)
- Grafana: http://localhost:3000 (admin / admin123), dashboard "Crypto Tracker Overview"

## STEP 6: Terraform: create the AWS server
Prerequisites: AWS account, `aws configure` done (IAM user access keys), an SSH key (`ssh-keygen -t rsa -b 4096`).
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # fill in your IP, GitHub URL, Docker Hub user
terraform init
terraform plan
terraform apply
```
Find your public IP at https://checkip.amazonaws.com and write it as `x.x.x.x/32`.
When it finishes, note the outputs (`app_url`, `grafana_url`, `prometheus_url`).
Wait 3 to 5 minutes for the server to install Docker and start the containers.
Check the boot log if needed: `ssh -i ~/.ssh/id_rsa ec2-user@<ip>` then `sudo cat /var/log/user-data.log`.

## STEP 7: Jenkins
1. Install Jenkins (on your laptop, or a second EC2 instance). The `jenkins` user must be able to run Docker:
   `sudo usermod -aG docker jenkins && sudo systemctl restart jenkins`
2. Plugins: Pipeline, Git, Credentials Binding (installed by default with suggested plugins).
3. Add credentials (Manage Jenkins > Credentials):
   - `dockerhub-creds`: Username with password (Docker Hub username + access token)
   - `ec2-ssh-key`: SSH Username with private key (username `ec2-user`, paste your private key)
4. Edit `DOCKERHUB_USER` at the top of the `Jenkinsfile`, commit and push.
5. New Item > Pipeline > "Pipeline script from SCM" > Git > your repo URL > branch `main`.
6. Build with Parameters: paste the EC2 public IP into `EC2_HOST` to also deploy.

## STEP 8: Verify
- App: `http://<EC2_IP>:5000`
- Prometheus targets: `http://<EC2_IP>:9090/targets`
- Grafana: `http://<EC2_IP>:3000`

## STEP 9: Clean up (avoid AWS charges!)
```bash
cd terraform
terraform destroy
```

---
## Screenshot checklist for the report
1. GitHub repo home, file list, commits, Jenkinsfile, Terraform folder
2. Terminal: `pytest -q` passing
3. Terminal: `docker build`, `docker images`, `docker run`, `docker ps`
4. App in browser (localhost) with prices and an alert rule
5. Docker Hub repo page with tags
6. Terminal: `terraform init`, `plan`, `apply` and outputs
7. AWS Console: EC2 instance running, security group, key pair, Elastic IP
8. Jenkins: credentials page, pipeline config, Stage View (all green), Console Output ending in SUCCESS
9. App in browser on the EC2 public IP
10. Prometheus: Targets page (all UP) and a query like `crypto_price`
11. Grafana: data source page and the dashboard with live panels
12. A triggered alert shown in the app and in `docker logs crypto-app`
13. Terminal: `terraform destroy` and the empty EC2 console afterwards

## Useful alert examples
- bitcoin, price above, (a value just under the current price) to test quickly
- ethereum, % change in window, 0.5, 5 minutes
- bitcoin, volume up %, 5, 10 minutes
