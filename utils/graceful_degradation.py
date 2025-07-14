"""
Graceful Degradation for Multi-Tool Coordination

This module provides utilities for handling tool failures and server outages
gracefully in multi-tool workflows.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from utils.server_monitor import ServerHealthMonitor


class DegradationStrategy(Enum):
    """Strategies for handling tool failures."""
    SKIP = "skip"  # Skip the failed tool and continue
    SUBSTITUTE = "substitute"  # Use an alternative tool
    PARTIAL = "partial"  # Continue with reduced functionality
    FAIL = "fail"  # Fail the entire workflow


@dataclass
class ToolAlternative:
    """Alternative tool configuration."""
    primary_tool: str
    alternative_tool: str
    capability_match: float  # 0.0 to 1.0, how well alternative matches primary
    notes: str = ""


@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    tool_name: str
    required: bool = True
    alternatives: list[str] | None = None
    degradation_strategy: DegradationStrategy = DegradationStrategy.FAIL

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class GracefulDegradationManager:
    """Manages graceful degradation of multi-tool workflows."""

    def __init__(self, server_monitor: ServerHealthMonitor | None = None):
        """
        Initialize degradation manager.
        
        Args:
            server_monitor: Optional server health monitor
        """
        self.server_monitor = server_monitor
        self.logger = logging.getLogger(__name__)

        # Tool alternatives mapping
        self.tool_alternatives: dict[str, list[ToolAlternative]] = {
            # Search alternatives
            "searxng_web_search": [
                ToolAlternative(
                    primary_tool="searxng_web_search",
                    alternative_tool="web_url_read",
                    capability_match=0.6,
                    notes="Can read specific URLs but not search broadly"
                )
            ],

            # Note creation alternatives
            "create_note": [
                ToolAlternative(
                    primary_tool="create_note",
                    alternative_tool="edit_note",
                    capability_match=0.8,
                    notes="Can edit existing notes if create fails"
                )
            ],

            # Task management alternatives
            "todoist_create_task": [
                ToolAlternative(
                    primary_tool="todoist_create_task",
                    alternative_tool="create_note",
                    capability_match=0.7,
                    notes="Can create task notes in vault instead"
                )
            ],

            # Video processing alternatives
            "get-video-info": [
                ToolAlternative(
                    primary_tool="get-video-info",
                    alternative_tool="web_url_read",
                    capability_match=0.4,
                    notes="Can read video page but not extract transcript"
                )
            ]
        }

        # Workflow patterns and their degradation strategies
        self.workflow_patterns = {
            "research_workflow": [
                WorkflowStep("searxng_web_search", required=True,
                           alternatives=["web_url_read"],
                           degradation_strategy=DegradationStrategy.SUBSTITUTE),
                WorkflowStep("create_note", required=True,
                           degradation_strategy=DegradationStrategy.FAIL),
                WorkflowStep("todoist_create_task", required=False,
                           alternatives=["create_note"],
                           degradation_strategy=DegradationStrategy.SUBSTITUTE)
            ],

            "video_learning": [
                WorkflowStep("get-video-info", required=True,
                           alternatives=["web_url_read"],
                           degradation_strategy=DegradationStrategy.SUBSTITUTE),
                WorkflowStep("create_note", required=True,
                           degradation_strategy=DegradationStrategy.FAIL)
            ],

            "information_synthesis": [
                WorkflowStep("searxng_web_search", required=True,
                           degradation_strategy=DegradationStrategy.PARTIAL),
                WorkflowStep("web_url_read", required=False,
                           degradation_strategy=DegradationStrategy.SKIP),
                WorkflowStep("create_note", required=True,
                           degradation_strategy=DegradationStrategy.FAIL)
            ]
        }

    def get_available_tools(self) -> set[str]:
        """
        Get set of currently available tools based on server health.
        
        Returns:
            Set of available tool names
        """
        if not self.server_monitor:
            # If no monitor, assume all tools are available
            return set([
                "create_note", "read_note", "search_vault", "edit_note",
                "searxng_web_search", "web_url_read",
                "todoist_create_task", "todoist_get_tasks",
                "get-video-info"
            ])

        available_tools = set()
        healthy_servers = self.server_monitor.get_healthy_servers()

        # Map servers to their tools
        server_tools = {
            "obsidian": ["create_note", "read_note", "search_vault", "edit_note",
                        "list_available_vaults", "move_note", "delete_note",
                        "add_tags", "remove_tags", "rename_tag", "create_directory"],
            "searxng": ["searxng_web_search", "web_url_read"],
            "todoist": ["todoist_create_task", "todoist_get_tasks",
                       "todoist_update_task", "todoist_delete_task"],
            "youtube": ["get-video-info", "get_video_info"]
        }

        for server in healthy_servers:
            if server in server_tools:
                available_tools.update(server_tools[server])

        return available_tools

    def plan_workflow_with_degradation(self, intended_workflow: list[str]) -> tuple[list[str], list[str]]:
        """
        Plan a workflow with graceful degradation.
        
        Args:
            intended_workflow: List of intended tools to use
            
        Returns:
            Tuple of (executable_workflow, degradation_notes)
        """
        available_tools = self.get_available_tools()
        executable_workflow = []
        degradation_notes = []

        for tool in intended_workflow:
            if tool in available_tools:
                # Tool is available, use as planned
                executable_workflow.append(tool)
            else:
                # Tool is not available, try degradation
                alternative, note = self._find_alternative(tool, available_tools)

                if alternative:
                    executable_workflow.append(alternative)
                    degradation_notes.append(f"Substituted {tool} with {alternative}: {note}")
                    self.logger.warning(f"Tool {tool} unavailable, using {alternative}")
                else:
                    degradation_notes.append(f"Tool {tool} unavailable and no alternatives found")
                    self.logger.error(f"Tool {tool} unavailable with no alternatives")

        return executable_workflow, degradation_notes

    def _find_alternative(self, unavailable_tool: str, available_tools: set[str]) -> tuple[str | None, str]:
        """
        Find an alternative for an unavailable tool.
        
        Args:
            unavailable_tool: The tool that is not available
            available_tools: Set of currently available tools
            
        Returns:
            Tuple of (alternative_tool, explanation) or (None, reason)
        """
        if unavailable_tool not in self.tool_alternatives:
            return None, f"No alternatives configured for {unavailable_tool}"

        alternatives = self.tool_alternatives[unavailable_tool]

        # Find the best available alternative
        best_alternative = None
        best_match_score = 0.0

        for alt in alternatives:
            if alt.alternative_tool in available_tools:
                if alt.capability_match > best_match_score:
                    best_alternative = alt
                    best_match_score = alt.capability_match

        if best_alternative:
            return best_alternative.alternative_tool, best_alternative.notes
        else:
            available_alts = [alt.alternative_tool for alt in alternatives]
            return None, f"Alternatives {available_alts} are also unavailable"

    def execute_with_degradation(self, workflow_pattern: str,
                                user_query: str) -> tuple[bool, list[str], str]:
        """
        Execute a workflow with degradation handling.
        
        Args:
            workflow_pattern: Name of workflow pattern to execute
            user_query: User's original query
            
        Returns:
            Tuple of (success, executed_tools, result_message)
        """
        if workflow_pattern not in self.workflow_patterns:
            return False, [], f"Unknown workflow pattern: {workflow_pattern}"

        pattern = self.workflow_patterns[workflow_pattern]
        available_tools = self.get_available_tools()
        executed_tools = []
        degradation_messages = []

        for step in pattern:
            tool_executed = None

            # Try primary tool first
            if step.tool_name in available_tools:
                tool_executed = step.tool_name
            else:
                # Primary tool unavailable, apply degradation strategy
                if step.degradation_strategy == DegradationStrategy.FAIL and step.required:
                    return False, executed_tools, f"Required tool {step.tool_name} unavailable"

                elif step.degradation_strategy == DegradationStrategy.SUBSTITUTE:
                    # Try alternatives
                    for alt in step.alternatives:
                        if alt in available_tools:
                            tool_executed = alt
                            degradation_messages.append(f"Substituted {step.tool_name} with {alt}")
                            break

                    if not tool_executed and step.required:
                        return False, executed_tools, f"No alternatives available for required tool {step.tool_name}"

                elif step.degradation_strategy == DegradationStrategy.SKIP:
                    degradation_messages.append(f"Skipped unavailable tool {step.tool_name}")
                    continue

                elif step.degradation_strategy == DegradationStrategy.PARTIAL:
                    degradation_messages.append(f"Continuing with reduced functionality (missing {step.tool_name})")
                    continue

            if tool_executed:
                executed_tools.append(tool_executed)

        # Build result message
        result_parts = [f"Executed workflow '{workflow_pattern}' with tools: {', '.join(executed_tools)}"]

        if degradation_messages:
            result_parts.append("Degradation applied:")
            result_parts.extend(f"  - {msg}" for msg in degradation_messages)

        return True, executed_tools, "\n".join(result_parts)

    def get_degradation_report(self) -> dict[str, Any]:
        """
        Get a report on current degradation status.
        
        Returns:
            Dictionary with degradation status information
        """
        available_tools = self.get_available_tools()
        all_tools = set()

        # Collect all known tools
        for alternatives in self.tool_alternatives.values():
            for alt in alternatives:
                all_tools.add(alt.primary_tool)
                all_tools.add(alt.alternative_tool)

        unavailable_tools = all_tools - available_tools

        # Check which workflows are affected
        affected_workflows = {}
        for workflow_name, pattern in self.workflow_patterns.items():
            missing_required = []
            missing_optional = []

            for step in pattern:
                if step.tool_name not in available_tools:
                    if step.required:
                        missing_required.append(step.tool_name)
                    else:
                        missing_optional.append(step.tool_name)

            if missing_required or missing_optional:
                affected_workflows[workflow_name] = {
                    "missing_required": missing_required,
                    "missing_optional": missing_optional,
                    "can_execute": len(missing_required) == 0
                }

        return {
            "total_tools": len(all_tools),
            "available_tools": len(available_tools),
            "unavailable_tools": len(unavailable_tools),
            "unavailable_tool_list": list(unavailable_tools),
            "affected_workflows": affected_workflows,
            "degradation_strategies_available": len(self.tool_alternatives)
        }

    def add_tool_alternative(self, primary: str, alternative: str,
                           capability_match: float, notes: str = ""):
        """
        Add a new tool alternative.
        
        Args:
            primary: Primary tool name
            alternative: Alternative tool name
            capability_match: Match quality (0.0 to 1.0)
            notes: Description of the alternative
        """
        if primary not in self.tool_alternatives:
            self.tool_alternatives[primary] = []

        alt = ToolAlternative(
            primary_tool=primary,
            alternative_tool=alternative,
            capability_match=capability_match,
            notes=notes
        )

        self.tool_alternatives[primary].append(alt)
        self.logger.info(f"Added alternative {alternative} for {primary}")


# Global degradation manager instance
_global_degradation_manager: GracefulDegradationManager | None = None


def get_global_degradation_manager() -> GracefulDegradationManager:
    """Get or create global degradation manager."""
    global _global_degradation_manager
    if _global_degradation_manager is None:
        from utils.server_monitor import get_global_monitor
        _global_degradation_manager = GracefulDegradationManager(get_global_monitor())
    return _global_degradation_manager
