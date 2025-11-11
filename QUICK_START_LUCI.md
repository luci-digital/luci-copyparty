# Luci Digital Quick Start Guide

> Deploy copyparty to your Synology NAS in minutes with Infrastructure as Code

---

## Choose Your Path

### 🎯 Path 1: Terraform/OpenTofu (Best for Production)

**When to use:** Version-controlled infrastructure, teams, production environments

```bash
# 1. Navigate to Terraform directory
cd contrib/iac/terraform

# 2. Copy and edit configuration
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# 3. Initialize and deploy
tofu init
tofu plan    # Preview changes
tofu apply   # Deploy!

# Access: http://YOUR_NAS_IP:3923
```

**Minimum config:**
```hcl
synology_host     = "192.168.1.9"
synology_username = "admin"
synology_password = "your-password"
config_volume     = "/volume2/configs/cpp"
nvme_volume       = "/volume2/media-nvme"
archive_volume    = "/volume1/media-archive"
```

---

### 🤖 Path 2: Ansible (Best for Multiple Devices)

**When to use:** Managing multiple NAS devices, simple deployments

```bash
# 1. Navigate to Ansible directory
cd contrib/iac/ansible

# 2. Copy and edit inventory
cp inventory.ini.example inventory.ini
nano inventory.ini

# 3. Deploy
ansible-playbook -i inventory.ini playbook.yml --ask-pass

# Access: http://YOUR_NAS_IP:3923
```

**Minimum inventory:**
```ini
[synology]
nas1 ansible_host=192.168.1.9 ansible_user=admin
```

---

### 🧠 Path 3: MCP + Claude (Best for Daily Operations)

**When to use:** AI-assisted management, quick tasks, exploration

```bash
# 1. Install MCP server
cd contrib/mcp-synology
pip install -e .

# 2. Configure Claude Desktop
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Minimum config:**
```json
{
  "mcpServers": {
    "copyparty-synology": {
      "command": "python",
      "args": ["-m", "copyparty_mcp_synology.server"],
      "env": {
        "SYNOLOGY_HOST": "192.168.1.9",
        "SYNOLOGY_USERNAME": "admin",
        "SYNOLOGY_PASSWORD": "your-password"
      }
    }
  }
}
```

**Usage:**
```
"Hey Claude, deploy copyparty to /volume2/media-nvme"
"Claude, show me all running containers"
"Restart the copyparty container"
```

---

## Prerequisites Checklist

Before starting, ensure you have:

### On Your Synology NAS
- [ ] **DSM 6.x, 7.1, or 7.2+** installed
- [ ] **Container Manager** (DSM 7.2+) or **Docker** (older) installed
- [ ] **SSH enabled** (Control Panel → Terminal & SNMP)
- [ ] **Admin account** credentials
- [ ] **Shared folders** created:
  - Config folder (e.g., `/volume2/configs/cpp`)
  - Data folder(s) (e.g., `/volume2/media-nvme`)

### On Your Local Machine
- [ ] **Terraform/OpenTofu** (for Path 1)
  ```bash
  brew install opentofu  # macOS
  ```
- [ ] **Ansible** (for Path 2)
  ```bash
  brew install ansible   # macOS
  ```
- [ ] **Python 3.10+** (for Path 3)
  ```bash
  python --version       # Check version
  ```

---

## Common Configurations

### DS923+ with NVMe RAID 1 + HDD

**Optimal setup:**
```yaml
config_volume:   /volume2/configs/cpp       # NVMe - database
nvme_volume:     /volume2/media-nvme        # NVMe - hot data
archive_volume:  /volume1/media-archive     # HDD - cold storage
```

**Why:**
- Config/database on NVMe = 10-50x faster queries
- Hot media on NVMe = 500+ MiB/s transfers
- Archive on HDD = cost-effective bulk storage

### Single Volume Setup

**If you only have one volume:**
```yaml
config_volume:   /volume1/configs/cpp
nvme_volume:     /volume1/media
archive_volume:  /volume1/media
```

### Multi-Volume Setup

**For complex configurations:**
```yaml
config_volume:   /volume2/configs/cpp
nvme_volume:     /volume2/media-hot
archive_volume:  /volume1/media-archive
photos_volume:   /volume3/photos
music_volume:    /volume3/music
```

---

## Docker Image Selection

Choose the right copyparty image for your needs:

| Image | Size | Features | Use Case |
|-------|------|----------|----------|
| `copyparty/min` | 57 MiB | Basic only | Minimal deployments |
| `copyparty/im` | 70 MiB | + Image thumbnails | Photo sharing |
| `copyparty/ac` | 163 MiB | + FFmpeg | **RECOMMENDED** |
| `copyparty/iv` | 211 MiB | + vips (HEIF/AVIF) | Modern image formats |
| `copyparty/dj` | 309 MiB | + BPM detection | Music libraries |

**Default:** `copyparty/ac:latest` (best balance of features/size)

---

## Default Credentials

After deployment, copyparty is accessible at:

```
URL: http://YOUR_NAS_IP:3923
Username: admin
Password: changeme123
```

**⚠️ IMPORTANT:** Change the password immediately!

**How to change:**
1. Edit config file: `/volume2/configs/cpp/copyparty.conf`
2. Find line: `admin: changeme123`
3. Change to: `admin: your_secure_password`
4. Restart container:
   ```bash
   docker restart copyparty
   # or via Terraform: tofu apply
   # or via Ansible: ansible-playbook -i inventory.ini playbook.yml
   ```

---

## Verification Steps

### 1. Check Container Status

**Via Docker:**
```bash
ssh admin@YOUR_NAS_IP
docker ps | grep copyparty
```

**Via Ansible:**
```bash
ansible -i inventory.ini synology -m shell -a "docker ps | grep copyparty"
```

**Via MCP + Claude:**
```
"Claude, show me the copyparty container status"
```

### 2. Test Web Access

```bash
curl http://YOUR_NAS_IP:3923
# Should return HTML
```

### 3. Check Logs

```bash
docker logs copyparty --tail 50
```

### 4. Verify Volumes

```bash
docker inspect copyparty | grep -A 10 Mounts
```

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker logs copyparty
```

