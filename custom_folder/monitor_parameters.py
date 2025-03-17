import os
import psutil
import shutil
import docker
import subprocess


def get_per_container_memory_usage():
    try:
        # Initialize Docker client
        client = docker.from_env()

        # Get all containers (running only)
        containers = client.containers.list()

        # Prepare the result
        result = []
        for container in containers:
            # Get memory usage from container stats
            stats = container.stats(stream=False)
            mem_usage = stats["memory_stats"]["usage"]  # Current memory usage in bytes
            mem_limit = stats["memory_stats"].get("limit", None)  # Memory limit in bytes (if set)

            # Convert to MB for readability
            mem_usage_mb = round(mem_usage / (1024 * 1024), 2)
            mem_limit_mb = round(mem_limit / (1024 * 1024), 2) if mem_limit else None
            result.append({
                'value': mem_usage_mb,
                'label': [container.name, container.id[:12], 'memory_usage']
            })

        return {"result": result, "labels": ["name", "id", "memory_limit_mb"]}

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_total_disk_usage(path):
    total, _ ,_ = shutil.disk_usage(path)
    return total


def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (FileNotFoundError, PermissionError):
                # Skip inaccessible files
                continue
    print("total size",total_size)
    return total_size

def collect_filesystem_disk():
    df_output = subprocess.check_output(['df', '-h'], text=True)
    lines = df_output.strip().split('\n')
    lines.pop(0)
    return {
    'result': [{'label': line.split()[5], 'value': line.split()[4]} for line in lines],
    'labels': ['path']
    }
def total_memory_usage():
    return {
    'result': [
        {'label': 'mem_used', 'value': psutil.virtual_memory().percent}
    ],
    'labels': ['memory']
    }
def network_io():
    net_io = psutil.net_io_counters()
    return {
    'result': [
        {'label': 'bytes_sent', 'value': format_bytes(net_io.bytes_sent)},
        {'label': 'bytes_received', 'value': format_bytes(net_io.bytes_recv)},
        {'label': 'packets_sent', 'value': format_bytes(net_io.packets_sent)},
        {'label': 'packets_received', 'value': format_bytes(net_io.packets_recv)}
    ],
    'labels': ['networkio']
    }
def collect_disk_metrics():
    memory_info = psutil.virtual_memory()
    return collect_filesystem_disk()



# print(get_per_container_memory_usage())