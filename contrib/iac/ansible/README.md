# Ansible Playbook for Synology copyparty Deployment

Automate the deployment and configuration of copyparty on Synology NAS using Ansible.

## Features

- **Automated Deployment**: One command to deploy copyparty
- **Idempotent**: Safe to run multiple times
- **Multi-Host Support**: Deploy to multiple Synology devices
- **Configuration Management**: Version control your NAS configuration
- **Dependency Handling**: Automatically installs required packages

## Prerequisites

### On Your Local Machine

1. **Ansible** installed:

```bash
# macOS
brew install ansible

# Linux (Debian/Ubuntu)
sudo apt update && sudo apt install ansible

# Linux (RHEL/Fedora)
sudo dnf install ansible

# Python pip
pip3 install ansible
```

2. **SSH client** installed (usually pre-installed)

### On Your Synology NAS

1. **Enable SSH**:
   - Control Panel → Terminal & SNMP
   - Enable "Enable SSH service"
   - Port: 22 (default)

2. **Install Container Manager** (DSM 7.2+) or **Docker** (older versions):
   - Package Center → Search for "Container Manager" or "Docker"
   - Install

3. **Test SSH access**:
   ```bash
   ssh admin@192.168.1.9
   ```

## Quick Start

### 1. Configure Inventory

Copy and edit the inventory file:

```bash
cp inventory.ini.example inventory.ini
nano inventory.ini
```

Update with your Synology details:

```ini
[synology]
ds923plus ansible_host=192.168.1.9 ansible_user=admin
```

### 2. Configure Variables

Edit the group variables to match your setup:

```bash
nano group_vars/synology.yml
```

Key settings:

```yaml
# Docker image
copyparty_image: "copyparty/ac:latest"

# Volume paths (adjust for your NAS)
config_volume: "/volume2/configs/cpp"
nvme_volume: "/volume2/media-nvme"
archive_volume: "/volume1/media-archive"

# User/Group IDs
puid: "1000"
pgid: "100"
```

### 3. Test Connectivity

```bash
ansible -i inventory.ini synology -m ping --ask-pass
```

Enter your Synology password when prompted.

### 4. Run the Playbook

```bash
ansible-playbook -i inventory.ini playbook.yml --ask-pass
```

Enter your Synology password when prompted.

### 5. Access copyparty

After deployment completes:

```
http://YOUR_SYNOLOGY_IP:3923
```

**Default credentials**: admin / changeme123
**IMPORTANT**: Change the password immediately!

## Configuration

### Docker Image Variants

Edit `group_vars/synology.yml`:

```yaml
copyparty_image: "copyparty/ac:latest"  # Recommended
```

**Available images**:
- `copyparty/min` (57 MiB): Basic only
- `copyparty/im` (70 MiB): + Image thumbnails + media tags
- `copyparty/ac` (163 MiB): + FFmpeg for video/audio **← RECOMMENDED**
- `copyparty/iv` (211 MiB): + vips for faster HEIF/AVIF/JXL
- `copyparty/dj` (309 MiB): + BPM and musical key detection

### Volume Configuration

**DS923+ with NVMe RAID 1 + HDD**:

```yaml
config_volume: "/volume2/configs/cpp"       # NVMe
nvme_volume: "/volume2/media-nvme"          # NVMe
archive_volume: "/volume1/media-archive"    # HDD
```

**Single volume setup**:

```yaml
config_volume: "/volume1/configs/cpp"
nvme_volume: "/volume1/media"
archive_volume: "/volume1/media"
```

### Custom copyparty Config

The playbook creates a default config if none exists. To use your own:

1. Create `{{ config_volume }}/copyparty.conf` before running
2. Or replace the config after deployment
3. Restart the container: `docker restart copyparty`

## Common Tasks

### Deploy to Multiple NAS Devices

Add multiple hosts to `inventory.ini`:

```ini
[synology]
nas1 ansible_host=192.168.1.9 ansible_user=admin
nas2 ansible_host=192.168.1.10 ansible_user=admin
office-nas ansible_host=10.0.0.50 ansible_user=admin

[home-nas]
nas1
nas2

[office-nas-group]
office-nas
```

Deploy to specific groups:

```bash
# Deploy to all
ansible-playbook -i inventory.ini playbook.yml --ask-pass

# Deploy to home NAS only
ansible-playbook -i inventory.ini playbook.yml --ask-pass --limit home-nas
```

### Update copyparty

```bash
# Pull latest image and restart container
ansible-playbook -i inventory.ini playbook.yml --ask-pass --tags update
```

### Check Deployment Status

```bash
ansible -i inventory.ini synology -m shell -a "docker ps | grep copyparty" --ask-pass
```

### View Container Logs

```bash
ansible -i inventory.ini synology -m shell -a "docker logs copyparty --tail 50" --ask-pass
```

### Restart Container

```bash
ansible -i inventory.ini synology -m shell -a "docker restart copyparty" --ask-pass
```

### Remove Deployment

```bash
ansible-playbook -i inventory.ini playbook.yml --ask-pass --tags remove
```

## Using SSH Keys (Recommended)

Instead of typing passwords, use SSH keys:

