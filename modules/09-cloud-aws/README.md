# Module 09 — Cloud: AWS (Free Tier)

> **AWS is the world's largest cloud provider.** Learning it opens doors everywhere. We'll use only the free tier — everything here costs $0.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand core AWS services relevant to DevOps
- [ ] Set up an AWS account and configure the CLI
- [ ] Deploy the Next.js app to EC2 (free tier)
- [ ] Store Docker images in ECR (Elastic Container Registry)
- [ ] Deploy with ECS (Elastic Container Service)
- [ ] Use S3 for static assets
- [ ] Use Terraform to provision AWS resources

---

## 1. AWS Free Tier Overview

AWS gives you 12 months of free tier access after sign-up, plus some services that are always free.

| Service | Free Tier | What it does |
|---------|-----------|-------------|
| **EC2** | 750 hrs/month t2.micro | Virtual server (Linux) |
| **S3** | 5 GB storage | Object storage (files, images, backups) |
| **RDS** | 750 hrs/month db.t3.micro | Managed database (Postgres, MySQL) |
| **ECR** | 500 MB/month | Docker image registry |
| **ECS** | Free (pay for underlying EC2) | Container management on EC2 |
| **Lambda** | 1M requests/month (always free) | Serverless functions |
| **CloudFront** | 1 TB data transfer/month | CDN |

> **Sign up:** https://aws.amazon.com/free/ — requires a credit card but won't charge if you stay within free tier.

---

## 2. AWS CLI Setup

```bash
# Install AWS CLI v2
# Windows: https://awscli.amazonaws.com/AWSCLIV2.msi
# Mac: brew install awscli

aws --version

# Configure with your credentials
aws configure
# AWS Access Key ID: (from IAM → Users → Security Credentials)
# AWS Secret Access Key: (only shown once — save it!)
# Default region: us-east-1
# Default output format: json
```

### Create an IAM User (never use root account for CLI)
1. AWS Console → IAM → Users → Create User
2. Attach policy: `AdministratorAccess` (for learning — restrict in production)
3. Security Credentials → Create Access Key → CLI
4. Copy the key and secret

```bash
# Test the CLI works
aws sts get-caller-identity
# {
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/devops-user"
# }

# List your S3 buckets
aws s3 ls
```

---

## 3. Core AWS Concepts

| AWS Term | What it is | Equivalent |
|----------|-----------|-----------|
| **Region** | Geographic area (us-east-1, eu-west-1) | Data center location |
| **AZ (Availability Zone)** | Isolated data centers within a region | Separate buildings |
| **VPC** | Virtual Private Cloud — your isolated network | Your private network |
| **Security Group** | Firewall rules for EC2/RDS | Firewall |
| **IAM** | Identity and Access Management | Users and permissions |
| **EC2** | Elastic Compute Cloud — virtual servers | Your Linux server |
| **S3** | Simple Storage Service — object storage | Hard drive for files |
| **ECS** | Elastic Container Service | Docker host manager |
| **EKS** | Elastic Kubernetes Service | Managed Kubernetes |
| **RDS** | Relational Database Service — managed DBs | Managed Postgres/MySQL |
| **ECR** | Elastic Container Registry | Docker Hub, but AWS |
| **CloudWatch** | Monitoring and logging | Grafana + logs |
| **Route 53** | DNS service | Domain name routing |

---

## 4. Deploy to EC2 (Terraform + Ansible)

Create `terraform/aws/main.tf`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "key_name" {
  description = "Name of your EC2 key pair"
}

# ── Security Group ──────────────────────────────────────────────────
resource "aws_security_group" "app_sg" {
  name        = "devops-app-sg"
  description = "Allow HTTP and SSH traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # Restrict to your IP in production!
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "devops-app-sg" }
}

# ── EC2 Instance (free tier: t2.micro) ──────────────────────────────
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical (Ubuntu)

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type         = "t2.micro"   # Free tier!
  key_name              = var.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  tags = {
    Name      = "devops-app-server"
    ManagedBy = "terraform"
  }
}

# ── Outputs ──────────────────────────────────────────────────────────
output "public_ip" {
  value = aws_instance.app_server.public_ip
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.app_server.public_ip}"
}
```

```bash
# Create an EC2 key pair first
aws ec2 create-key-pair --key-name devops-key --query 'KeyMaterial' --output text > ~/.ssh/devops-key.pem
chmod 400 ~/.ssh/devops-key.pem

# Deploy
cd terraform/aws
terraform init
terraform plan -var="key_name=devops-key"
terraform apply -var="key_name=devops-key"

# SSH in
ssh -i ~/.ssh/devops-key.pem ubuntu@$(terraform output -raw public_ip)

# Then run Ansible to configure it!
ansible-playbook -i "$(terraform output -raw public_ip)," \
  ansible/playbooks/setup-docker.yml \
  -u ubuntu \
  --private-key ~/.ssh/devops-key.pem

# Deploy the app
ansible-playbook -i "$(terraform output -raw public_ip)," \
  ansible/playbooks/deploy-app.yml \
  -u ubuntu \
  --private-key ~/.ssh/devops-key.pem \
  -e "dockerhub_username=YOUR_USERNAME"

# Clean up when done (to avoid charges!)
terraform destroy -var="key_name=devops-key"
```

---

## 5. Push Docker Images to ECR

```bash
# Create an ECR repository
aws ecr create-repository --repository-name devops-app --region us-east-1

# Get the registry URI
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
ECR_URI=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/devops-app

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

# Tag and push
docker tag my-app:prod $ECR_URI:latest
docker push $ECR_URI:latest
```

In GitHub Actions, use the `aws-actions/amazon-ecr-login` action:
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build and push to ECR
  run: |
    docker build -t ${{ steps.login-ecr.outputs.registry }}/devops-app:${{ github.sha }} ./app
    docker push ${{ steps.login-ecr.outputs.registry }}/devops-app:${{ github.sha }}
```

---

## 6. S3 for Static Assets

```bash
# Create an S3 bucket
aws s3 mb s3://devops-essentials-YOUR_NAME --region us-east-1

# Upload a file
aws s3 cp app/public/favicon.ico s3://devops-essentials-YOUR_NAME/

# Upload a directory
aws s3 sync app/public/ s3://devops-essentials-YOUR_NAME/public/

# List contents
aws s3 ls s3://devops-essentials-YOUR_NAME/

# Enable static website hosting
aws s3 website s3://devops-essentials-YOUR_NAME/ --index-document index.html

# Clean up
aws s3 rm s3://devops-essentials-YOUR_NAME/ --recursive
aws s3 rb s3://devops-essentials-YOUR_NAME/
```

---

## Checklist

- [ ] AWS account created and CLI configured
- [ ] I know the 10 core AWS services
- [ ] I've provisioned an EC2 instance with Terraform
- [ ] I've deployed the Docker container with Ansible
- [ ] I've pushed a Docker image to ECR
- [ ] I've uploaded files to S3
- [ ] I've destroyed all resources when done (no surprise bills!)

---

**Next:** [Module 10 — Cloud (GCP)](../10-cloud-gcp/README.md)
