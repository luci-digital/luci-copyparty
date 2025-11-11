# Terraform/OpenTofu for Synology copyparty Deployment

Infrastructure as Code for deploying copyparty on Synology NAS using Docker containers.

## Features

- **Declarative Infrastructure**: Define your entire copyparty deployment as code
- **Version Control**: Track changes to your infrastructure over time
- **Reproducible**: Deploy the same configuration across multiple Synology devices
- **State Management**: Terraform/OpenTofu tracks what's deployed and can detect drift
- **OpenTofu Compatible**: Works with both Terraform and OpenTofu (recommended)

## Prerequisites

1. **Synology NAS** with DSM 6.x, 7.1, or 7.2+
2. **Container Manager** (DSM 7.2+) or **Docker** (older versions) installed
3. **SSH Access** enabled on Synology (Control Panel → Terminal & SNMP)
4. **Terraform** or **OpenTofu** installed on your local machine:

### Install OpenTofu (Recommended)

```bash
# macOS
brew install opentofu

# Linux (Debian/Ubuntu)
curl -fsSL https://get.opentofu.org/install-opentofu.sh | sh

# Linux (manual)
wget https://github.com/opentofu/opentofu/releases/latest/download/tofu_linux_amd64.tar.gz
tar -xzf tofu_linux_amd64.tar.gz
sudo mv tofu /usr/local/bin/
```

### Or Install Terraform

```bash
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/latest/terraform_linux_amd64.zip
unzip terraform_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

## Quick Start

### 1. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Edit `terraform.tfvars` with your Synology details:

```hcl
synology_host     = "192.168.1.9"
synology_username = "admin"
synology_password = "your-password"

config_volume  = "/volume2/configs/cpp"
nvme_volume    = "/volume2/media-nvme"
archive_volume = "/volume1/media-archive"
```

**Important**: Never commit `terraform.tfvars` to version control (it's in .gitignore)

### 2. Initialize Terraform/OpenTofu

```bash
# Using OpenTofu
tofu init

# Or using Terraform
terraform init
```

This downloads the Synology provider plugin.

### 3. Preview Changes

```bash
# Using OpenTofu
tofu plan

# Or using Terraform
terraform plan
```

Review what will be created/changed.

### 4. Deploy copyparty

```bash
# Using OpenTofu
tofu apply

# Or using Terraform
terraform apply
```

Type `yes` when prompted.

### 5. Access copyparty

After deployment completes, access copyparty at:

```
http://YOUR_SYNOLOGY_IP:3923
```

## Configuration Options

### Docker Image Variants

Choose the right image for your needs (in `terraform.tfvars`):

```hcl
copyparty_image = "copyparty/ac:latest"  # Recommended
```

**Available images**:
- `copyparty/min` (57 MiB): Basic only
- `copyparty/im` (70 MiB): + Image thumbnails + media tags
- `copyparty/ac` (163 MiB): + FFmpeg for video/audio **← RECOMMENDED**
- `copyparty/iv` (211 MiB): + vips for faster HEIF/AVIF/JXL
- `copyparty/dj` (309 MiB): + BPM and musical key detection

### Volume Configuration

**For DS923+ with NVMe RAID 1 + HDD**:

```hcl
config_volume   = "/volume2/configs/cpp"       # NVMe - config & database
nvme_volume     = "/volume2/media-nvme"        # NVMe - hot data
archive_volume  = "/volume1/media-archive"     # HDD - cold storage
```

**For single volume setups**:

```hcl
config_volume   = "/volume1/configs/cpp"
nvme_volume     = "/volume1/media"
archive_volume  = "/volume1/media"  # Can point to same location
```

### Resource Limits

Adjust CPU and memory limits in `terraform.tfvars`:

```hcl
cpu_limit    = "2.0"   # 2 CPU cores
memory_limit = "2G"    # 2 GB RAM
```

## Managing Your Deployment

### View Current State

```bash
tofu show
# or
terraform show
```

### Update Configuration

1. Edit `terraform.tfvars` or `variables.tf`
2. Preview changes: `tofu plan`
3. Apply changes: `tofu apply`

### Destroy Deployment

```bash
tofu destroy
# or
terraform destroy
```

**Warning**: This removes the container but does NOT delete your data or config files.

### Update copyparty Image

To update to the latest copyparty version:

```bash
# Option 1: Let Terraform/OpenTofu handle it
tofu apply -replace=synology_container_project.copyparty

# Option 2: Update via Synology UI, then refresh state
tofu refresh
```

## Advanced Usage

### Multiple Synology Devices

Use Terraform workspaces:

```bash
# Create workspaces
tofu workspace new nas1
tofu workspace new nas2

# Switch between them
tofu workspace select nas1
tofu apply

tofu workspace select nas2
tofu apply
```

### Enable 2FA Authentication

Uncomment in `variables.tf` and `main.tf`:

```hcl
variable "synology_otp_secret" {
  description = "OTP secret for 2FA (base32 encoded)"
  type        = string
  sensitive   = true
}
```

In `terraform.tfvars`:

```hcl
synology_otp_secret = "YOUR_BASE32_OTP_SECRET"
```

### Remote State Storage

For team collaboration, store state remotely:

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "synology/copyparty/terraform.tfstate"
    region = "us-east-1"
  }
}
```

## Troubleshooting

### Connection Issues

```bash
# Test Synology API access
curl -k https://192.168.1.9:5001/webapi/entry.cgi
```

### Provider Not Found

```bash
# Re-initialize
tofu init -upgrade
```

### State Locked

```bash
# Force unlock (use carefully!)
tofu force-unlock LOCK_ID
```

### Container Not Starting

Check logs via Synology Container Manager UI or:

```bash
ssh admin@192.168.1.9
docker logs copyparty
```

## Security Best Practices

1. **Never commit** `terraform.tfvars` or `*.tfstate` files
2. **Use environment variables** instead of tfvars for CI/CD:
   ```bash
   export TF_VAR_synology_username="admin"
   export TF_VAR_synology_password="password"
   ```
3. **Enable 2FA** on your Synology admin account
4. **Use HTTPS** for Synology API connections
5. **Restrict SSH access** to specific IPs if possible

## Migration from Manual Deployment

If you already have copyparty running:

1. **Import existing container**:
   ```bash
   tofu import synology_container_project.copyparty copyparty
   ```

2. **Verify state matches**:
   ```bash
   tofu plan  # Should show no changes
   ```

## Integration with CI/CD

### GitHub Actions Example

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

## Resources

- [Synology Provider Documentation](https://registry.terraform.io/providers/synology-community/synology/latest/docs)
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [copyparty Documentation](https://github.com/9001/copyparty)
- [Synology DSM API Guide](https://global.download.synology.com/download/Document/Software/DeveloperGuide/)

## Support

For issues with:
- **Terraform/OpenTofu**: Check the Synology provider issues on GitHub
- **copyparty**: See the main copyparty repository
- **Synology DSM**: Consult Synology support documentation
