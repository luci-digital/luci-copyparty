terraform {
  required_version = ">= 1.0"

  required_providers {
    synology = {
      source  = "synology-community/synology"
      version = "~> 1.0"
    }
  }
}

provider "synology" {
  host     = var.synology_host
  port     = var.synology_port
  username = var.synology_username
  password = var.synology_password
  ssl      = var.synology_ssl

  # Optional: Enable 2FA support
  # otp_secret = var.synology_otp_secret
}

# Create copyparty Docker Compose project
resource "synology_container_project" "copyparty" {
  name = "copyparty"

  compose_file = yamlencode({
    version = "3.8"
    services = {
      copyparty = {
        image           = var.copyparty_image
        container_name  = "copyparty"
        restart         = "unless-stopped"

        ports = [
          "${var.copyparty_port}:3923"
        ]

        volumes = [
          "${var.config_volume}:/cfg",
          "${var.nvme_volume}:/w/nvme",
          "${var.archive_volume}:/w/archive"
        ]

        environment = {
          PUID = var.puid
          PGID = var.pgid
          TZ   = var.timezone
        }

        # Resource limits (optional but recommended)
        deploy = {
          resources = {
            limits = {
              cpus   = var.cpu_limit
              memory = var.memory_limit
            }
          }
        }
      }
    }
  })
}

# Output the container status
output "copyparty_status" {
  description = "Status of the copyparty container"
  value       = synology_container_project.copyparty.id
}

output "copyparty_url" {
  description = "URL to access copyparty"
  value       = "http://${var.synology_host}:${var.copyparty_port}"
}
