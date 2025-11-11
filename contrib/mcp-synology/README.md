# copyparty MCP Server for Synology NAS

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that enables AI assistants like Claude to manage Synology NAS devices and copyparty deployments.

## Features

### 🔧 Tools
- **Container Management**: List, start, stop, restart Docker containers
- **System Monitoring**: Get system info, storage status, shared folders
- **copyparty Deployment**: Deploy and configure copyparty containers
- **File Operations**: Manage shared folders and volumes

### 📚 Resources
- `synology://containers` - List all Docker containers with status
- `synology://system-info` - NAS system information and specs
- `synology://storage` - Volume information and disk usage
- `synology://shared-folders` - Available shared folders

### 💬 Prompts
MCP prompts appear as slash commands in Claude Code (coming soon):
- `/deploy-copyparty` - Interactive copyparty deployment wizard
- `/container-health` - Check container health and logs
- `/storage-report` - Generate storage usage report

## Installation

### Prerequisites

1. **Python 3.10+** installed
2. **Synology NAS** with DSM 6.x, 7.1, or 7.2+
3. **SSH access** enabled on your Synology
4. **Admin credentials** for your NAS

### Install via pip

```bash
# From the repository
cd contrib/mcp-synology
pip install -e .

# Or directly from source
pip install git+https://github.com/9001/copyparty.git#subdirectory=contrib/mcp-synology
```

