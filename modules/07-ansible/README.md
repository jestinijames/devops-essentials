# Module 07 — Ansible

> **Terraform creates the server. Ansible configures it.** Once your VM or EC2 instance exists, Ansible SSH-es in and installs Docker, sets up users, writes config files, and starts services — automatically.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand what configuration management is and when to use Ansible
- [ ] Install Ansible and understand its architecture (agentless!)
- [ ] Write Ansible playbooks in YAML
- [ ] Use inventory files to target servers
- [ ] Organize configuration into roles
- [ ] Use Ansible Vault to encrypt secrets

---

## 1. What is Configuration Management?

Terraform provisions the infrastructure (creates the server). But a fresh server needs:
- Docker installed
- Nginx configured
- Users created
- SSL certificates set up
- Firewall rules applied
- App deployed and started

You could SSH in and do all this manually. Or you could write it once in Ansible and run it on 1 server or 1000.

**Ansible is agentless** — it uses SSH to connect to target machines. No software needed on the target. This is its biggest advantage over alternatives like Puppet and Chef (which require agents).

---

## 2. Install Ansible

```bash
# Mac
brew install ansible

# Windows (via WSL — Ansible doesn't run natively on Windows)
sudo apt update && sudo apt install ansible

# Verify
ansible --version
```

---

## 3. Key Concepts

```
Control Node           Managed Nodes
─────────────         ─────────────────────────────
Your laptop    →SSH→   web-server-01 (Ubuntu)
  ansible             web-server-02 (Ubuntu)
                       db-server-01 (Ubuntu)
```

| Term | What it is |
|------|-----------|
| **Control Node** | Machine where Ansible runs (your laptop, CI server) |
| **Managed Node** | Target machine Ansible configures (your servers) |
| **Inventory** | List of managed nodes |
| **Playbook** | YAML file that defines what to do on which hosts |
| **Task** | A single action (install a package, copy a file, restart a service) |
| **Module** | Built-in task type (`apt`, `copy`, `service`, `docker_container`, etc.) |
| **Role** | Reusable, organized collection of tasks |
| **Vault** | Ansible's encrypted secrets manager |

---

## 4. Inventory File

Create `ansible/inventory/hosts.ini`:
```ini
# Groups of servers
[web_servers]
web-01 ansible_host=192.168.1.10 ansible_user=ubuntu
web-02 ansible_host=192.168.1.11 ansible_user=ubuntu

[db_servers]
db-01 ansible_host=192.168.1.20 ansible_user=ubuntu

# A group of groups
[all_servers:children]
web_servers
db_servers

[all_servers:vars]
ansible_ssh_private_key_file=~/.ssh/devops_key
ansible_python_interpreter=/usr/bin/python3
```

For local practice using Vagrant (see Module 11):
```ini
[local_vms]
vm1 ansible_host=192.168.56.10 ansible_user=vagrant ansible_password=vagrant
vm2 ansible_host=192.168.56.11 ansible_user=vagrant ansible_password=vagrant
```

Test connectivity:
```bash
cd ansible
ansible all -i inventory/hosts.ini -m ping
# web-01 | SUCCESS => { "ping": "pong" }
# web-02 | SUCCESS => { "ping": "pong" }
```

---

## 5. Your First Playbook

Create `ansible/playbooks/setup-docker.yml`:
```yaml
---
- name: Install and configure Docker on web servers
  hosts: web_servers        # Target the web_servers group
  become: true              # Run as sudo

  vars:
    docker_users:
      - ubuntu
      - deploy

  tasks:
    # ── Update package cache ──────────────────────────────────────────
    - name: Update apt cache
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600   # Don't update if updated < 1hr ago

    # ── Install prerequisites ─────────────────────────────────────────
    - name: Install required packages
      ansible.builtin.apt:
        name:
          - apt-transport-https
          - ca-certificates
          - curl
          - gnupg
          - lsb-release
        state: present

    # ── Add Docker GPG key ────────────────────────────────────────────
    - name: Add Docker GPG key
      ansible.builtin.apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        state: present

    # ── Add Docker APT repository ─────────────────────────────────────
    - name: Add Docker repository
      ansible.builtin.apt_repository:
        repo: "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
        state: present

    # ── Install Docker ────────────────────────────────────────────────
    - name: Install Docker CE
      ansible.builtin.apt:
        name:
          - docker-ce
          - docker-ce-cli
          - containerd.io
          - docker-compose-plugin
        state: present
        update_cache: true

    # ── Start Docker service ──────────────────────────────────────────
    - name: Start and enable Docker service
      ansible.builtin.service:
        name: docker
        state: started
        enabled: true    # Start on boot

    # ── Add users to docker group ─────────────────────────────────────
    - name: Add users to docker group
      ansible.builtin.user:
        name: "{{ item }}"
        groups: docker
        append: true
      loop: "{{ docker_users }}"

    # ── Verify Docker works ───────────────────────────────────────────
    - name: Verify Docker is running
      ansible.builtin.command: docker --version
      register: docker_version   # Save output to variable

    - name: Print Docker version
      ansible.builtin.debug:
        msg: "Docker installed: {{ docker_version.stdout }}"
```

