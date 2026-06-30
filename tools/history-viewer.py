#!/usr/bin/env python3
"""
MiroFish — History Viewer
Lihat semua proyek, simulasi, lingkungan, report, dan grafik pengetahuan.
Menggabungkan semua data dari berbagai API endpoint.
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

BACKEND_URL = "http://localhost:5001"
UPLOADS_DIR = Path.home() / "MiroFish" / "backend" / "uploads"
SIMULATIONS_DIR = UPLOADS_DIR / "simulations"
REPORTS_DIR = UPLOADS_DIR / "reports"


def api_get(path, method='GET'):
    """Request ke MiroFish API."""
    import urllib.request
    try:
        url = f"{BACKEND_URL}{path}"
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.request.HTTPError as e:
        if e.code == 404:
            return {"error": "not_found"}
        body = e.read().decode()[:200]
        return {"error": f"HTTP {e.code}: {body}"}
    except Exception as e:
        return {"error": str(e)}


def color(text, code=""):
    """Warnai teks untuk terminal."""
    colors = {
        'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
        'cyan': '\033[96m', 'blue': '\033[94m', 'bold': '\033[1m',
        'dim': '\033[2m', 'reset': '\033[0m'
    }
    return f"{colors.get(code, '')}{text}{colors['reset']}"


def fmt_time(t):
    """Format timestamp."""
    if not t:
        return "-"
    try:
        dt = datetime.fromisoformat(t.replace('Z', '+00:00').replace('T', ' ')[:19])
        return dt.strftime('%d/%m %H:%M')
    except:
        return str(t)[:16]


# =========================================================================
# 1. Lihat Semua Proyek
# =========================================================================
def list_projects():
    """Tampilkan semua proyek."""
    result = api_get("/api/graph/project/list")
    projects = result.get('data', [])

    if not projects:
        print(color("Belum ada proyek.", "yellow"))
        return

    print(color(f"\n{'='*60}", "cyan"))
    print(color(f"  📁 SEMUA PROYEK ({len(projects)})", "bold"))
    print(color(f"{'='*60}", "cyan"))
    print()

    for p in projects:
        pid = p.get('project_id', '?')
        name = p.get('project_name', 'Tanpa Nama')
        status = p.get('status', '?')
        created = fmt_time(p.get('created_at', ''))
        sim_count = len(p.get('simulations', []))
        graph_id = str(p.get('graph_id', '') or '')[:20]

        print(f"  {color(pid, 'cyan')}  {color(name, 'bold')}")
        print(f"     Status: {status}  |  Grafik: {graph_id}")
        print(f"     Dibuat: {created}  |  Simulasi: {sim_count}")
        print()


# =========================================================================
# 2. Detail Proyek
# =========================================================================
def show_project(project_id):
    """Tampilkan detail proyek."""
    result = api_get(f"/api/graph/project/{project_id}")
    p = result.get('data', {})

    if not p:
        print(color(f"Proyek {project_id} tidak ditemukan.", "red"))
        return

    name = p.get('project_name', 'Tanpa Nama')
    graph_id = p.get('graph_id', '-')
    status = p.get('status', '-')
    req = p.get('simulation_requirement', '-')[:200]
    files = p.get('files', [])
    created = fmt_time(p.get('created_at', ''))

    print(color(f"\n{'='*60}", "cyan"))
    print(color(f"  📁 PROYEK: {name}", "bold"))
    print(color(f"{'='*60}", "cyan"))
    print(f"  ID:       {color(project_id, 'dim')}")
    print(f"  Status:   {status}")
    print(f"  Grafik:   {graph_id}")
    print(f"  Dibuat:   {created}")
    print(f"  Dokumen:  {len(files)} file")
    print(f"  Tujuan:   {req}")
    print()

    # Tampilkan entitas grafik
    if graph_id and graph_id != '-':
        print(color(f"  ── Entitas Grafik ──", "green"))
        try:
            entities = api_get(f"/api/simulation/entities/{graph_id}")
            data = entities.get('data', {})
            if isinstance(data, dict):
                for etype, ents in data.items():
                    if isinstance(ents, list):
                        print(f"    {etype}: {len(ents)} entitas")
        except:
            pass
        print()


# =========================================================================
# 3. List Semua Simulasi
# =========================================================================
def list_simulations():
    """Tampilkan semua simulasi dengan detail."""
    result = api_get("/api/simulation/history")
    data = result.get('data', [])
    count = result.get('count', len(data))

    if not data:
        print(color("Belum ada simulasi.", "yellow"))
        return

    print(color(f"\n{'='*60}", "cyan"))
    print(color(f"  🎮 SEMUA SIMULASI ({count})", "bold"))
    print(color(f"{'='*60}", "cyan"))
    print()

    for s in data:
        sim_id = str(s.get('simulation_id', '') or '?')[:20]
        project_name = s.get('project_name', 'Tanpa Nama')
        status = s.get('status', '?')
        created = fmt_time(s.get('created_at', ''))
        agent_count = s.get('agent_count', s.get('expected_entities_count', '-'))
        rounds = s.get('max_rounds', '-')
        has_report = color("✓", "green") if s.get('report_id') else color("✗", "dim")

        print(f"  {color(sim_id, 'cyan')}  {color(project_name, 'bold')}")
        print(f"     Status: {status}  |  Agen: {agent_count}  |  Putaran: {rounds}  |  Report: {has_report}")
        print(f"     Dibuat: {created}")
        print()

        # Detail tambahan
        config = s.get('simulation_config', {})
        if config:
            hours = config.get('simulation_hours', '-')
            interval = config.get('interval_minutes', '-')
            platforms = []
            if config.get('enable_twitter'): platforms.append('Twitter')
            if config.get('enable_reddit'): platforms.append('Reddit')
            print(f"     Durasi: {hours}jam  |  Interval: {interval}min  |  Platform: {', '.join(platforms)}")
            print()


# =========================================================================
# 4. Detail Simulasi Lengkap
# =========================================================================
def show_simulation(sim_id, action_limit=10, post_limit=5):
    """Tampilkan detail lengkap simulasi."""
    result = api_get(f"/api/simulation/{sim_id}")
    s = result.get('data', {})

    if not s:
        print(color(f"Simulasi {sim_id} tidak ditemukan.", "red"))
        return

    status = s.get('status', '?')
    graph_id = s.get('graph_id', '-')
    config = s.get('simulation_config', {})
    profiles_path = SIMULATIONS_DIR / sim_id / "reddit_profiles.json"
    run_state = SIMULATIONS_DIR / sim_id / "run_state.json"
    state_file = SIMULATIONS_DIR / sim_id / "state.json"
    db_file = SIMULATIONS_DIR / sim_id / "twitter_simulation.db"
    log_file = SIMULATIONS_DIR / sim_id / "simulation.log"
    twitter_dir = SIMULATIONS_DIR / sim_id / "twitter"
    reddit_dir = SIMULATIONS_DIR / sim_id / "reddit"

    print(color(f"\n{'='*70}", "cyan"))
    print(color(f"  🎮 SIMULASI DETAIL", "bold"))
    print(color(f"{'='*70}", "cyan"))
    print(f"  ID:         {color(sim_id, 'dim')}")
    print(f"  Status:     {status}")
    print(f"  Grafik ID:  {graph_id}")
    print()

    # Konfigurasi
    if config:
        print(color(f"  ── Konfigurasi ──", "green"))
        for k, v in config.items():
            if isinstance(v, (str, int, float, bool)):
                print(f"    {k}: {v}")
        print()

    # Profil
    if profiles_path.exists():
        with open(profiles_path) as f:
            profiles = json.load(f)
        print(color(f"  ── Agen ({len(profiles)}) ──", "green"))
        for i, p in enumerate(profiles[:5]):
            if isinstance(p, dict):
                name = p.get('name', p.get('username', '?'))
                bio = p.get('bio', p.get('description', ''))[:80]
                age = p.get('age', '?')
                print(f"    {i+1}. {color(name, 'bold')} (usia {age}) - {bio}")
        if len(profiles) > 5:
            print(f"    ... dan {len(profiles)-5} lainnya")
        print()

    # Status Run
    if run_state.exists():
        with open(run_state) as f:
            rs = json.load(f)
        if rs:
            print(color(f"  ── Status Run ──", "green"))
            print(f"    Runner:    {rs.get('runner_status', '?')}")
            print(f"    PID:       {rs.get('process_pid', '-')}")
            print(f"    Putaran:   {rs.get('current_round', 0)}/{config.get('max_rounds', '?')}")
            print(f"    Progress:  {rs.get('progress_percent', 0):.1f}%")
            print(f"    Twitter:   {rs.get('twitter_actions_count', 0)} aksi")
            print(f"    Reddit:    {rs.get('reddit_actions_count', 0)} aksi")
            print(f"    Mulai:     {fmt_time(rs.get('started_at', ''))}")
            print()

    # Tampilkan aksi-aksi
    print(color(f"  ── Aksi Terbaru ──", "green"))
    try:
        actions = api_get(f"/api/simulation/{sim_id}/actions?limit={action_limit}")
        acts = actions.get('data', {}).get('actions', [])
        if acts:
            for a in acts[:action_limit]:
                if isinstance(a, dict):
                    agent_id = a.get('agent_id', '-')
                    action_type = a.get('action', a.get('action_type', '?'))
                    content = a.get('content', a.get('info', ''))[:120]
                    platform = a.get('platform', '-')
                    print(f"    [{platform}] Agent#{agent_id}: {color(action_type, 'yellow')} - {content}")
    except:
        pass
    print()

    # Tampilkan posting
    print(color(f"  ── Posting Twitter ──", "green"))
    try:
        posts = api_get(f"/api/simulation/{sim_id}/posts?limit={post_limit}")
        post_list = posts.get('data', {}).get('posts', [])
        if post_list:
            for p in post_list[:post_limit]:
                if isinstance(p, dict):
                    uname = p.get('user_name', '?')
                    content = p.get('content', '')[:150]
                    likes = p.get('num_likes', 0)
                    print(f"    {color(uname, 'bold')}: {content}")
                    print(f"    ❤️ {likes}  |  🕐 {fmt_time(p.get('created_at', ''))}")
                    print()
    except:
        pass

    # Log simulasi
    if log_file.exists():
        print(color(f"  ── Log Terakhir ──", "green"))
        with open(log_file) as f:
            lines = f.readlines()
        for line in lines[-10:]:
            print(f"    {line.strip()}")
        print()

    # File
    print(color(f"  ── File Data ──", "green"))
    for f in sorted(SIMULATIONS_DIR.glob(f"{sim_id}/*")):
        size = f.stat().st_size
        if f.is_file():
            print(f"    {f.name:40s} {size//1024:>6}KB")
    print()


# =========================================================================
# 5. Lihat Semua Report
# =========================================================================
def list_reports():
    """Tampilkan semua report."""
    result = api_get("/api/report/list")
    data = result.get('data', [])

    if not data:
        print(color("Belum ada report.", "yellow"))
        return

    print(color(f"\n{'='*60}", "cyan"))
    print(color(f"  📝 SEMUA REPORT ({len(data)})", "bold"))
    print(color(f"{'='*60}", "cyan"))
    print()

    for r in data:
        rid = str(r.get('report_id', '') or '?')[:20]
        sim_id = str(r.get('simulation_id', '') or '?')[:20]
        status = r.get('status', '?')
        sections = r.get('section_count', r.get('sections', 0))
        created = fmt_time(r.get('created_at', ''))

        print(f"  {color(rid, 'cyan')}")
        print(f"     Simulasi: {sim_id}  |  Status: {status}  |  Sections: {sections}")
        print(f"     Dibuat: {created}")
        print()


# =========================================================================
# 6. Laporan Lingkungan — Lihat Semua Data
# =========================================================================
def environment_report(full=False):
    """Laporan lengkap tentang lingkungan MiroFish."""
    print(color(f"\n{'='*70}", "cyan"))
    print(color(f"  🌐 LAPORAN LINGKUNGAN MIROFISH", "bold"))
    print(color(f"{'='*70}", "cyan"))
    print()

    # Cek backend
    health = api_get("/health")
    backend_ok = health.get('status') == 'ok'
    print(f"  Backend: {color('✓ Berjalan', 'green') if backend_ok else color('✗ Mati', 'red')}")
    if backend_ok:
        print(f"  Service: {health.get('service', '-')}")
    print()

    # Proyek
    projects = api_get("/api/graph/project/list").get('data', [])
    print(f"  📁 Proyek:          {color(len(projects), 'bold')}")
    for p in projects:
        pid = p.get('project_id', '?')
        name = str(p.get('project_name', '') or 'Tanpa Nama')[:40]
        status = p.get('status', '?')
        graph = p.get('graph_id', '-')
        if graph is None:
            graph = '-'
        graph = str(graph)[:16]
        print(f"    {color(pid, 'dim')}  {name}")
        print(f"      Status: {status}  Grafik: {graph}")
    print()

    # Simulasi
    sims = api_get("/api/simulation/history").get('data', [])
    print(f"  🎮 Simulasi:        {color(len(sims), 'bold')}")
    active = sum(1 for s in sims if s.get('status') in ('running', 'preparing', 'generating'))
    completed = sum(1 for s in sims if s.get('status') in ('completed', 'ready'))
    print(f"    Aktif: {active}  Selesai: {completed}")
    for s in sims:
        sid = str(s.get('simulation_id', '') or '?')[:16]
        name = str(s.get('project_name', '') or '-')[:40]
        status = s.get('status', '?')
        agents = s.get('expected_entities_count', '-')
        print(f"    {color(sid, 'dim')}  {name}")
        print(f"      Status: {status}  Agen: {agents}")
    print()

    # Report
    reports = api_get("/api/report/list").get('data', [])
    print(f"  📝 Report:          {color(len(reports), 'bold')}")
    for r in reports:
        rid = str(r.get('report_id', '') or '?')[:16]
        sim_id = str(r.get('simulation_id', '') or '?')[:16]
        status = r.get('status', '?')
        print(f"    {color(rid, 'dim')}  Sim: {sim_id}  Status: {status}")
    print()

    # Grafik
    graph_count = 0
    node_total = 0
    edge_total = 0
    for p in projects:
        gid = p.get('graph_id', '')
        if gid:
            try:
                gdata = api_get(f"/api/graph/data/{gid}").get('data', {})
                if isinstance(gdata, dict):
                    nodes = len(gdata.get('nodes', []))
                    edges = len(gdata.get('edges', []))
                    node_total += nodes
                    edge_total += edges
                    graph_count += 1
            except:
                pass
    print(f"  🔗 Grafik:          {color(graph_count, 'bold')}")
    print(f"    Total node: {node_total}  Edge: {edge_total}")
    print()

    # Database
    db_files = list(SIMULATIONS_DIR.rglob("*.db"))
    print(f"  💾 Database:        {color(len(db_files), 'bold')}")
    for db in db_files:
        try:
            conn = sqlite3.connect(db)
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            post_count = conn.execute("SELECT COUNT(*) FROM post").fetchone()[0]
            user_count = conn.execute("SELECT COUNT(*) FROM user").fetchone()[0]
            comment_count = conn.execute("SELECT COUNT(*) FROM comment").fetchone()[0]
            conn.close()
            print(f"    {db.parent.name}/{db.name}")
            print(f"      Users:{user_count}  Post:{post_count}  Comments:{comment_count}")
        except:
            pass
    print()


def delete_project(project_id):
    """Hapus proyek + grafik + simulasi terkait."""
    result = api_get(f"/api/graph/project/{project_id}")
    if 'error' in result:
        return print(color(f"❌ Gagal: {result['error']}", "red"))

    # Hapus grafik jika ada
    project = result.get('data', {})
    graph_id = project.get('graph_id')
    if graph_id:
        api_get(f"/api/graph/delete/{graph_id}")
        print(color(f"  Grafik {graph_id[:20]} dihapus", "dim"))

    api_get(f"/api/graph/project/{project_id}/reset")

    # Hapus direktori proyek jika ada
    proj_dir = UPLOADS_DIR / "projects" / project_id
    if proj_dir.exists():
        import shutil
        shutil.rmtree(proj_dir)

    print(color(f"✅ Proyek {project_id} dihapus", "green"))


def delete_simulation(sim_id):
    """Hapus simulasi + data + report."""
    # Cari report terkait
    report_data = api_get(f"/api/report/by-simulation/{sim_id}")
    if 'data' in report_data:
        report = report_data['data']
        if report and report.get('report_id'):
            api_get(f"/api/report/{report['report_id']}")  # DELETE
            print(color(f"  Report {report['report_id'][:20]} dihapus", "dim"))

    # Hapus direktori simulasi
    sim_dir = SIMULATIONS_DIR / sim_id
    if sim_dir.exists():
        import shutil
        shutil.rmtree(sim_dir)
        print(color(f"  Data simulasi dihapus", "dim"))

    # Hapus report directory
    report_dir = REPORTS_DIR / f"report_*"
    for d in REPORTS_DIR.glob("*"):
        if d.is_dir():
            meta = d / "meta.json"
            if meta.exists():
                try:
                    mdata = json.loads(meta.read_text())
                    if mdata.get('simulation_id') == sim_id:
                        import shutil
                        shutil.rmtree(d)
                        print(color(f"  Report dir {d.name} dihapus", "dim"))
                except:
                    pass

    print(color(f"✅ Simulasi {sim_id} dihapus", "green"))


def clean_all(confirm=False):
    """Hapus SEMUA data."""
    if not confirm:
        print(color("⚠️  PERINGATAN: Ini akan menghapus SEMUA data MiroFish!", "red"))
        print(color("  Gunakan: history-viewer.py clean --force", "yellow"))
        return

    # Hapus semua proyek
    projects = api_get("/api/graph/project/list").get('data', [])
    for p in projects:
        pid = p.get('project_id', '')
        if pid:
            delete_project(pid)

    # Hapus direktori
    for d in [SIMULATIONS_DIR, REPORTS_DIR, UPLOADS_DIR / "projects"]:
        if d.exists():
            import shutil
            for sub in d.iterdir():
                if sub.is_dir():
                    shutil.rmtree(sub)

    print(color(f"\n✅ SEMUA DATA DIHAPUS! Lingkungan bersih.", "green"))
    print(color(f"  Jalankan ulang: cd ~/MiroFish && npm run dev", "cyan"))


# =========================================================================
# MAIN
# =========================================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description='MiroFish — History Viewer')
    parser.add_argument('command', nargs='?', default='env',
                       choices=['env', 'projects', 'project', 'sims', 'sim', 'reports', 'report',
                                'hapus', 'delete', 'clean', 'reset'],
                       help='Perintah')
    parser.add_argument('id', nargs='?', help='Project/Simulation ID')
    parser.add_argument('--force', action='store_true', help='Force clean all')
    parser.add_argument('--actions', type=int, default=10, help='Jumlah aksi')
    parser.add_argument('--posts', type=int, default=5, help='Jumlah posting')

    args = parser.parse_args()

    if args.command == 'env':
        environment_report()
    elif args.command == 'projects':
        list_projects()
    elif args.command == 'project':
        show_project(args.id)
    elif args.command == 'sims':
        list_simulations()
    elif args.command == 'sim':
        show_simulation(args.id, args.actions, args.posts)
    elif args.command == 'reports':
        list_reports()
    elif args.command in ('hapus', 'delete'):
        if args.id:
            print(color(f"\n🗑️  HAPUS: {args.id}\n", "yellow"))
            # Deteksi tipe dari prefix
            if args.id.startswith('proj_'):
                delete_project(args.id)
            elif args.id.startswith('sim_'):
                delete_simulation(args.id)
            elif args.id.startswith('report_'):
                # Hapus report
                api_get(f"/api/report/{args.id}", method='DELETE')
                print(color(f"✅ Report {args.id} dihapus", "green"))
            else:
                print(color("ID tidak dikenal. Gunakan: proj_xxx, sim_xxx, atau report_xxx", "yellow"))
        else:
            print(color("Gunakan: history-viewer.py hapus <project_id/simulation_id/report_id>", "yellow"))
            print()
            print("Contoh:")
            print("  history-viewer.py hapus proj_d06dd21ca757")
            print("  history-viewer.py hapus sim_61a3447f8a93")
            print("  history-viewer.py hapus report_38b84a05fb30")
    elif args.command in ('clean', 'reset'):
        clean_all(args.force)
    elif args.command == 'report':
        if args.id:
            print(color(f"\nReport {args.id}:", "bold"))
            print(json.dumps(api_get(f"/api/report/{args.id}"), indent=2, ensure_ascii=False)[:3000])
        else:
            list_reports()


if __name__ == '__main__':
    main()
