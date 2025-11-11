# Infrastructure as Code (IaC) for copyparty on Synology NAS

Comprehensive Infrastructure as Code solutions for deploying and managing copyparty on Synology NAS devices.

## Overview

This directory contains multiple IaC tools and frameworks for deploying copyparty to Synology NAS:

| Tool | Best For | Learning Curve | State Management |
|------|----------|----------------|------------------|
| [Terraform/OpenTofu](terraform/) | Declarative infrastructure, version control | Medium | Yes ✅ |
| [Ansible](ansible/) | Multi-system automation, orchestration | Low-Medium | No |
| [MCP Server](../mcp-synology/) | AI-assisted management with Claude | Low | N/A |

## Quick Comparison

### Terraform/OpenTofu

**Pros**:
- ✅ True declarative infrastructure
- ✅ State tracking and drift detection
- ✅ Plan before apply (preview changes)
- ✅ Works with both Terraform and OpenTofu
- ✅ Integration with CI/CD pipelines

**Cons**:
- ⚠️ Requires learning HCL syntax
- ⚠️ State file management needed
- ⚠️ Synology provider has limited features

**Use when**: You want version-controlled, reproducible infrastructure with state management.

### Ansible

**Pros**:
- ✅ Easy to learn (YAML)
- ✅ Great for multi-system deployments
- ✅ Rich ecosystem of modules
- ✅ Agentless (SSH-based)
- ✅ Powerful for orchestration

**Cons**:
- ⚠️ No native state management
- ⚠️ Slower than Terraform for large deployments
- ⚠️ Can be verbose for complex logic

**Use when**: You have multiple Synology devices or need complex orchestration workflows.

### MCP Server

**Pros**:
- ✅ Natural language interface via Claude
- ✅ No learning curve (AI-assisted)
- ✅ Real-time interaction
- ✅ Great for ad-hoc tasks
- ✅ Combines with Claude's reasoning

**Cons**:
- ⚠️ Requires Claude Desktop or Code
- ⚠️ Not suitable for automation
- ⚠️ Experimental technology

**Use when**: You want AI-assisted management and prefer natural language over code.

## Getting Started

### 1. Choose Your Tool

**New to IaC?** Start with [Ansible](ansible/) - it's the easiest to learn.

**Want reproducible infrastructure?** Use [Terraform/OpenTofu](terraform/).

**Want AI assistance?** Try the [MCP Server](../mcp-synology/) with Claude Desktop.

**Need all three?** They complement each other! Use Terraform for infrastructure, Ansible for configuration, and MCP for interactive management.

### 2. Prerequisites

All tools require:
- Synology NAS with DSM 6.x, 7.1, or 7.2+
- SSH access enabled
- Admin credentials
- Container Manager (DSM 7.2+) or Docker installed

### 3. Install Tools

#### Terraform/OpenTofu

```bash
# macOS
brew install opentofu

# Linux
curl -fsSL https://get.opentofu.org/install-opentofu.sh | sh
```

[Full Terraform/OpenTofu setup →](terraform/README.md)

#### Ansible

```bash
# macOS
brew install ansible

# Linux (Debian/Ubuntu)
sudo apt install ansible

# Python
pip install ansible
```

[Full Ansible setup →](ansible/README.md)

#### MCP Server

```bash
cd contrib/mcp-synology
pip install -e .
```

[Full MCP setup →](../mcp-synology/README.md)

## Example Workflows

### Workflow 1: Initial Deployment with Terraform

```bash
cd contrib/iac/terraform

# Configure
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# Deploy
tofu init
tofu plan
tofu apply
```

**Result**: copyparty deployed with tracked state, easy to update or destroy.

### Workflow 2: Multi-NAS Deployment with Ansible

```bash
cd contrib/iac/ansible

# Configure inventory
nano inventory.ini

# Add multiple NAS devices
# [synology]
# nas1 ansible_host=192.168.1.9
# nas2 ansible_host=192.168.1.10
# office-nas ansible_host=10.0.0.50

# Deploy to all
ansible-playbook -i inventory.ini playbook.yml --ask-pass
```

**Result**: Consistent copyparty deployment across all your NAS devices.

### Workflow 3: Interactive Management with MCP

```bash
# Configure Claude Desktop with MCP server
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Then in Claude Desktop:
User: "Show me all containers on my Synology"
Claude: [uses MCP to list containers]

User: "Deploy copyparty to /volume2/media-nvme"
Claude: [uses MCP to deploy copyparty]
```

**Result**: Natural language infrastructure management.

### Workflow 4: Combined Approach (Recommended)

1. **Initial deployment**: Use Terraform for reproducible infrastructure
2. **Configuration management**: Use Ansible for complex config updates
3. **Daily operations**: Use MCP with Claude for quick tasks

```bash
# 1. Deploy with Terraform
cd contrib/iac/terraform && tofu apply

# 2. Configure with Ansible
cd contrib/iac/ansible && ansible-playbook -i inventory.ini playbook.yml

# 3. Manage with Claude + MCP
# "Hey Claude, restart my copyparty container"
```

