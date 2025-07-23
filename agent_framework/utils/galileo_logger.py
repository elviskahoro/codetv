"""
Galileo Logger Implementation for Agent Framework

This module provides Galileo observability integration for the agent framework.
It's designed to be optional - if Galileo is not configured or fails to initialize,
the system will fall back to console logging without breaking functionality.
"""

import os
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from abc import ABC

# Optional Galileo import - will be None if not available
try:
    from galileo import GalileoLogger as GalileoLoggerBase

    GALILEO_AVAILABLE = True
except ImportError:
    GalileoLoggerBase = None
    GALILEO_AVAILABLE = False

from .logging import AgentLogger
from .hooks import ToolHooks, ToolSelectionHooks


class GalileoAgentLogger(AgentLogger):
    """
    Galileo implementation of agent logger with fallback to console logging.

    This logger integrates with Galileo observability platform to provide:
    - Trace and span logging for LLM calls
    - Tool execution monitoring
    - Performance metrics
    - Error tracking

    If Galileo is not available or fails to initialize, it falls back to
    console logging to ensure the system continues to work.
    """

    def __init__(
        self,
        agent_id: str,
        project_name: Optional[str] = None,
        log_stream: Optional[str] = None,
    ):
        super().__init__(agent_id)

        # Galileo configuration
        self.galileo_enabled = False
        self.galileo_logger: Optional[GalileoLoggerBase] = None
        self.current_trace_name: Optional[str] = None
        self.trace_start_time: Optional[int] = None

        # Fallback console logger for when Galileo is not available
        from .logging import ConsoleAgentLogger

        self.fallback_logger = ConsoleAgentLogger(agent_id)

        # Try to initialize Galileo
        self._initialize_galileo(project_name, log_stream)

    def _initialize_galileo(
        self, project_name: Optional[str], log_stream: Optional[str]
    ) -> None:
        """
        Initialize Galileo logger with proper error handling.

        Args:
            project_name: Optional project name override
            log_stream: Optional log stream override
        """
        if not GALILEO_AVAILABLE:
            self.fallback_logger.warning(
                "Galileo SDK not available. Falling back to console logging.",
                agent_id=self.agent_id,
            )
            return

        try:
            # Check for required environment variables
            api_key = os.getenv("GALILEO_API_KEY")
            if not api_key:
                self.fallback_logger.warning(
                    "GALILEO_API_KEY not found in environment. Galileo logging disabled.",
                    agent_id=self.agent_id,
                )
                return

            # Use provided values or fall back to environment variables
            project = project_name or os.getenv("GALILEO_PROJECT")
            stream = log_stream or os.getenv("GALILEO_LOG_STREAM")

            if not project:
                self.fallback_logger.warning(
                    "GALILEO_PROJECT not found in environment. Galileo logging disabled.",
                    agent_id=self.agent_id,
                )
                return

            # Initialize Galileo logger
            self.galileo_logger = GalileoLoggerBase()
            self.galileo_enabled = True

            self.fallback_logger.info(
                f"Galileo logging initialized successfully",
                agent_id=self.agent_id,
                project=project,
                log_stream=stream,
            )

        except Exception as e:
            self.fallback_logger.error(
                f"Failed to initialize Galileo logger: {str(e)}",
                agent_id=self.agent_id,
                error=str(e),
            )
            self.galileo_enabled = False

    def _log_to_galileo(self, level: str, message: str, **kwargs) -> None:
        """
        Log to Galileo if available, otherwise use fallback.

        Args:
            level: Log level (info, warning, error, debug)
            message: Log message
            **kwargs: Additional context
        """
        if self.galileo_enabled and self.galileo_logger:
            try:
                # Add metadata to the log
                metadata = {
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "level": level,
                    **kwargs,
                }

                # For now, we'll use the fallback logger for basic logging
                # Galileo is primarily used for traces and spans
                self.fallback_logger.info(f"[Galileo] {message}", **metadata)

            except Exception as e:
                self.fallback_logger.error(
                    f"Failed to log to Galileo: {str(e)}",
                    original_message=message,
                    error=str(e),
                )
        else:
            # Use fallback logger
            getattr(self.fallback_logger, level)(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an informational message"""
        self._log_to_galileo("info", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message"""
        self._log_to_galileo("warning", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message"""
        self._log_to_galileo("error", message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message"""
        self._log_to_galileo("debug", message, **kwargs)

    def _write_log(self, log_entry: Dict[str, Any]) -> None:
        """Write a log entry - delegated to fallback logger"""
        self.fallback_logger._write_log(log_entry)

    def _sanitize_for_json(self, obj: Any) -> Any:
        """Sanitize an object for JSON serialization - delegated to fallback logger"""
        return self.fallback_logger._sanitize_for_json(obj)

    def start_trace(self, trace_name: str) -> None:
        """
        Start a new Galileo trace.

        Args:
            trace_name: Name of the trace
        """
        if not self.galileo_enabled or not self.galileo_logger:
            self.fallback_logger.info(f"Starting trace: {trace_name}")
            return

        try:
            self.galileo_logger.start_trace(trace_name)
            self.current_trace_name = trace_name
            self.trace_start_time = time.perf_counter_ns()

            self.fallback_logger.info(
                f"Started Galileo trace: {trace_name}",
                trace_name=trace_name,
                agent_id=self.agent_id,
            )

        except Exception as e:
            self.fallback_logger.error(
                f"Failed to start Galileo trace: {str(e)}",
                trace_name=trace_name,
                error=str(e),
            )

    def add_llm_span(
        self,
        input_text: str,
        output_text: str,
        model: str,
        name: str,
        num_input_tokens: Optional[int] = None,
        num_output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        duration_ns: Optional[int] = None,
    ) -> None:
        """
        Add an LLM span to the current trace.

        Args:
            input_text: Input prompt to the LLM
            output_text: Output response from the LLM
            model: Model name used
            name: Span name
            num_input_tokens: Number of input tokens
            num_output_tokens: Number of output tokens
            total_tokens: Total tokens used
            duration_ns: Duration in nanoseconds
        """
        if not self.galileo_enabled or not self.galileo_logger:
            self.fallback_logger.info(
                f"LLM Span: {name}",
                model=model,
                input_tokens=num_input_tokens,
                output_tokens=num_output_tokens,
                total_tokens=total_tokens,
                duration_ns=duration_ns,
            )
            return

        try:
            self.galileo_logger.add_llm_span(
                input=input_text,
                output=output_text,
                model=model,
                name=name,
                num_input_tokens=num_input_tokens,
                num_output_tokens=num_output_tokens,
                total_tokens=total_tokens,
                duration_ns=duration_ns,
            )

            self.fallback_logger.info(
                f"Added LLM span to Galileo: {name}",
                model=model,
                input_tokens=num_input_tokens,
                output_tokens=num_output_tokens,
                total_tokens=total_tokens,
                duration_ns=duration_ns,
            )

        except Exception as e:
            self.fallback_logger.error(
                f"Failed to add LLM span to Galileo: {str(e)}",
                span_name=name,
                error=str(e),
            )

    def add_tool_span(
        self,
        tool_name: str,
        inputs: Dict[str, Any],
        outputs: Optional[Dict[str, Any]] = None,
        duration_ns: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """
        Add a tool execution span to the current trace.

        Args:
            tool_name: Name of the tool
            inputs: Tool inputs
            outputs: Tool outputs
            duration_ns: Duration in nanoseconds
            success: Whether the tool execution was successful
            error: Error message if execution failed
        """
        if not self.galileo_enabled or not self.galileo_logger:
            self.fallback_logger.info(
                f"Tool Span: {tool_name}",
                success=success,
                duration_ns=duration_ns,
                error=error,
            )
            return

        try:
            # Create a custom span for tool execution
            span_data = {
                "tool_name": tool_name,
                "inputs": self._sanitize_for_json(inputs),
                "outputs": self._sanitize_for_json(outputs) if outputs else None,
                "success": success,
                "error": error,
                "duration_ns": duration_ns,
            }

            # For now, we'll log this as a custom span
            # In the future, we could add a specific tool span type to Galileo
            self.fallback_logger.info(f"Tool execution span: {tool_name}", **span_data)

        except Exception as e:
            self.fallback_logger.error(
                f"Failed to add tool span to Galileo: {str(e)}",
                tool_name=tool_name,
                error=str(e),
            )

    def conclude_trace(self, output: str, duration_ns: Optional[int] = None) -> None:
        """
        Conclude the current trace and flush to Galileo.

        Args:
            output: Final output of the trace
            duration_ns: Total duration in nanoseconds
        """
        if not self.galileo_enabled or not self.galileo_logger:
            self.fallback_logger.info(
                f"Concluded trace: {self.current_trace_name}",
                output=output,
                duration_ns=duration_ns,
            )
            return

        try:
            self.galileo_logger.conclude(output=output, duration_ns=duration_ns)
            self.galileo_logger.flush()

            self.fallback_logger.info(
                f"Concluded and flushed Galileo trace: {self.current_trace_name}",
                output=output,
                duration_ns=duration_ns,
            )

            # Reset trace state
            self.current_trace_name = None
            self.trace_start_time = None

        except Exception as e:
            self.fallback_logger.error(
                f"Failed to conclude Galileo trace: {str(e)}",
                trace_name=self.current_trace_name,
                error=str(e),
            )

    async def on_agent_planning(self, planning_prompt: str) -> None:
        """Log the agent planning prompt"""
        self.info(f"Planning: {planning_prompt}")

    def on_agent_start(self, initial_task: str) -> None:
        """Log the agent execution start and start a trace"""
        self.info(f"Starting task: {initial_task}")

        # Start a new trace for this task
        trace_name = (
            f"Agent Task: {initial_task[:50]}{'...' if len(initial_task) > 50 else ''}"
        )
        self.start_trace(trace_name)

    async def on_agent_done(
        self, result: str, message_history: List[Dict[str, Any]]
    ) -> None:
        """Log the agent completion and conclude the trace"""
        # Calculate total duration if we have a start time
        duration_ns = None
        if self.trace_start_time:
            duration_ns = time.perf_counter_ns() - self.trace_start_time

        self.info(f"Task completed: {result}")

        # Conclude the trace
        self.conclude_trace(result, duration_ns)

    def get_tool_hooks(self) -> ToolHooks:
        """Get tool hooks for this logger"""
        return self._tool_hooks

    def get_tool_selection_hooks(self) -> ToolSelectionHooks:
        """Get tool selection hooks for this logger"""
        return self._tool_selection_hooks


def create_galileo_logger(
    agent_id: str,
) -> Union[GalileoAgentLogger, "ConsoleAgentLogger"]:
    """
    Factory function to create a Galileo logger with fallback.

    Args:
        agent_id: Unique identifier for the agent

    Returns:
        GalileoAgentLogger if Galileo is available and configured,
        ConsoleAgentLogger as fallback
    """
    # Check if Galileo is enabled
    enable_galileo = os.getenv("ENABLE_GALILEO", "false").lower() == "true"

    if not enable_galileo:
        from .logging import ConsoleAgentLogger

        return ConsoleAgentLogger(agent_id)

    return GalileoAgentLogger(agent_id)
