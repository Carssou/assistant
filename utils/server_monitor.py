"""
MCP Server Health Monitoring

This module provides utilities for monitoring the health and connectivity
of MCP servers in the multi-tool coordination system.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ServerStatus(Enum):
    """MCP Server status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class ServerHealthMetrics:
    """Health metrics for a single MCP server."""

    server_name: str
    status: ServerStatus
    last_check: datetime
    response_time_ms: float | None = None
    error_count: int = 0
    uptime_percentage: float = 0.0
    last_error: str | None = None
    consecutive_failures: int = 0


@dataclass
class CoordinationMetrics:
    """Metrics for multi-tool coordination performance."""

    successful_workflows: int = 0
    failed_workflows: int = 0
    average_workflow_time: float = 0.0
    total_tool_calls: int = 0
    cross_server_operations: int = 0
    last_coordination_check: datetime | None = None


class ServerHealthMonitor:
    """Monitor health and performance of MCP servers."""

    def __init__(self, check_interval: int = 60):
        """
        Initialize server health monitor.

        Args:
            check_interval: Seconds between health checks
        """
        self.check_interval = check_interval
        self.server_metrics: dict[str, ServerHealthMetrics] = {}
        self.coordination_metrics = CoordinationMetrics()
        self.logger = logging.getLogger(__name__)
        self._monitoring = False
        self._check_task: asyncio.Task | None = None

    async def start_monitoring(self, server_names: list[str]):
        """
        Start monitoring MCP servers.

        Args:
            server_names: List of server names to monitor
        """
        # Initialize metrics for each server
        for server_name in server_names:
            self.server_metrics[server_name] = ServerHealthMetrics(
                server_name=server_name, status=ServerStatus.UNKNOWN, last_check=datetime.now()
            )

        self._monitoring = True
        self._check_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info(f"Started monitoring {len(server_names)} MCP servers")

    async def stop_monitoring(self):
        """Stop monitoring MCP servers."""
        self._monitoring = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped MCP server monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                await self._check_all_servers()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying

    async def _check_all_servers(self):
        """Check health of all monitored servers."""
        check_tasks = []
        for server_name in self.server_metrics.keys():
            task = asyncio.create_task(self._check_server_health(server_name))
            check_tasks.append(task)

        if check_tasks:
            await asyncio.gather(*check_tasks, return_exceptions=True)

    async def _check_server_health(self, server_name: str):
        """
        Check health of a specific server.

        Args:
            server_name: Name of the server to check
        """
        start_time = time.time()
        metrics = self.server_metrics[server_name]

        try:
            # Attempt a simple server interaction
            # In a real implementation, this would ping the MCP server
            # For now, we'll simulate based on server type
            success = await self._simulate_server_check(server_name)

            response_time = (time.time() - start_time) * 1000  # Convert to ms

            if success:
                metrics.status = ServerStatus.HEALTHY
                metrics.consecutive_failures = 0
                metrics.response_time_ms = response_time
            else:
                metrics.error_count += 1
                metrics.consecutive_failures += 1
                metrics.last_error = f"Server check failed for {server_name}"

                if metrics.consecutive_failures >= 3:
                    metrics.status = ServerStatus.DOWN
                else:
                    metrics.status = ServerStatus.DEGRADED

            metrics.last_check = datetime.now()

        except Exception as e:
            metrics.error_count += 1
            metrics.consecutive_failures += 1
            metrics.last_error = str(e)
            metrics.status = ServerStatus.DOWN
            metrics.last_check = datetime.now()

            self.logger.warning(f"Health check failed for {server_name}: {e}")

    async def _simulate_server_check(self, server_name: str) -> bool:
        """
        Simulate server health check.

        Args:
            server_name: Name of server to check

        Returns:
            True if server is healthy, False otherwise
        """
        # Simulate different response times and occasional failures
        await asyncio.sleep(0.1)  # Simulate network delay

        # Simulate 95% uptime
        import random

        return random.random() > 0.05

    def get_server_status(self, server_name: str) -> ServerHealthMetrics | None:
        """
        Get current status of a specific server.

        Args:
            server_name: Name of server

        Returns:
            Server health metrics or None if not found
        """
        return self.server_metrics.get(server_name)

    def get_all_server_status(self) -> dict[str, ServerHealthMetrics]:
        """Get status of all monitored servers."""
        return self.server_metrics.copy()

    def get_healthy_servers(self) -> list[str]:
        """Get list of currently healthy servers."""
        return [
            name
            for name, metrics in self.server_metrics.items()
            if metrics.status == ServerStatus.HEALTHY
        ]

    def get_degraded_servers(self) -> list[str]:
        """Get list of degraded servers."""
        return [
            name
            for name, metrics in self.server_metrics.items()
            if metrics.status == ServerStatus.DEGRADED
        ]

    def get_down_servers(self) -> list[str]:
        """Get list of down servers."""
        return [
            name
            for name, metrics in self.server_metrics.items()
            if metrics.status == ServerStatus.DOWN
        ]

    def record_workflow_success(self, workflow_time: float, tools_used: list[str]):
        """
        Record a successful workflow completion.

        Args:
            workflow_time: Time taken for workflow in seconds
            tools_used: List of tools used in workflow
        """
        self.coordination_metrics.successful_workflows += 1
        self.coordination_metrics.total_tool_calls += len(tools_used)

        # Update average workflow time
        total_workflows = (
            self.coordination_metrics.successful_workflows
            + self.coordination_metrics.failed_workflows
        )
        if total_workflows > 1:
            current_avg = self.coordination_metrics.average_workflow_time
            self.coordination_metrics.average_workflow_time = (
                current_avg * (total_workflows - 1) + workflow_time
            ) / total_workflows
        else:
            self.coordination_metrics.average_workflow_time = workflow_time

        # Count cross-server operations
        unique_servers = set()
        for tool in tools_used:
            server = self._get_server_for_tool(tool)
            if server:
                unique_servers.add(server)

        if len(unique_servers) > 1:
            self.coordination_metrics.cross_server_operations += 1

        self.coordination_metrics.last_coordination_check = datetime.now()

    def record_workflow_failure(self, error: str, tools_attempted: list[str]):
        """
        Record a failed workflow.

        Args:
            error: Error message
            tools_attempted: List of tools that were attempted
        """
        self.coordination_metrics.failed_workflows += 1
        self.coordination_metrics.last_coordination_check = datetime.now()

        self.logger.warning(f"Workflow failed with error: {error}")
        self.logger.warning(f"Tools attempted: {tools_attempted}")

    def _get_server_for_tool(self, tool_name: str) -> str | None:
        """
        Get server name for a given tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Server name or None if not found
        """
        # Map tools to servers based on naming conventions
        tool_server_map = {
            "create_note": "obsidian",
            "read_note": "obsidian",
            "search_vault": "obsidian",
            "edit_note": "obsidian",
            "searxng_web_search": "searxng",
            "web_url_read": "searxng",
            "todoist_create_task": "todoist",
            "todoist_get_tasks": "todoist",
            "get-video-info": "youtube",
            "get_video_info": "youtube",
        }

        return tool_server_map.get(tool_name)

    def get_coordination_metrics(self) -> CoordinationMetrics:
        """Get coordination performance metrics."""
        return self.coordination_metrics

    def get_health_summary(self) -> dict[str, Any]:
        """Get overall health summary."""
        healthy = len(self.get_healthy_servers())
        degraded = len(self.get_degraded_servers())
        down = len(self.get_down_servers())
        total = len(self.server_metrics)

        if total == 0:
            overall_health = "unknown"
        elif down > 0:
            overall_health = "degraded"
        elif degraded > 0:
            overall_health = "partial"
        else:
            overall_health = "healthy"

        return {
            "overall_health": overall_health,
            "servers": {"total": total, "healthy": healthy, "degraded": degraded, "down": down},
            "coordination": {
                "success_rate": (
                    self.coordination_metrics.successful_workflows
                    / max(
                        1,
                        self.coordination_metrics.successful_workflows
                        + self.coordination_metrics.failed_workflows,
                    )
                )
                * 100,
                "average_workflow_time": self.coordination_metrics.average_workflow_time,
                "cross_server_operations": self.coordination_metrics.cross_server_operations,
            },
        }


# Global monitor instance
_global_monitor: ServerHealthMonitor | None = None


def get_global_monitor() -> ServerHealthMonitor:
    """Get or create global server monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ServerHealthMonitor()
    return _global_monitor


async def start_monitoring(server_names: list[str]):
    """Start monitoring MCP servers globally."""
    monitor = get_global_monitor()
    await monitor.start_monitoring(server_names)


async def stop_monitoring():
    """Stop global monitoring."""
    global _global_monitor
    if _global_monitor:
        await _global_monitor.stop_monitoring()
        _global_monitor = None
