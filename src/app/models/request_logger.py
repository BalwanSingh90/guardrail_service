# src/app/models/request_logger.py

"""
Request Logger Module

This module provides functionality for logging request-specific data in JSON format.
It creates a separate JSON log file for each request, tracking various stages of
request processing with timestamps and associated data. This is useful for
debugging, auditing, and monitoring request flows.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.app.core.config import Settings
from src.app.core.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Initialize settings
settings = Settings()


class RequestLogger:
    """
    A class for logging request-specific data in JSON format.

    This class creates and manages JSON log files for individual requests,
    allowing for detailed tracking of request processing stages, timestamps,
    and associated data. Each request gets its own log file, making it easy
    to track the complete lifecycle of a request.

    Attributes:
        request_id (str): Unique identifier for the request
        log_dir (Path): Directory where log files are stored
        log_file (Path): Path to the specific log file for this request
        log_data (Dict): In-memory storage of the log data structure
    """

    def __init__(self, request_id: str):
        """
        Initialize a new RequestLogger instance.

        Args:
            request_id (str): Unique identifier for the request to be logged

        Note:
            Creates the log directory if it doesn't exist and initializes
            the log data structure with request metadata.
        """
        self.request_id = request_id
        self.log_dir = Path(settings.log_dir)

        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Log directory ensured at: {self.log_dir}")
        except Exception as e:
            logger.error(f"Failed to create log directory {self.log_dir}: {e!s}")
            raise

        self.log_file = self.log_dir / f"request_{request_id}.json"
        logger.info(f"Initializing request logger for request_id: {request_id}")

        # Initialize log data structure
        self.log_data: dict[str, Any] = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "stages": [],
        }

        # Create initial log file
        self._write_log_file()
        logger.debug(f"Created initial log file at: {self.log_file}")

    def log_stage(self, stage_name: str, data: Dict[str, Any]) -> None:
        """
        Log a new stage in the request processing.

        Args:
            stage_name (str): Name of the processing stage
            data (Dict[str, Any]): Associated data for this stage

        Note:
            Appends a new stage entry to the log and writes the updated
            log data to the JSON file. Each stage includes a timestamp
            and the provided data.
        """
        logger.debug(f"Logging stage '{stage_name}' for request {self.request_id}")

        entry = {
            "stage": stage_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        self.log_data["stages"].append(entry)
        self._write_log_file()
        logger.debug(f"Successfully logged stage '{stage_name}'")

    def _write_log_file(self) -> None:
        """
        Write the current log data to the JSON file.

        This is an internal method that handles the actual file writing
        operation. It includes error handling and logging.

        Raises:
            IOError: If there are issues writing to the log file
        """
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.log_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Successfully wrote to log file: {self.log_file}")
        except Exception as e:
            logger.error(f"Failed to write to log file {self.log_file}: {e!s}")
            raise

    def get_latest_stage(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently logged stage.

        Returns:
            Optional[Dict[str, Any]]: The latest stage entry if any stages exist,
                                     None otherwise
        """
        if not self.log_data["stages"]:
            logger.debug("No stages logged yet")
            return None
        return self.log_data["stages"][-1]

    def get_stage_count(self) -> int:
        """
        Get the total number of stages logged.

        Returns:
            int: Number of stages logged for this request
        """
        return len(self.log_data["stages"])

    def get_logs(self) -> Optional[dict[str, Any]]:
        """
        Return the entire log data dictionary, or None if not available.
        """
        if self.log_data:
            return self.log_data
        return None
