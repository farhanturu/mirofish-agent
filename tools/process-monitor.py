#!/usr/bin/env python3
"""
MiroFish — Process Monitor
Lihat proses yang sedang berjalan di lingkungan MiroFish.
"""

import os
import json
import subprocess
import pwd
from pathlib import Path
from datetime import datetime

BACKEND_URL = "http://localhost:5001"


def color(text, code=""):
    colors = {
        'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
        'cyan': '\033[96m', 'blue': '\033[94m', 'bold': '\033[1m',
        'dim': '\033[2m', 'reset': '\033[0m', 'purple': '\033[95m'
    }
    return f"{colors.get(code, '')}{text}{colors['reset']}"


def fmt_time(ts):
    try:
        return datetime.fromtimestamp(float(ts)).strftime('%H:%M:%S')
    except:
        return str(ts)[:8]


def get_username(uid):
    try:
        return pwd.getpwuid(uid).pw_name
    except:
        return str(uid)


def get_processes():
    """Ambil daftar proses."""
    processes = []
    
    try:
        result = subprocess.run(
            ['ps', 'aux', '--sort=-%cpu'],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            header = lines[0]
            for line in lines[1:]:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    proc = {
                        'user': parts[0],
                        'pid': parts[1],
                        'cpu': float(parts[2]),
                        'mem': float(parts[3]),
                        'vsz': parts[4],
                        'rss': parts[5],
                        'tty': parts[6],
                        'stat': parts[7],
                        'start': parts[8],
                        'time': parts[9],
                        'command': parts[10][:100]
                    }
                    processes.append(proc)
    except:
        pass
    
    return processes


def filter_mirofish(processes):
    """Filter proses yang terkait MiroFish."""
    keywords = ['mirofish', 'flask', 'vite', 'python.*run.py', 'npm.*dev', 
                'node.*dashboard', 'uvicorn', 'gunicorn', 'oasis']
    related = []
    for p in processes:
        cmd = p['command'].lower()
        if any(k in cmd for k in keywords):
            related.append(p)
    return related


def filter_by_port():
    """Cari proses yang mendengarkan di port tertentu."""
    services = []
    try:
        result = subprocess.run(
            ['ss', '-tlnp'], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split('\n'):
            if 'LISTEN' in line:
                parts = line.split()
                port = ''
                pid = ''
                for part in parts:
                    if part.count(':') >= 1 and not part.startswith('users'):
                        # Extract port from address:port
                        port_part = part.rsplit(':', 1)[-1]
                        if port_part.isdigit():
                            port = port_part
                    if 'pid=' in part:
                        pid_match = __import__('re').search(r'pid=(\d+)', part)
                        if pid_match:
                            pid = pid_match.group(1)
                if port:
                    services.append({
                        'port': port,
                        'pid': pid,
                        'line': line.strip()
                    })
    except:
        pass
    return services


def show_processes():
    """Tampilkan semua proses yang berjalan."""
    print(color(f"\n{'='*70}", "cyan"))
    print(color(f"  📊 MONITOR PROSES MIROFISH", "bold"))
    print(color(f"{'='*70}", "cyan"))
    print()

    all_procs = get_processes()
    mirofish_procs = filter_mirofish(all_procs)
    
    # Cek MiroFish backend
    print(color(f"  ── Layanan MiroFish ──", "green"))
    try:
        import urllib.request
        req = urllib.request.Request(f"{BACKEND_URL}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            if data.get('status') == 'ok':
                print(f"    {color('● Backend API', 'green')}  {color(':5001', 'dim')}  Berjalan")
    except:
        print(f"    {color('● Backend API', 'red')}  {color(':5001', 'dim')}  Mati")
    
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:3000/")
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"    {color('● Frontend', 'green')}  {color(':3000', 'dim')}  Berjalan (HTTP {resp.status})")
    except:
        print(f"    {color('● Frontend', 'red')}  {color(':3000', 'dim')}  Mati")
    
    print()
    
    # Proses backend
    print(color(f"  ── Proses Aktif ──", "green"))
    print(f"    {'PID':<8}{'CPU':<6}{'MEM':<6}{'TIME':<8}{'COMMAND':<30}")
    print(f"    {'─'*60}")
    
    for p in mirofish_procs[:15]:
        pid = p['pid']
        cpu = f"{p['cpu']:.1f}"
        mem = f"{p['mem']:.1f}"
        runtime = p['time']
        cmd = p['command'][:50]
        status = color('●', 'green') if p['stat'] in ('R', 'R+', 'Ss', 'S', 'Ss+') else color('○', 'dim')
        
        print(f"    {status} {pid:<6} {cpu:<5} {mem:<5} {runtime:<8} {color(cmd, 'bold')}")
    
    print()
    
    # Resource usage
    print(color(f"  ── Resource ──", "green"))
    try:
        # CPU
        cpu_load = subprocess.run(['uptime'], capture_output=True, text=True, timeout=3)
        load = cpu_load.stdout.strip().split('load average: ')[-1] if 'load average' in cpu_load.stdout else '-'
        
        # Memory
        mem_info = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=3)
        mem_lines = mem_info.stdout.split('\n')
        mem_total = mem_lines[1].split()[1] if len(mem_lines) > 1 else '-'
        mem_used = mem_lines[1].split()[2] if len(mem_lines) > 1 else '-'
        mem_percent = mem_lines[1].split()[2] if len(mem_lines) > 1 else '-'
        
        # Hitung persentase
        try:
            parts = mem_info.stdout.split('\n')[1].split()
            total_kb = int(parts[1])
            used_kb = int(parts[2])
            mem_pct = used_kb / total_kb * 100
        except:
            mem_pct = 0
        
        # Disk
        disk = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=3)
        disk_line = disk.stdout.split('\n')[1].split() if len(disk.stdout.split('\n')) > 1 else []
        
        print(f"    CPU Load:   {load}")
        print(f"    Memory:     {mem_used}/{mem_total} ({mem_pct:.1f}%)")
        if disk_line:
            print(f"    Disk:       {disk_line[2]}/{disk_line[1]} ({disk_line[4]})")
    except:
        pass
    
    print()
    
    # Port yang digunakan
    print(color(f"  ── Port ──", "green"))
    services = filter_by_port()
    found = False
    for s in services:
        if s['port'] in ('3000', '5001', '9867'):
            found = True
            label = {'3000': 'Frontend', '5001': 'Backend', '9867': 'PinchTab'}.get(s['port'], 'Service')
            print(f"    :{s['port']} → {color(label, 'bold')} (PID: {s['pid']})")
    
    if not found:
        print(color(f"    (tidak ada port MiroFish terdeteksi)", "dim"))
    
    print()


if __name__ == '__main__':
    show_processes()