Run the playbook:
```bash
# Dry run (check mode — doesn't make changes)
ansible-playbook -i inventory/hosts.ini playbooks/setup-docker.yml --check

# Run it for real
ansible-playbook -i inventory/hosts.ini playbooks/setup-docker.yml

# Run with extra verbosity (great for debugging)
ansible-playbook -i inventory/hosts.ini playbooks/setup-docker.yml -v
ansible-playbook -i inventory/hosts.ini playbooks/setup-docker.yml -vvv
```

---

## 6. Deploy the App with Ansible

Create `ansible/playbooks/deploy-app.yml`:
```yaml
---
- name: Deploy Next.js app with Docker
  hosts: web_servers
  become: true

  vars:
    app_image: "{{ dockerhub_username }}/devops-app:{{ app_version | default('latest') }}"
    app_port: 3000
    container_name: devops-app

  tasks:
    - name: Pull the latest Docker image
      community.docker.docker_image:
        name: "{{ app_image }}"
        source: pull

    - name: Remove old container (if exists)
      community.docker.docker_container:
        name: "{{ container_name }}"
        state: absent

    - name: Start new container
      community.docker.docker_container:
        name: "{{ container_name }}"
        image: "{{ app_image }}"
        state: started
        restart_policy: unless-stopped
        ports:
          - "{{ app_port }}:3000"
        env:
          NODE_ENV: production

    - name: Wait for app to be healthy
      ansible.builtin.uri:
        url: "http://localhost:{{ app_port }}"
        status_code: 200
      register: result
      retries: 10
      delay: 3
      until: result.status == 200

    - name: Deployment complete
      ansible.builtin.debug:
        msg: "App deployed successfully at http://{{ inventory_hostname }}:{{ app_port }}"
```

```bash
# Deploy version v0.2.0
ansible-playbook -i inventory/hosts.ini playbooks/deploy-app.yml \
  -e "dockerhub_username=YOUR_USERNAME app_version=v0.2.0"
```

---

## 7. Roles — Organizing Playbooks

As playbooks grow, use **roles** to organize them:

```bash
ansible-galaxy init roles/docker
# Creates:
# roles/docker/
# ├── tasks/main.yml        ← primary task list
# ├── handlers/main.yml     ← handlers (restart service, etc.)
# ├── vars/main.yml         ← role variables
# ├── defaults/main.yml     ← default values
# ├── templates/            ← Jinja2 templates
# ├── files/                ← static files to copy
# └── meta/main.yml         ← metadata (author, dependencies)
```

Use the role in a playbook:
```yaml
---
- name: Configure web servers
  hosts: web_servers
  become: true
  roles:
    - docker
    - nginx
    - app-deploy
```

---

## 8. Ansible Vault — Encrypting Secrets

```bash
# Create an encrypted secrets file
ansible-vault create ansible/vars/secrets.yml
# Enter vault password when prompted, then write:
# dockerhub_password: mysecretpassword
# db_root_password: anotherpassword

# View encrypted file
ansible-vault view ansible/vars/secrets.yml

# Edit encrypted file
ansible-vault edit ansible/vars/secrets.yml

# Encrypt an existing file
ansible-vault encrypt ansible/vars/secrets.yml

# Use the vault in a playbook
ansible-playbook deploy-app.yml --vault-password-file ~/.vault_pass
# OR
ansible-playbook deploy-app.yml --ask-vault-pass
```

In the playbook:
```yaml
- name: Deploy app
  hosts: web_servers
  vars_files:
    - ../vars/secrets.yml    # Decrypted at runtime
```

---

## Checklist

- [ ] I understand when to use Ansible vs Terraform
- [ ] I can write a playbook with tasks, variables, and loops
- [ ] I understand the `become: true` (sudo) concept
- [ ] I can use `register` to capture command output
- [ ] I've organized tasks into a role
- [ ] I can encrypt secrets with Ansible Vault
- [ ] My deploy playbook runs the Docker container and checks health

---

**Next:** [Module 08 — GitOps](../08-gitops/README.md)