## Use Cases

### Personal Home NAS

**Recommended**: Ansible or MCP Server

- Simple setup, single device
- Manual updates are fine
- Natural language management is convenient

### Home Lab with Multiple NAS

**Recommended**: Ansible + Terraform

- Multiple devices need consistency
- Ansible handles orchestration well
- Terraform tracks infrastructure state

### Production Environment

**Recommended**: Terraform + CI/CD

- Need reproducible deployments
- Version control is critical
- Automated testing and rollback
- State management essential

### Development/Testing

**Recommended**: MCP Server + Terraform

- Rapid iteration with Claude
- Terraform for clean environments
- Easy to tear down and rebuild

## Advanced Topics

### Multi-Environment Setup

```
iac/
├── terraform/
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── modules/
│       └── copyparty/
├── ansible/
│   ├── inventories/
│   │   ├── dev.ini
│   │   ├── staging.ini
│   │   └── prod.ini
│   └── playbooks/
└── mcp-synology/
    └── configs/
        └── dev-config.json
```

### CI/CD Integration

#### GitHub Actions with Terraform

```yaml
name: Deploy copyparty
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: opentofu/setup-opentofu@v1
      - name: Deploy
        env:
          TF_VAR_synology_username: ${{ secrets.SYNOLOGY_USER }}
          TF_VAR_synology_password: ${{ secrets.SYNOLOGY_PASS }}
        run: |
          cd contrib/iac/terraform
          tofu init
          tofu apply -auto-approve
```

#### GitHub Actions with Ansible

```yaml
name: Deploy with Ansible
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Ansible
        run: pip install ansible
      - name: Deploy
        env:
          ANSIBLE_HOST_KEY_CHECKING: False
        run: |
          cd contrib/iac/ansible
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > key.pem
          chmod 600 key.pem
          ansible-playbook -i inventory.ini playbook.yml \
            --private-key=key.pem
```

### Secrets Management

#### Using 1Password

```bash
# Terraform
export TF_VAR_synology_password=$(op read "op://Private/Synology/password")
tofu apply

# Ansible
export ANSIBLE_VAULT_PASSWORD=$(op read "op://Private/Ansible/vault-password")
ansible-playbook --vault-password-file=<(echo $ANSIBLE_VAULT_PASSWORD) playbook.yml
```

#### Using HashiCorp Vault

```hcl
# Terraform
data "vault_generic_secret" "synology" {
  path = "secret/synology"
}

provider "synology" {
  username = data.vault_generic_secret.synology.data["username"]
  password = data.vault_generic_secret.synology.data["password"]
}
```

### Backup and Disaster Recovery

#### Terraform State Backup

```bash
# Backup state
cp terraform.tfstate terraform.tfstate.backup

# Use remote state for safety
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "synology/copyparty/terraform.tfstate"
  }
}
```

#### Ansible Configuration Backup

```yaml
- name: Backup copyparty config
  hosts: synology
  tasks:
    - name: Fetch config
      fetch:
        src: /volume2/configs/cpp/copyparty.conf
        dest: backups/{{ inventory_hostname }}/
        flat: yes
```

## Troubleshooting

### Common Issues

#### SSH Connection Failures

```bash
# Test SSH
ssh admin@192.168.1.9

# Check SSH config
cat ~/.ssh/config
```

#### Permission Denied

```bash
# Ensure user has admin privileges
# Try with sudo/become
ansible-playbook -i inventory.ini playbook.yml --ask-become-pass
```

#### Provider/Module Not Found

```bash
# Terraform
tofu init -upgrade

# Ansible
ansible-galaxy collection install community.docker
```

### Getting Help

- **Terraform**: [Synology Provider Issues](https://github.com/synology-community/terraform-provider-synology/issues)
- **Ansible**: [Ansible Community Forum](https://forum.ansible.com/)
- **MCP Server**: [copyparty Issues](https://github.com/9001/copyparty/issues)
- **copyparty**: [Main Repository](https://github.com/9001/copyparty)

## Contributing

Contributions welcome! To add a new IaC tool or improve existing ones:

1. Fork the repository
2. Create a feature branch
3. Add your tool in a new subdirectory
4. Include comprehensive README
5. Add examples and tests
6. Submit a pull request

## Resources

### Documentation

- [Synology DSM API Guide](https://global.download.synology.com/download/Document/Software/DeveloperGuide/)
- [Terraform Synology Provider](https://registry.terraform.io/providers/synology-community/synology/latest/docs)
- [Ansible Docker Module](https://docs.ansible.com/ansible/latest/collections/community/docker/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

### Community

- [copyparty GitHub](https://github.com/9001/copyparty)
- [Synology Community](https://community.synology.com/)
- [r/synology](https://reddit.com/r/synology)

## License

All IaC configurations are provided under the same license as copyparty.

## Acknowledgments

- **Synology** for providing comprehensive APIs
- **synology-community** for the Terraform provider
- **Ansible** community for Docker modules
- **Anthropic** for the Model Context Protocol
- **copyparty** community for feedback and contributions
