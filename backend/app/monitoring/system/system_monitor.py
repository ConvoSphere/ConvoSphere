"""
System monitoring functionality.

This module provides system-level monitoring including CPU, memory,
disk, and network metrics collection.
"""

import psutil
from typing import Any

from loguru import logger


class SystemMonitor:
    """Monitors system-level metrics."""

    def __init__(self):
        """Initialize system monitor."""
        self._last_network_io = psutil.net_io_counters()

    def get_system_metrics(self) -> dict[str, float]:
        """Get current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_freq_current = cpu_freq.current if cpu_freq else 0.0

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024 ** 3)  # GB
            memory_used = memory.used / (1024 ** 3)  # GB
            memory_total = memory.total / (1024 ** 3)  # GB

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024 ** 3)  # GB
            disk_used = disk.used / (1024 ** 3)  # GB
            disk_total = disk.total / (1024 ** 3)  # GB

            # Network metrics
            network_io = psutil.net_io_counters()
            network_bytes_sent = network_io.bytes_sent
            network_bytes_recv = network_io.bytes_recv
            network_packets_sent = network_io.packets_sent
            network_packets_recv = network_io.packets_recv

            # Calculate network rates if we have previous data
            network_send_rate = 0.0
            network_recv_rate = 0.0
            if hasattr(self, '_last_network_io') and self._last_network_io:
                time_diff = 1.0  # Assuming 1 second interval
                network_send_rate = (network_bytes_sent - self._last_network_io.bytes_sent) / time_diff
                network_recv_rate = (network_bytes_recv - self._last_network_io.bytes_recv) / time_diff

            self._last_network_io = network_io

            # Load average (Unix-like systems)
            try:
                load_avg = psutil.getloadavg()
                load_avg_1min = load_avg[0]
                load_avg_5min = load_avg[1]
                load_avg_15min = load_avg[2]
            except AttributeError:
                # Windows doesn't have load average
                load_avg_1min = 0.0
                load_avg_5min = 0.0
                load_avg_15min = 0.0

            return {
                # CPU metrics
                "cpu_percent": cpu_percent,
                "cpu_count": float(cpu_count),
                "cpu_freq_mhz": cpu_freq_current,
                "load_avg_1min": load_avg_1min,
                "load_avg_5min": load_avg_5min,
                "load_avg_15min": load_avg_15min,

                # Memory metrics
                "memory_percent": memory_percent,
                "memory_available_gb": memory_available,
                "memory_used_gb": memory_used,
                "memory_total_gb": memory_total,

                # Disk metrics
                "disk_percent": disk_percent,
                "disk_free_gb": disk_free,
                "disk_used_gb": disk_used,
                "disk_total_gb": disk_total,

                # Network metrics
                "network_bytes_sent": float(network_bytes_sent),
                "network_bytes_recv": float(network_bytes_recv),
                "network_packets_sent": float(network_packets_sent),
                "network_packets_recv": float(network_packets_recv),
                "network_send_rate_bps": network_send_rate,
                "network_recv_rate_bps": network_recv_rate,
            }

        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}

    def get_detailed_system_info(self) -> dict[str, Any]:
        """Get detailed system information."""
        try:
            # Basic system info
            system_info = {
                "platform": psutil.sys.platform,
                "python_version": psutil.sys.version,
                "hostname": psutil.gethostname(),
            }

            # CPU info
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "cpu_freq": {},
                "cpu_stats": {},
            }

            # CPU frequency info
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    cpu_info["cpu_freq"] = {
                        "current_mhz": cpu_freq.current,
                        "min_mhz": cpu_freq.min,
                        "max_mhz": cpu_freq.max,
                    }
            except Exception:
                pass

            # CPU stats
            try:
                cpu_stats = psutil.cpu_stats()
                cpu_info["cpu_stats"] = {
                    "ctx_switches": cpu_stats.ctx_switches,
                    "interrupts": cpu_stats.interrupts,
                    "soft_interrupts": cpu_stats.soft_interrupts,
                    "syscalls": cpu_stats.syscalls,
                }
            except Exception:
                pass

            # Memory info
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": memory.total / (1024 ** 3),
                "available_gb": memory.available / (1024 ** 3),
                "used_gb": memory.used / (1024 ** 3),
                "free_gb": memory.free / (1024 ** 3),
                "percent": memory.percent,
            }

            # Disk info
            disk_info = {}
            try:
                disk_partitions = psutil.disk_partitions()
                for partition in disk_partitions:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_info[partition.mountpoint] = {
                            "device": partition.device,
                            "fstype": partition.fstype,
                            "total_gb": usage.total / (1024 ** 3),
                            "used_gb": usage.used / (1024 ** 3),
                            "free_gb": usage.free / (1024 ** 3),
                            "percent": usage.percent,
                        }
                    except PermissionError:
                        # Skip partitions we can't access
                        continue
            except Exception:
                pass

            # Network info
            network_info = {}
            try:
                network_addrs = psutil.net_if_addrs()
                for interface, addrs in network_addrs.items():
                    network_info[interface] = []
                    for addr in addrs:
                        network_info[interface].append({
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        })
            except Exception:
                pass

            return {
                "system": system_info,
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "network": network_info,
            }

        except Exception as e:
            logger.error(f"Failed to get detailed system info: {e}")
            return {}

    def get_process_metrics(self, pid: int | None = None) -> dict[str, float]:
        """Get metrics for a specific process or current process."""
        try:
            if pid is None:
                process = psutil.Process()
            else:
                process = psutil.Process(pid)

            # CPU metrics
            cpu_percent = process.cpu_percent()
            cpu_times = process.cpu_times()
            cpu_times_user = cpu_times.user
            cpu_times_system = cpu_times.system

            # Memory metrics
            memory_info = process.memory_info()
            memory_rss = memory_info.rss / (1024 ** 2)  # MB
            memory_vms = memory_info.vms / (1024 ** 2)  # MB
            memory_percent = process.memory_percent()

            # IO metrics
            try:
                io_counters = process.io_counters()
                io_read_bytes = io_counters.read_bytes / (1024 ** 2)  # MB
                io_write_bytes = io_counters.write_bytes / (1024 ** 2)  # MB
                io_read_count = io_counters.read_count
                io_write_count = io_counters.write_count
            except psutil.AccessDenied:
                io_read_bytes = 0.0
                io_write_bytes = 0.0
                io_read_count = 0
                io_write_count = 0

            # Thread count
            num_threads = process.num_threads()

            # File descriptors (Unix-like systems)
            try:
                num_fds = process.num_fds()
            except AttributeError:
                num_fds = 0

            return {
                "cpu_percent": cpu_percent,
                "cpu_times_user": cpu_times_user,
                "cpu_times_system": cpu_times_system,
                "memory_rss_mb": memory_rss,
                "memory_vms_mb": memory_vms,
                "memory_percent": memory_percent,
                "io_read_mb": io_read_bytes,
                "io_write_mb": io_write_bytes,
                "io_read_count": float(io_read_count),
                "io_write_count": float(io_write_count),
                "num_threads": float(num_threads),
                "num_fds": float(num_fds),
            }

        except Exception as e:
            logger.error(f"Failed to get process metrics: {e}")
            return {}