**Common issues:**
- Port 3923 already in use → Change `copyparty_port` variable
- Volume paths don't exist → Create them manually
- Permission denied → Check folder permissions

### Can't Connect

**Check firewall:**
```bash
# On Synology
sudo iptables -L | grep 3923
```

**Test from NAS:**
```bash
curl localhost:3923
```

### Terraform Errors

**Provider not found:**
```bash
tofu init -upgrade
```

**State locked:**
```bash
tofu force-unlock LOCK_ID
```

### Ansible Errors

**SSH connection failed:**
```bash
# Test SSH
ssh admin@YOUR_NAS_IP

# Check inventory
ansible -i inventory.ini synology -m ping --ask-pass
```

**Docker module error:**
```bash
# SSH into NAS and install
ssh admin@YOUR_NAS_IP
sudo pip3 install docker
```

### MCP Server Issues

**Can't connect to Synology:**
```bash
# Test API access
curl -k https://YOUR_NAS_IP:5001/webapi/entry.cgi
```

**Claude doesn't see tools:**
- Restart Claude Desktop
- Check config file syntax
- Verify environment variables

---

## Next Steps

### After Initial Deployment

1. **Change default password** (see above)
2. **Configure additional users** in copyparty.conf
3. **Set up backup strategy** for config folder
4. **Enable HTTPS** (optional)
5. **Configure firewall rules** (optional)

### Advanced Features

- **Multi-environment:** Set up dev/staging/prod
- **CI/CD:** Automate deployments with GitHub Actions
- **Monitoring:** Add Prometheus metrics
- **High Availability:** Deploy across multiple NAS
- **Custom plugins:** Extend copyparty functionality

### Learning Resources

- **[Full Enhancement Docs](LUCI_ENHANCEMENTS.md)** - Complete feature breakdown
- **[IaC Comparison](contrib/iac/README.md)** - Choose the right tool
- **[Terraform Deep Dive](contrib/iac/terraform/README.md)** - Advanced usage
- **[Ansible Deep Dive](contrib/iac/ansible/README.md)** - Multi-device patterns
- **[MCP Deep Dive](contrib/mcp-synology/README.md)** - AI operations

---

## Common Commands

### Terraform

```bash
# Preview changes
tofu plan

# Apply changes
tofu apply

# Destroy everything
tofu destroy

# Show current state
tofu show

# Refresh state
tofu refresh
```

### Ansible

```bash
# Test connectivity
ansible -i inventory.ini synology -m ping --ask-pass

# Run playbook
ansible-playbook -i inventory.ini playbook.yml --ask-pass

# Run specific tasks
ansible-playbook -i inventory.ini playbook.yml --tags update

# Dry run
ansible-playbook -i inventory.ini playbook.yml --check
```

### Docker (via SSH)

```bash
# List containers
docker ps

# View logs
docker logs copyparty

# Restart container
docker restart copyparty

# Stop container
docker stop copyparty

# Start container
docker start copyparty

# Remove container
docker rm copyparty
```

### MCP + Claude

```
# Container management
"Show all containers"
"Restart copyparty"
"Check copyparty status"

# System info
"Show system information"
"How much storage is available?"
"List all shared folders"

# Deployment
"Deploy copyparty to /volume2/media"
"Update copyparty to latest version"
```

---

## Getting Help

### Documentation
- **Luci Digital Enhancements**: See [LUCI_ENHANCEMENTS.md](LUCI_ENHANCEMENTS.md)
- **Original copyparty**: See [README.md](README.md)
- **Synology Manual Setup**: See [docs/synology-dsm.md](docs/synology-dsm.md)

### Support Channels
- **IaC Issues**: Open issue in this repository
- **copyparty Issues**: https://github.com/9001/copyparty/issues
- **Synology Help**: https://community.synology.com/

### Community
- **Share configs**: Contribute your deployments
- **Report bugs**: Help improve the tooling
- **Request features**: Tell us what you need

---

<div align="center">

**Quick Start Complete! 🎉**

[View Full Docs](LUCI_ENHANCEMENTS.md) • [Troubleshooting](contrib/iac/README.md) • [Original Project](https://github.com/9001/copyparty)

*Built by Luci Digital on the excellent copyparty by 9001*

</div>
