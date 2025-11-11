# Synology Connection Variables
variable "synology_host" {
  description = "Synology NAS hostname or IP address"
  type        = string
}

variable "synology_port" {
  description = "Synology DSM port (usually 5000 or 5001 for HTTPS)"
  type        = number
  default     = 5001
}

variable "synology_username" {
  description = "Synology admin username"
  type        = string
  sensitive   = true
}

variable "synology_password" {
  description = "Synology admin password"
  type        = string
  sensitive   = true
}

variable "synology_ssl" {
  description = "Use SSL/HTTPS for Synology connection"
  type        = bool
  default     = true
}

# Optional: 2FA support
# variable "synology_otp_secret" {
#   description = "OTP secret for 2FA (base32 encoded)"
#   type        = string
#   sensitive   = true
#   default     = ""
# }

# copyparty Configuration
variable "copyparty_image" {
  description = "Docker image for copyparty"
  type        = string
  default     = "copyparty/ac:latest"

  validation {
    condition     = contains(["copyparty/min:latest", "copyparty/im:latest", "copyparty/ac:latest", "copyparty/iv:latest", "copyparty/dj:latest"], var.copyparty_image)
    error_message = "Must be a valid copyparty image: min, im, ac (recommended), iv, or dj"
  }
}

variable "copyparty_port" {
  description = "Local port to expose copyparty on"
  type        = number
  default     = 3923
}

variable "config_volume" {
  description = "Path to config volume on Synology (e.g., /volume2/configs/cpp)"
  type        = string
}

variable "nvme_volume" {
  description = "Path to NVMe/fast storage volume on Synology (e.g., /volume2/media-nvme)"
  type        = string
}

variable "archive_volume" {
  description = "Path to archive/HDD storage volume on Synology (e.g., /volume1/media-archive)"
  type        = string
}

# Container Environment
variable "puid" {
  description = "User ID for container process"
  type        = number
  default     = 1000
}

variable "pgid" {
  description = "Group ID for container process"
  type        = number
  default     = 100
}

variable "timezone" {
  description = "Timezone for container"
  type        = string
  default     = "UTC"
}

# Resource Limits
variable "cpu_limit" {
  description = "CPU limit for container (e.g., '2.0' for 2 cores)"
  type        = string
  default     = "2.0"
}

variable "memory_limit" {
  description = "Memory limit for container (e.g., '2G')"
  type        = string
  default     = "2G"
}