### Install for Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "copyparty-synology": {
      "command": "python",
      "args": [
        "-m",
        "copyparty_mcp_synology.server"
      ],
      "env": {
        "SYNOLOGY_HOST": "192.168.1.9",
        "SYNOLOGY_PORT": "5001",
        "SYNOLOGY_USERNAME": "admin",
        "SYNOLOGY_PASSWORD": "your-password",
        "SYNOLOGY_SSL": "true"
      }
    }
  }
}
```

**Security Note**: For production, use environment variables or a secure config file instead of storing passwords in the config.

### Install for Claude Code (VS Code)

Add to your VS Code settings or workspace `.vscode/settings.json`:

```json
{
  "mcp.servers": {
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

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SYNOLOGY_HOST` | NAS hostname or IP | - | Yes |
| `SYNOLOGY_PORT` | DSM port (5000 or 5001) | 5001 | No |
| `SYNOLOGY_USERNAME` | Admin username | - | Yes |
| `SYNOLOGY_PASSWORD` | Admin password | - | Yes |
| `SYNOLOGY_SSL` | Use HTTPS | true | No |
| `SYNOLOGY_VERIFY_SSL` | Verify SSL certs | true | No |

### Configuration File

Create `~/.config/copyparty-mcp/config.json`:

```json
{
  "host": "192.168.1.9",
  "port": 5001,
  "username": "admin",
  "password": "your-password",
  "ssl": true,
  "verify_ssl": true
}
```

Then reference it in your MCP config:

```json
{
  "mcpServers": {
    "copyparty-synology": {
      "command": "python",
      "args": [
        "-m",
        "copyparty_mcp_synology.server",
        "--config",
        "~/.config/copyparty-mcp/config.json"
      ]
    }
  }
}
```

## Usage Examples

### In Claude Desktop/Code

Once configured, you can interact naturally:

**Example 1: Check containers**
```
User: Show me all Docker containers on my Synology
Claude: [uses list_containers tool]
```

**Example 2: Deploy copyparty**
```
User: Deploy copyparty on my NAS with NVMe storage at /volume2/media-nvme
Claude: [uses deploy_copyparty tool with appropriate parameters]
```

**Example 3: Monitor storage**
```
User: How much storage space do I have left?
Claude: [uses @synology://storage resource]
```

**Example 4: Container management**
```
User: Restart the copyparty container
Claude: [uses restart_container tool with name="copyparty"]
```

### Direct API Usage

You can also use the MCP server programmatically:

```python
from copyparty_mcp_synology.server import SynologyConfig, SynologyAPI

config = SynologyConfig(
    host="192.168.1.9",
    username="admin",
    password="your-password"
)

api = SynologyAPI(config)
api.login()

# List containers
containers = api.list_containers()
for container in containers:
    print(f"{container['name']}: {container['status']}")

# Get system info
info = api.get_system_info()
print(f"Model: {info['model']}")
print(f"RAM: {info['ram_size']} MB")

api.logout()
```

## Available Tools

### Container Management

#### `list_containers`
Lists all Docker containers with their status.

**Returns**: Array of container objects with name, status, image, ports, etc.

#### `get_container_status`
Get detailed status of a specific container.

**Parameters**:
- `name` (string): Container name

**Returns**: Detailed container information

#### `start_container`
Start a stopped container.

**Parameters**:
- `name` (string): Container name to start

**Returns**: Success/failure message

#### `stop_container`
Stop a running container.

**Parameters**:
- `name` (string): Container name to stop

**Returns**: Success/failure message

#### `restart_container`
Restart a container.

**Parameters**:
- `name` (string): Container name to restart

**Returns**: Success/failure message

### System Information

#### `get_system_info`
Get Synology NAS system information.

**Returns**: System specs (model, DSM version, RAM, CPU, etc.)

#### `get_storage_info`
Get storage volume information and usage.

**Returns**: Array of volumes with size, used space, free space

#### `list_shared_folders`
List all shared folders on the NAS.

**Returns**: Array of shared folders with paths and permissions

### copyparty Deployment

#### `deploy_copyparty`
Deploy copyparty container with recommended configuration.

**Parameters**:
- `config_volume` (string): Path to config volume (e.g., `/volume2/configs/cpp`)
- `data_volumes` (array): Paths to data volumes (e.g., `["/volume2/media-nvme"]`)
- `port` (integer, optional): Port to expose (default: 3923)
- `image` (string, optional): Docker image to use (default: `copyparty/ac:latest`)

**Returns**: Deployment instructions or confirmation

## Resources

Resources can be referenced with `@` mentions in Claude:

### `@synology://containers`
Live view of all Docker containers. Use this to check container status without calling tools.

### `@synology://system-info`
System information including model, DSM version, hardware specs.

### `@synology://storage`
Storage volume information and disk usage statistics.

### `@synology://shared-folders`
List of all shared folders with paths and metadata.

## Security Considerations

1. **Credentials Storage**: Never commit passwords to version control
   - Use environment variables
   - Use system keyring (coming soon)
   - Use encrypted config files

2. **Network Security**:
   - Enable SSL/HTTPS for DSM connections
   - Use VPN when accessing remotely
   - Restrict API access to specific IPs if possible

3. **Authentication**:
   - Use a dedicated API user instead of admin
   - Enable 2FA on Synology (OTP support coming soon)
   - Rotate passwords regularly

4. **API Permissions**:
   - Grant minimum required permissions
   - Audit API access logs
   - Monitor for unusual activity

## Troubleshooting

### Connection Issues

```bash
# Test DSM API accessibility
curl -k https://192.168.1.9:5001/webapi/entry.cgi?api=SYNO.API.Info&version=1&method=query
```

### Authentication Failures

- Verify credentials are correct
- Check if 2FA is enabled (not yet supported)
- Ensure user has admin privileges
- Check if IP is not blocked

### Container Operations Fail

- Verify Docker/Container Manager is running
- Check user has Docker permissions
- Ensure SSH access is enabled
- Check DSM logs: `/var/log/synolog/`

### SSL Certificate Errors

If using self-signed certificates:

```json
{
  "env": {
    "SYNOLOGY_VERIFY_SSL": "false"
  }
}
```

**Warning**: Only disable SSL verification on trusted networks.

### Debug Mode

Enable detailed logging:

```json
{
  "env": {
    "LOG_LEVEL": "DEBUG"
  }
}
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/9001/copyparty.git
cd copyparty/contrib/mcp-synology

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black copyparty_mcp_synology/
mypy copyparty_mcp_synology/
```

### Adding New Tools

1. Add tool definition to `list_tools()`
2. Implement tool handler in `call_tool()`
3. Add corresponding API method to `SynologyAPI` class
4. Update documentation

### Adding New Resources

1. Add resource definition to `list_resources()`
2. Implement resource reader in `read_resource()`
3. Update documentation

## Roadmap

- [ ] 2FA/OTP support
- [ ] File upload/download operations
- [ ] Task scheduler integration
- [ ] Package management (install/update packages)
- [ ] Virtual Machine management
- [ ] Snapshot management
- [ ] User and permission management
- [ ] Active Directory integration
- [ ] Prometheus metrics export
- [ ] Webhook notifications
- [ ] Backup and restore tools

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Synology DSM API Guide](https://global.download.synology.com/download/Document/Software/DeveloperGuide/)
- [copyparty Documentation](https://github.com/9001/copyparty)
- [Claude Desktop](https://claude.ai/desktop)
- [Claude Code for VS Code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)

## Support

For issues:
- **MCP Server**: Open an issue in the copyparty repository
- **Synology API**: Check Synology developer documentation
- **copyparty**: See main copyparty repository issues

## Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- Integrates with [copyparty](https://github.com/9001/copyparty) file server
- Supports [Synology](https://www.synology.com/) NAS devices
