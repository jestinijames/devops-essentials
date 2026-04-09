# Module 11 — Vagrant

> **Vagrant creates and configures local virtual machines.** It's the safe practice ground before you touch real cloud servers.

---

## Learning Objectives

- [ ] Understand what Vagrant is and when to use it
- [ ] Install Vagrant and VirtualBox
- [ ] Write a Vagrantfile to define VMs
- [ ] Use Vagrant to practice Ansible (from Module 07)
- [ ] Spin up a multi-VM environment locally

---

## 1. What is Vagrant?

Vagrant is a CLI tool that automates the creation of virtual machines. You write a `Vagrantfile` (Ruby syntax) that describes your VM(s), and Vagrant handles:
- Downloading the OS image (called a "box")
- Creating the VM in VirtualBox (or VMware, Hyper-V)
- Networking, port forwarding
- File syncing between host and guest
- Running provisioning scripts (shell, Ansible, Puppet, Chef)

### Why use Vagrant?

- Practice Ansible on real SSH-able Linux machines **without needing cloud accounts**
- Reproduce complex multi-server setups locally
- Isolate your practice environment — break things safely
- Much cheaper than cloud VMs

### Vagrant vs Docker

| | Vagrant | Docker |
|--|---------|--------|
| **Isolation** | Full VM (separate kernel) | Container (shared kernel) |
| **Boot time** | ~30 seconds | ~1 second |
| **Resource use** | High (GBs of RAM) | Low (MBs) |
| **Best for** | Simulating real servers, Ansible practice | App containerization |

---

## 2. Setup

```bash
# Install VirtualBox (free hypervisor)
# https://www.virtualbox.org/wiki/Downloads

# Install Vagrant
# Windows: choco install vagrant
# Mac:     brew install --cask vagrant

# Verify
vagrant --version
```

---

## 3. Basic Vagrantfile

Create `vagrant/single-vm/Vagrantfile`:

```ruby
Vagrant.configure("2") do |config|
  # Base OS image (Ubuntu 22.04 LTS)
  config.vm.box = "ubuntu/jammy64"
  
  # VM settings
  config.vm.hostname = "devops-vm"
  
  # Port forwarding: host:3000 → guest:3000
  config.vm.network "forwarded_port", guest: 3000, host: 3000
  
  # Private network (for multi-VM communication)
  config.vm.network "private_network", ip: "192.168.56.10"
  
  # Sync a folder: host → guest
  config.vm.synced_folder "../..", "/home/vagrant/devops-essentials"
  
  # VirtualBox settings
  config.vm.provider "virtualbox" do |vb|
    vb.name   = "devops-vm"
    vb.memory = "1024"   # 1 GB RAM
    vb.cpus   = 2
  end
  
  # Shell provisioning (runs on first boot)
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update -q
    apt-get install -y -q curl git
    echo "VM is ready!"
  SHELL
end
```

```bash
cd vagrant/single-vm

# Start the VM (downloads box on first run ~1GB)
vagrant up

# SSH into the VM
vagrant ssh

# Inside the VM:
ls /home/vagrant/devops-essentials  # Your repo is here!
exit

# Run provisioning again
vagrant provision

# Restart the VM
vagrant reload

# Stop the VM
vagrant halt

# Delete the VM (keeps the box)
vagrant destroy

# Check VM status
vagrant status
```

---

## 4. Multi-VM Vagrantfile

This creates a realistic web + DB server setup to practice Ansible:

Create `vagrant/multi-vm/Vagrantfile`:

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  
  # Disable default shared folder
  config.vm.synced_folder ".", "/vagrant", disabled: true
  
  # ── Web Servers ──────────────────────────────────────────────────
  (1..2).each do |i|
    config.vm.define "web-#{i}" do |web|
      web.vm.hostname = "web-#{i}"
      web.vm.network "private_network", ip: "192.168.56.1#{i}"
      
      web.vm.provider "virtualbox" do |vb|
        vb.name   = "web-#{i}"
        vb.memory = "512"
        vb.cpus   = 1
      end
    end
  end
  
  # ── Database Server ──────────────────────────────────────────────
  config.vm.define "db-1" do |db|
    db.vm.hostname = "db-1"
    db.vm.network "private_network", ip: "192.168.56.20"
    
    db.vm.provider "virtualbox" do |vb|
      vb.name   = "db-1"
      vb.memory = "1024"
    end
  end
end
```

```bash
cd vagrant/multi-vm

# Start all VMs
vagrant up

# Start only one VM
vagrant up web-1

# SSH into a specific VM
vagrant ssh web-1
vagrant ssh db-1

# Run Ansible against all VMs
# Update ansible/inventory/vagrant-hosts.ini:
# [web_servers]
# web-1 ansible_host=192.168.56.11 ansible_user=vagrant ansible_password=vagrant
# web-2 ansible_host=192.168.56.12 ansible_user=vagrant ansible_password=vagrant
# [db_servers]
# db-1 ansible_host=192.168.56.20 ansible_user=vagrant ansible_password=vagrant

ansible-playbook -i ../../ansible/inventory/vagrant-hosts.ini \
  ../../ansible/playbooks/setup-docker.yml

# Destroy all VMs
vagrant destroy -f
```

---

## 5. Vagrant + Ansible Provisioning

You can tell Vagrant to automatically run Ansible when creating the VM:

```ruby
config.vm.define "web-1" do |web|
  web.vm.hostname = "web-1"
  web.vm.network "private_network", ip: "192.168.56.11"
  
  # Auto-provision with Ansible on first boot
  web.vm.provision "ansible" do |ansible|
    ansible.playbook = "../../ansible/playbooks/setup-docker.yml"
    ansible.inventory_path = "../../ansible/inventory/vagrant-hosts.ini"
  end
end
```

---

## Checklist

- [ ] VirtualBox and Vagrant installed
- [ ] I can start, stop, and destroy VMs with Vagrant commands
- [ ] I've SSH-ed into a Vagrant VM
- [ ] I've run my Ansible playbook against a Vagrant VM
- [ ] I've set up a multi-VM environment (web + db)

---

**Next:** [Module 12 — Monitoring](../12-monitoring/README.md)
