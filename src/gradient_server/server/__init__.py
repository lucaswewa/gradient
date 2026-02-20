"""A package responsible for, setup, booting, and shutting down the server."""

from __future__ import annotations

import logging
import os
from argparse import Namespace
from copy import copy
from typing import Any, Optional

import uvicorn
from fastapi.middleware.cors import CORSMiddleware  # vue3 migration

import labthings_fastapi as lt
from labthings_fastapi.server import fallback
from labthings_fastapi.server.config_model import ThingServerConfig

from .._logging import (
    GRADIENT_HANDLER,
    configure_logging,
    retrieve_log,
    retrieve_log_from_file,
)
from ..utilities import load_patched_config

LOGGER = logging.getLogger(__name__)
DEVELOPER_MODE = os.getenv("GRADIENT_SERVER_DEV_MODE", "false").lower() == "true"


def customise_server(
    server: lt.ThingServer, log_folder: str, _scans_folder: Optional[str]
) -> None:
    """Customise the server with additional endpoints, etc."""
    configure_logging(log_folder)

    if DEVELOPER_MODE:
        # Allow CORS in developer mode for easier testing with the webapp
        server.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # # Add an endpoint to get the logs - (directly calling the FastAPI decorator)
    server.app.get("/log/")(retrieve_log)
    server.app.get("/logfile/")(retrieve_log_from_file)


def _get_scans_dir(config: dict) -> Optional[str]:
    """Read the config and return the scans directory.

    Return is None if there is no smart_scan thing loaded.
    """
    if "smart_scan" in config["things"]:
        try:
            return config["things"]["smart_scan"]["kwargs"]["scans_folder"]
        except KeyError as e:
            msg = "Configuration error: smart scan should have scans_folder kwarg set"
            raise RuntimeError(msg) from e
    return None


def serve_from_cli(argv: Optional[list[str]] = None) -> None:
    """Start the server from the command line."""
    args = lt.cli.parse_args(argv)

    log_config = copy(uvicorn.config.LOGGING_CONFIG)
    log_config["loggers"]["uvicorn"]["propagate"] = True
    log_config["loggers"]["uvicorn.access"]["propagate"] = True

    # Create server and lt_config vars before trying to configure so they are defined
    # if fallback is needed before they are set.
    lt_config = None
    server = None
    try:
        lt_config, internal_config = _full_config_from_args(args)

        server = lt.ThingServer.from_config(lt_config)
        customise_server(
            server, internal_config["log_folder"], internal_config["scans_folder"]
        )

        uvicorn.run(
            server.app,
            host=args.host,
            port=args.port,
            log_config=log_config,
            timeout_graceful_shutdown=2,
        )

    except BaseException as e:
        if args.fallback:
            # Allow printing to the terminal for fallback errors so they are not
            # presented in the fallback logs.
            print(f"Error: {e}")  # noqa: T201
            print("Starting fallback server.")  # noqa: T201
            try:
                log_history = GRADIENT_HANDLER.log_history
            except BaseException:
                # If log history fails for any reason carry on.
                log_history = None

            app = fallback.app
            app.set_context(
                fallback.FallbackContext(
                    server=server, config=lt_config, error=e, log_history=log_history
                )
            )
            uvicorn.run(
                app,
                host=args.host,
                port=args.port,
                log_config=log_config,
            )
        else:
            raise e


def _full_config_from_args(args: Namespace) -> tuple[ThingServerConfig, dict[str, Any]]:
    """Load configuration from LabThings args allowing patching.

    This returns the labthings ThingServerConfig model and a dictionary of the config
    for the Gradient device.

    This provides similar functionarlity to lt.cli.config_from_args except allows the
    configuration file to specify a base config, and optionally patches.
    """
    internal_config = {"log_folder": "./gradient_server/logs", "scans_folder": None}
    # If no config file specified let LabThings handle it.
    if not args.config:
        return lt.cli.config_from_args(args), internal_config

    patched_config = load_patched_config(args.config)
    log_folder = patched_config.pop("log_folder", None)
    if log_folder is not None:
        internal_config["log_folder"] = log_folder
    scans_folder = _get_scans_dir(patched_config)
    if scans_folder is not None:
        internal_config["scans_folder"] = scans_folder
    return ThingServerConfig(**patched_config), internal_config
