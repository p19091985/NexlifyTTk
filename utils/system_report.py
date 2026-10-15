from __future__ import annotations
import platform, shutil, subprocess, logging
from typing import Dict, List, Optional
import psutil
_logger=logging.getLogger(__name__)
def run_command(command: List[str], timeout: int = 5) -> Optional[str]:
    """Run a command and return stripped stdout when it succeeds."""
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        return None

    if completed.returncode != 0:
        return None

    output = completed.stdout.strip()
    return output or None

def collect_computer_info() -> Dict[str, object]:
    """Collect a best-effort report about the computer, including GPU."""
    uname = platform.uname()
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    boot = psutil.boot_time()

    report = {
        "system": {
            "Sistema": uname.system,
            "Versao": uname.version,
            "Release": uname.release,
            "Arquitetura": platform.machine(),
            "Hostname": uname.node,
            "Python": platform.python_version(),
        },
        "cpu": {
            "Modelo": platform.processor() or "Nao informado pelo sistema",
            "Nucleos fisicos": psutil.cpu_count(logical=False),
            "Nucleos logicos": psutil.cpu_count(logical=True),
            "Uso atual (%)": psutil.cpu_percent(interval=0.2),
            "Frequencia atual (MHz)": _cpu_freq_value("current"),
            "Frequencia maxima (MHz)": _cpu_freq_value("max"),
        },
        "memory": {
            "RAM total (GB)": round(vm.total / (1024 ** 3), 2),
            "RAM disponivel (GB)": round(vm.available / (1024 ** 3), 2),
            "RAM em uso (%)": vm.percent,
            "Swap total (GB)": round(swap.total / (1024 ** 3), 2),
            "Swap em uso (%)": swap.percent,
        },
        "storage": _collect_storage_info(),
        "gpu": _collect_gpu_info(),
        "boot_time": boot,
    }
    return report

def format_computer_report(report: Dict[str, object]) -> str:
    """Format the computer report into a readable text block."""
    lines: List[str] = []

    lines.extend([
        "SISTEMA",
    ])
    for key, value in report["system"].items():
        lines.append(f"{key}: {value}")

    lines.extend([
        "",
        "CPU",
    ])
    for key, value in report["cpu"].items():
        lines.append(f"{key}: {value}")

    lines.extend([
        "",
        "MEMORIA",
    ])
    for key, value in report["memory"].items():
        lines.append(f"{key}: {value}")

    lines.extend([
        "",
        "ARMAZENAMENTO",
    ])
    storage_items = report.get("storage") or []
    if storage_items:
        for item in storage_items:
            lines.append(
                f"{item['device']} | montagem={item['mountpoint']} | "
                f"fs={item['fstype']} | total={item['total_gb']} GB | "
                f"livre={item['free_gb']} GB | uso={item['used_percent']}%"
            )
    else:
        lines.append("Nenhuma particao legivel foi encontrada.")

    lines.extend([
        "",
        "GPU",
    ])
    gpu_items = report.get("gpu") or []
    if gpu_items:
        for idx, gpu in enumerate(gpu_items, start=1):
            lines.append(f"GPU {idx}:")
            for key, value in gpu.items():
                lines.append(f"  {key}: {value}")
    else:
        lines.append("Nenhuma GPU foi identificada pelo sistema.")

    return "\n".join(lines)

def _cpu_freq_value(field: str):
    freq = psutil.cpu_freq()
    if not freq:
        return "N/A"
    value = getattr(freq, field, None)
    if value is None:
        return "N/A"
    return round(value, 2)

def _collect_storage_info() -> List[Dict[str, object]]:
    disks: List[Dict[str, object]] = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        disks.append({
            "device": part.device,
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "used_percent": usage.percent,
        })
    return disks

def _collect_gpu_info() -> List[Dict[str, object]]:
    system = platform.system()

    if system == "Windows":
        return _collect_gpu_windows()
    if system == "Darwin":
        return _collect_gpu_macos()
    return _collect_gpu_linux()

def _collect_gpu_linux() -> List[Dict[str, object]]:
    gpus = _collect_gpu_nvidia_smi()
    if gpus:
        return gpus

    output = run_command(["lspci"])
    if output:
        lines = [
            line.strip() for line in output.splitlines()
            if any(tag in line.lower() for tag in ("vga compatible controller", "3d controller", "display controller"))
        ]
        if lines:
            return [{"Descricao": line} for line in lines]

    output = run_command(["glxinfo", "-B"])
    if output:
        gpu_info: Dict[str, str] = {}
        for line in output.splitlines():
            if ":" not in line:
                continue
            key, value = [chunk.strip() for chunk in line.split(":", 1)]
            if key in {"Vendor", "Device", "OpenGL renderer string", "OpenGL vendor string", "OpenGL version string"}:
                gpu_info[key] = value
        if gpu_info:
            return [gpu_info]

    return []

def _collect_gpu_windows() -> List[Dict[str, object]]:
    output = run_command([
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name,AdapterRAM,DriverVersion | "
            "ConvertTo-Json -Compress"
        ),
    ], timeout=10)
    if not output:
        return []

    try:
        import json
        data = json.loads(output)
    except Exception:
        return [{"Descricao": output}]

    if isinstance(data, dict):
        data = [data]

    gpus = []
    for item in data:
        ram = item.get("AdapterRAM")
        gpus.append({
            "Nome": item.get("Name") or "N/A",
            "Memoria dedicada (GB)": round(ram / (1024 ** 3), 2) if isinstance(ram, (int, float)) else "N/A",
            "Driver": item.get("DriverVersion") or "N/A",
        })
    return gpus

def _collect_gpu_macos() -> List[Dict[str, object]]:
    output = run_command(["system_profiler", "SPDisplaysDataType"], timeout=15)
    if not output:
        return []

    gpu_blocks: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":") and "Chipset Model" not in line and "VRAM" not in line and "Vendor" not in line:
            if current:
                gpu_blocks.append(current)
                current = {}
            current["Nome"] = line[:-1]
            continue
        if ":" in line:
            key, value = [chunk.strip() for chunk in line.split(":", 1)]
            if key in {"Chipset Model", "Vendor", "VRAM (Dynamic, Max)", "VRAM (Total)"}:
                current[key] = value
    if current:
        gpu_blocks.append(current)
    return gpu_blocks

def _collect_gpu_nvidia_smi() -> List[Dict[str, object]]:
    if not shutil.which("nvidia-smi"):
        return []

    output = run_command([
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    ], timeout=10)
    if not output:
        return []

    gpus = []
    for line in output.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            continue
        gpus.append({
            "Nome": parts[0],
            "Driver": parts[1],
            "Memoria total (MB)": parts[2],
        })
    return gpus
