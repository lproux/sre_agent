"""CLI entry-point for the SRE Agent.

Usage::

    # Run the agent continuously:
    sre-agent run

    # Execute a single poll-and-remediate cycle and exit:
    sre-agent run --once

    # Dry-run mode (no actual remediation):
    sre-agent run --dry-run

All configuration is loaded from environment variables (``SRE_AGENT_*``).
See :class:`~sre_agent.config.AgentConfig` for the full list of options.
"""

from __future__ import annotations

import logging
import sys

import click

from sre_agent.agent import SREAgent
from sre_agent.config import AgentConfig, LogLevel


def _configure_logging(level: LogLevel, json_logs: bool) -> None:
    import structlog

    processors: list = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.value),
    )


@click.group()
def main() -> None:
    """SRE Agent – Azure-enabled site reliability automation."""


@main.command()
@click.option("--once", is_flag=True, default=False, help="Run a single cycle and exit.")
@click.option("--dry-run", is_flag=True, default=False, help="Log remediations without executing them.")
def run(once: bool, dry_run: bool) -> None:
    """Start the SRE agent (continuous or single-cycle)."""
    try:
        config = AgentConfig()  # type: ignore[call-arg]
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Configuration error: {exc}", err=True)
        sys.exit(1)

    if dry_run:
        # Override config with dry_run=True
        config = config.model_copy(update={"dry_run": True})

    _configure_logging(config.log_level, config.log_json)

    agent = SREAgent(config=config)
    agent.register_default_remediations()

    if once:
        summary = agent.run_once()
        click.echo(f"Cycle summary: {summary}")
    else:
        agent.run()
