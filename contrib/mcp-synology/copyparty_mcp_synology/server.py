#!/usr/bin/env python3
"""
MCP Server for Synology NAS and copyparty Management

This Model Context Protocol server provides tools and resources for managing
Synology NAS devices and copyparty deployments.

Features:
- Container management (Docker/Container Manager)
- File operations via DSM API
- copyparty deployment and configuration
- System monitoring and status
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("copyparty-mcp-synology")


class SynologyConfig(BaseModel):
    """Configuration for Synology connection."""
    host: str = Field(..., description="Synology hostname or IP")
    port: int = Field(5001, description="DSM port (5000 or 5001)")
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")
    ssl: bool = Field(True, description="Use HTTPS")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")


class SynologyAPI:
    """Client for interacting with Synology DSM API."""

    def __init__(self, config: SynologyConfig):
        self.config = config
        self.base_url = f"{'https' if config.ssl else 'http'}://{config.host}:{config.port}"
        self.session_id: Optional[str] = None
        self.session = requests.Session()
        self.session.verify = config.verify_ssl

    def _api_url(self, path: str) -> str:
        """Construct API URL."""
        return urljoin(self.base_url, path)

    def login(self) -> bool:
        """Authenticate with DSM."""
        try:
            response = self.session.get(
                self._api_url("/webapi/entry.cgi"),
                params={
                    "api": "SYNO.API.Auth",
                    "version": "6",
                    "method": "login",
                    "account": self.config.username,
                    "passwd": self.config.password,
                    "format": "sid",
                },
            )
            data = response.json()
            if data.get("success"):
                self.session_id = data["data"]["sid"]
                logger.info("Successfully authenticated with Synology DSM")
                return True
            else:
                logger.error(f"Login failed: {data.get('error')}")
                return False
        except Exception as e:
            logger.error(f"Login exception: {e}")
            return False

    def logout(self):
        """Logout from DSM."""
        if self.session_id:
            try:
                self.session.get(
                    self._api_url("/webapi/entry.cgi"),
                    params={
                        "api": "SYNO.API.Auth",
                        "version": "6",
                        "method": "logout",
                        "_sid": self.session_id,
                    },
                )
            except Exception as e:
                logger.error(f"Logout exception: {e}")

    def _call_api(
        self, api: str, version: int, method: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an API call to DSM."""
        if not self.session_id:
            if not self.login():
                raise Exception("Failed to authenticate with Synology DSM")

        call_params = {
            "api": api,
            "version": version,
            "method": method,
            "_sid": self.session_id,
        }
        if params:
            call_params.update(params)

        response = self.session.get(
            self._api_url("/webapi/entry.cgi"), params=call_params
        )
        data = response.json()

        if not data.get("success"):
            raise Exception(f"API call failed: {data.get('error')}")

        return data.get("data", {})

    def list_containers(self) -> List[Dict[str, Any]]:
        """List all Docker containers."""
        try:
            result = self._call_api(
                "SYNO.Docker.Container",
                1,
                "list",
                {"limit": -1, "offset": 0},
            )
            return result.get("containers", [])
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return []

    def get_container_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific container."""
        containers = self.list_containers()
        for container in containers:
            if container.get("name") == name:
                return container
        return None

    def start_container(self, name: str) -> bool:
        """Start a Docker container."""
        try:
            self._call_api(
                "SYNO.Docker.Container",
                1,
                "start",
                {"name": name},
            )
            return True
        except Exception as e:
            logger.error(f"Failed to start container {name}: {e}")
            return False

    def stop_container(self, name: str) -> bool:
        """Stop a Docker container."""
        try:
            self._call_api(
                "SYNO.Docker.Container",
                1,
                "stop",
                {"name": name},
            )
            return True
        except Exception as e:
            logger.error(f"Failed to stop container {name}: {e}")
            return False

    def restart_container(self, name: str) -> bool:
        """Restart a Docker container."""
        try:
            self._call_api(
                "SYNO.Docker.Container",
                1,
                "restart",
                {"name": name},
            )
            return True
        except Exception as e:
            logger.error(f"Failed to restart container {name}: {e}")
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            return self._call_api("SYNO.Core.System", 3, "info")
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}

    def list_shared_folders(self) -> List[Dict[str, Any]]:
        """List all shared folders."""
        try:
            result = self._call_api(
                "SYNO.FileStation.List",
                2,
                "list_share",
                {"additional": '["real_path","size","owner","time"]'},
            )
            return result.get("shares", [])
        except Exception as e:
            logger.error(f"Failed to list shared folders: {e}")
            return []

    def get_storage_info(self) -> List[Dict[str, Any]]:
        """Get storage/volume information."""
        try:
            result = self._call_api("SYNO.Storage.CGI.Storage", 1, "load_info")
            return result.get("volumes", [])
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return []


# Global API client (initialized from environment or config)
api_client: Optional[SynologyAPI] = None


def create_server(config: SynologyConfig) -> Server:
    """Create and configure the MCP server."""
    global api_client
    api_client = SynologyAPI(config)

    server = Server("copyparty-mcp-synology")

    @server.list_resources()
    async def list_resources() -> List[Resource]:
        """List available resources."""
        return [
            Resource(
                uri="synology://containers",
                name="Docker Containers",
                mimeType="application/json",
                description="List of all Docker containers on the NAS",
            ),
            Resource(
                uri="synology://system-info",
                name="System Information",
                mimeType="application/json",
                description="Synology NAS system information",
            ),
            Resource(
                uri="synology://storage",
                name="Storage Information",
                mimeType="application/json",
                description="Storage volumes and usage information",
            ),
            Resource(
                uri="synology://shared-folders",
                name="Shared Folders",
                mimeType="application/json",
                description="List of shared folders on the NAS",
            ),
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a resource by URI."""
        if not api_client:
            raise Exception("API client not initialized")

        if uri == "synology://containers":
            containers = api_client.list_containers()
            return json.dumps(containers, indent=2)

        elif uri == "synology://system-info":
            info = api_client.get_system_info()
            return json.dumps(info, indent=2)

        elif uri == "synology://storage":
            storage = api_client.get_storage_info()
            return json.dumps(storage, indent=2)

        elif uri == "synology://shared-folders":
            folders = api_client.list_shared_folders()
            return json.dumps(folders, indent=2)

        else:
            raise Exception(f"Unknown resource URI: {uri}")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available tools."""
        return [
            Tool(
                name="list_containers",
                description="List all Docker containers on the Synology NAS",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_container_status",
                description="Get detailed status of a specific container",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Container name",
                        },
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="start_container",
                description="Start a Docker container",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Container name to start",
                        },
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="stop_container",
                description="Stop a Docker container",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Container name to stop",
                        },
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="restart_container",
                description="Restart a Docker container",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Container name to restart",
                        },
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="deploy_copyparty",
                description="Deploy copyparty container with recommended configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "config_volume": {
                            "type": "string",
                            "description": "Path to config volume (e.g., /volume2/configs/cpp)",
                        },
                        "data_volumes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Paths to data volumes (e.g., ['/volume2/media-nvme', '/volume1/archive'])",
                        },
                        "port": {
                            "type": "integer",
                            "description": "Port to expose (default: 3923)",
                            "default": 3923,
                        },
                        "image": {
                            "type": "string",
                            "description": "Docker image to use (default: copyparty/ac:latest)",
                            "default": "copyparty/ac:latest",
                        },
                    },
                    "required": ["config_volume", "data_volumes"],
                },
            ),
            Tool(
                name="get_system_info",
                description="Get Synology NAS system information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="list_shared_folders",
                description="List all shared folders on the NAS",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_storage_info",
                description="Get storage volume information and usage",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a tool."""
        if not api_client:
            raise Exception("API client not initialized")

        try:
            if name == "list_containers":
                containers = api_client.list_containers()
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(containers, indent=2),
                    )
                ]

            elif name == "get_container_status":
                container_name = arguments["name"]
                status = api_client.get_container_status(container_name)
                if status:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(status, indent=2),
                        )
                    ]
                else:
                    return [
                        TextContent(
                            type="text",
                            text=f"Container '{container_name}' not found",
                        )
                    ]

            elif name == "start_container":
                container_name = arguments["name"]
                success = api_client.start_container(container_name)
                return [
                    TextContent(
                        type="text",
                        text=f"Container '{container_name}' {'started successfully' if success else 'failed to start'}",
                    )
                ]

            elif name == "stop_container":
                container_name = arguments["name"]
                success = api_client.stop_container(container_name)
                return [
                    TextContent(
                        type="text",
                        text=f"Container '{container_name}' {'stopped successfully' if success else 'failed to stop'}",
                    )
                ]

            elif name == "restart_container":
                container_name = arguments["name"]
                success = api_client.restart_container(container_name)
                return [
                    TextContent(
                        type="text",
                        text=f"Container '{container_name}' {'restarted successfully' if success else 'failed to restart'}",
                    )
                ]

            elif name == "deploy_copyparty":
                # This would integrate with Docker Compose or direct container creation
                # For now, return instructions
                config = arguments.get("config_volume")
                volumes = arguments.get("data_volumes", [])
                port = arguments.get("port", 3923)
                image = arguments.get("image", "copyparty/ac:latest")

                instructions = f"""
To deploy copyparty with these settings:

Docker Run Command:
```bash
docker run -d \\
  --name copyparty \\
  --restart unless-stopped \\
  -p {port}:3923 \\
  -v {config}:/cfg \\
"""
                for i, vol in enumerate(volumes):
                    mount = f"/w/vol{i}" if i > 0 else "/w"
                    instructions += f"  -v {vol}:{mount} \\\n"

                instructions += f"  {image}\n```\n\n"
                instructions += f"Access copyparty at: http://your-nas-ip:{port}\n"

                return [TextContent(type="text", text=instructions)]

            elif name == "get_system_info":
                info = api_client.get_system_info()
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(info, indent=2),
                    )
                ]

            elif name == "list_shared_folders":
                folders = api_client.list_shared_folders()
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(folders, indent=2),
                    )
                ]

            elif name == "get_storage_info":
                storage = api_client.get_storage_info()
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(storage, indent=2),
                    )
                ]

            else:
                raise Exception(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error executing tool: {str(e)}",
                )
            ]

    return server


async def main():
    """Main entry point for the MCP server."""
    import os
    import sys

    # Load configuration from environment or config file
    config = SynologyConfig(
        host=os.getenv("SYNOLOGY_HOST", ""),
        port=int(os.getenv("SYNOLOGY_PORT", "5001")),
        username=os.getenv("SYNOLOGY_USERNAME", ""),
        password=os.getenv("SYNOLOGY_PASSWORD", ""),
        ssl=os.getenv("SYNOLOGY_SSL", "true").lower() == "true",
        verify_ssl=os.getenv("SYNOLOGY_VERIFY_SSL", "true").lower() == "true",
    )

    if not config.host or not config.username or not config.password:
        logger.error("Missing required configuration. Set SYNOLOGY_HOST, SYNOLOGY_USERNAME, and SYNOLOGY_PASSWORD environment variables.")
        sys.exit(1)

    server = create_server(config)

    async with stdio_server() as (read_stream, write_stream):
        logger.info("copyparty MCP Synology server started")
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
