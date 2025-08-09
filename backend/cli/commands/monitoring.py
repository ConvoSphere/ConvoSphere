"""Monitoring commands."""

import sys

from cli.utils.output import print_error, print_info, print_success

# Constants
HEALTH_THRESHOLD_PERCENT = 80


class MonitoringCommands:
    """Monitoring commands."""

    def health(self) -> None:
        """Check system health."""
        try:
            import psutil
            from app.core.database import get_db
            from sqlalchemy import text

            print_info("System Health Check")
            print("-" * 50)

            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            print(f"CPU Usage: {cpu_percent}%")
            print(
                f"Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)"
            )
            print(
                f"Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"
            )

            # Database health
            try:
                db = next(get_db())
                result = db.execute(text("SELECT 1"))
                result.fetchone()
                db.close()
                print_success("Database: OK")
            except Exception as e:
                print_error(f"Database: ERROR - {str(e)}")

            # Overall health
            if cpu_percent < HEALTH_THRESHOLD_PERCENT and memory.percent < HEALTH_THRESHOLD_PERCENT and disk.percent < HEALTH_THRESHOLD_PERCENT:
                print_success("System Health: GOOD")
            else:
                print_error("System Health: WARNING - High resource usage")

        except Exception as e:
            print_error(f"Health check failed: {str(e)}")
            sys.exit(1)

    def logs(self, lines: int = 50, level: str = "INFO") -> None:
        """Show recent logs."""
        try:
            import os

            # Try to find log files
            log_files = []
            possible_log_dirs = ["./logs", "/var/log", "/tmp"]

            for log_dir in possible_log_dirs:
                if os.path.exists(log_dir):
                    for file in os.listdir(log_dir):
                        if file.endswith(".log"):
                            log_files.append(os.path.join(log_dir, file))

            if not log_files:
                print_info("No log files found")
                return

            print_info(f"Recent logs (last {lines} lines):")
            print("-" * 80)

            for log_file in log_files[:3]:  # Show max 3 log files
                if os.path.exists(log_file):
                    print_info(f"Log file: {log_file}")
                    try:
                        with open(log_file) as f:
                            all_lines = f.readlines()
                            recent_lines = (
                                all_lines[-lines:]
                                if len(all_lines) > lines
                                else all_lines
                            )

                            for line in recent_lines:
                                if level in line.upper():
                                    print(line.strip())
                    except Exception as e:
                        print_error(f"Failed to read log file {log_file}: {str(e)}")

        except Exception as e:
            print_error(f"Failed to show logs: {str(e)}")
            sys.exit(1)

    def containers(self) -> None:
        """Show Docker container status."""
        try:
            import subprocess

            print_info("Docker Container Status")
            print("-" * 50)

            try:
                result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "-a",
                        "--format",
                        "table {{.Names}}\t{{.Status}}\t{{.Ports}}",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print(result.stdout)
            except subprocess.CalledProcessError:
                print_error("Docker not available or not running")
            except FileNotFoundError:
                print_error("Docker command not found")

        except Exception as e:
            print_error(f"Failed to check containers: {str(e)}")
            sys.exit(1)
