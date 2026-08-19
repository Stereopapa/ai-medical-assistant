"""System resource monitor adapter using psutil and pynvml."""

from __future__ import annotations

import threading
import time
from typing import Any

import psutil
import pynvml

from src.domain.models import ResourceUsageMetrics
from src.domain.ports import ResourceMonitorPort

_BYTES_PER_MB: float = 1024 * 1024


class SystemMonitorAdapter(ResourceMonitorPort):
    """Monitors RAM, CPU, and optionally VRAM usage during model inference.

    Uses psutil for system-wide RAM and CPU metrics. GPU VRAM is sampled
    via pynvml when available; otherwise it falls back to 0.0.
    """

    def __init__(self, sampling_interval_sec: float = 0.1) -> None:
        """Initialize the monitor and detect GPU availability.

        Args:
            sampling_interval_sec: Delay between consecutive resource samples.
        """
        self._sampling_interval_sec = sampling_interval_sec
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._ram_samples: list[float] = []
        self._vram_samples: list[float] = []
        self._cpu_samples: list[float] = []
        self._nvml_handle = self._init_nvml()

    @staticmethod
    def _init_nvml() -> Any | None:
        """Initialize NVML and return a GPU handle, or None if unavailable."""
        try:
            pynvml.nvmlInit()
            if pynvml.nvmlDeviceGetCount() == 0:
                return None
            return pynvml.nvmlDeviceGetHandleByIndex(0)
        except pynvml.NVMLError:
            return None

    def start_recording(self) -> None:
        """Begin recording resource usage on a background thread."""
        self._stop_event.clear()
        self._ram_samples.clear()
        self._vram_samples.clear()
        self._cpu_samples.clear()
        # Prime the CPU measurement so the first sample is meaningful.
        psutil.cpu_percent(interval=None)
        self._thread = threading.Thread(
            target=self._sampling_loop, daemon=True
        )
        self._thread.start()

    def stop_recording(self) -> ResourceUsageMetrics:
        """Stop recording and return aggregated peak metrics.

        Returns:
            ResourceUsageMetrics with peak RAM, peak VRAM, and average
            CPU utilization across all samples.
        """
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)

        peak_ram = max(self._ram_samples, default=0.0)
        peak_vram = max(self._vram_samples, default=0.0)
        avg_cpu = (
            sum(self._cpu_samples) / len(self._cpu_samples)
            if self._cpu_samples
            else 0.0
        )

        return ResourceUsageMetrics(
            ram_used_mb=round(peak_ram, 2),
            vram_used_mb=round(peak_vram, 2),
            cpu_percent=round(avg_cpu, 2),
        )

    def _sampling_loop(self) -> None:
        """Continuously sample resource usage until stopped."""
        while not self._stop_event.is_set():
            self._ram_samples.append(
                psutil.virtual_memory().used / _BYTES_PER_MB
            )
            self._cpu_samples.append(psutil.cpu_percent(interval=None))
            self._vram_samples.append(self._read_vram_mb())
            time.sleep(self._sampling_interval_sec)

    def _read_vram_mb(self) -> float:
        """Return current VRAM usage in MB, or 0.0 when no GPU is present."""
        if self._nvml_handle is None:
            return 0.0
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self._nvml_handle)
            return mem_info.used / _BYTES_PER_MB  # type: ignore[no-any-return]
        except pynvml.NVMLError:
            return 0.0

    def __del__(self) -> None:
        """Shut down NVML cleanly if it was initialized."""
        if self._nvml_handle is not None:
            try:
                pynvml.nvmlShutdown()
            except pynvml.NVMLError:
                pass