### 1. Generate SSH key (if you don't have one)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### 2. Copy key to Synology

```bash
ssh-copy-id admin@192.168.1.9
```

### 3. Remove `--ask-pass` from commands

```bash
ansible-playbook -i inventory.ini playbook.yml
```

## Advanced Usage

### Custom Playbook for Additional Tasks

Create `custom-tasks.yml`:

```yaml
---
- name: Custom copyparty configuration
  hosts: synology
  vars_files:
    - group_vars/synology.yml

  tasks:
    - name: Copy custom plugins
      copy:
        src: plugins/
        dest: "{{ config_volume }}/plugins/"
        mode: '0644'
      become: yes

    - name: Restart copyparty to load plugins
      docker_container:
        name: "{{ copyparty_container_name }}"
        state: started
        restart: yes
```

Run it:

```bash
ansible-playbook -i inventory.ini custom-tasks.yml --ask-pass
```

### Vault for Sensitive Data

Encrypt sensitive variables:

```bash
# Create encrypted file
ansible-vault create group_vars/secrets.yml
```

Add sensitive data:

```yaml
---
synology_admin_password: "your_secure_password"
copyparty_admin_password: "another_secure_password"
```

Use in playbook:

```bash
ansible-playbook -i inventory.ini playbook.yml --ask-vault-pass
```

### Dynamic Inventory

For larger deployments, use dynamic inventory:

```python
#!/usr/bin/env python3
# inventory.py
import json

inventory = {
    "synology": {
        "hosts": ["nas1", "nas2"],
        "vars": {
            "ansible_user": "admin"
        }
    },
    "_meta": {
        "hostvars": {
            "nas1": {"ansible_host": "192.168.1.9"},
            "nas2": {"ansible_host": "192.168.1.10"}
        }
    }
}

print(json.dumps(inventory))
```

```bash
chmod +x inventory.py
ansible-playbook -i inventory.py playbook.yml --ask-pass
```

### Integration with AWX/Tower

Import this playbook into AWX for:
- Web UI management
- Scheduled deployments
- RBAC and audit logging
- REST API access

## Troubleshooting

### "Python not found" Error

SSH into your Synology and check Python:

```bash
ssh admin@192.168.1.9
which python3
# Should output: /usr/bin/python3
```

If not found, you may need to install Python via Package Manager.

### "Permission Denied" Errors

Try with become (sudo):

```bash
ansible-playbook -i inventory.ini playbook.yml --ask-pass --ask-become-pass
```

### Docker Python Module Error

The playbook automatically installs it, but if it fails:

```bash
ssh admin@192.168.1.9
sudo pip3 install docker
```

### Container Fails to Start

Check logs:

```bash
ansible -i inventory.ini synology -m shell -a "docker logs copyparty" --ask-pass
```

Common issues:
- Port 3923 already in use
- Volume paths don't exist
- Insufficient permissions

### Ansible Connection Timeout

Increase timeout in `ansible.cfg`:

```ini
[defaults]
timeout = 30
```

## Best Practices

1. **Use SSH Keys**: More secure and convenient than passwords
2. **Version Control**: Store playbooks in Git (exclude `inventory.ini` with secrets)
3. **Test First**: Use `--check` mode to preview changes:
   ```bash
   ansible-playbook -i inventory.ini playbook.yml --check
   ```
4. **Backup Config**: Before making changes, backup your config:
   ```bash
   ansible -i inventory.ini synology -m fetch \
     -a "src={{ config_volume }}/copyparty.conf dest=backup/"
   ```
5. **Use Vault**: Encrypt sensitive data with ansible-vault
6. **Tags**: Use tags for selective execution:
   ```yaml
   - name: Update container
     docker_container:
       # ...
     tags: [update]
   ```

## Example Workflows

### Initial Setup Workflow

```bash
# 1. Test connectivity
ansible -i inventory.ini synology -m ping --ask-pass

# 2. Preview changes
ansible-playbook -i inventory.ini playbook.yml --ask-pass --check

# 3. Deploy
ansible-playbook -i inventory.ini playbook.yml --ask-pass

# 4. Verify
ansible -i inventory.ini synology -m shell -a "docker ps" --ask-pass
```

### Update Workflow

```bash
# 1. Backup current config
ansible -i inventory.ini synology -m fetch \
  -a "src=/volume2/configs/cpp/copyparty.conf dest=backup/" --ask-pass

# 2. Update image and restart
ansible-playbook -i inventory.ini playbook.yml --ask-pass

# 3. Test
curl http://192.168.1.9:3923
```

### Multi-Environment Workflow

```bash
# Deploy to dev
ansible-playbook -i inventory-dev.ini playbook.yml --ask-pass

# Test dev
# ... testing ...

# Deploy to prod
ansible-playbook -i inventory-prod.ini playbook.yml --ask-pass
```

## Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [Docker Ansible Module](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_container_module.html)
- [copyparty Documentation](https://github.com/9001/copyparty)
- [Synology Developer Guide](https://global.download.synology.com/download/Document/Software/DeveloperGuide/)

## Support

For issues with:
- **Ansible**: Check Ansible documentation or community forums
- **copyparty**: See the main copyparty repository
- **Synology**: Consult Synology support documentation
