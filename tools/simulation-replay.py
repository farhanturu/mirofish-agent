#!/usr/bin/env python3
"""
MiroFish — Simulation Replay
Tonton ulang simulasi step-by-step seperti nonton rekaman.
Lihat posting, komentar, aksi, interaksi, dan statistik per putaran.
"""

import sys
import os
import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta

BACKEND_URL = "http://localhost:5001"
UPLOADS_DIR = Path.home() / "MiroFish" / "backend" / "uploads"
SIMULATIONS_DIR = UPLOADS_DIR / "simulations"


def color(text, code=""):
    colors = {
        'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
        'cyan': '\033[96m', 'blue': '\033[94m', 'bold': '\033[1m',
        'dim': '\033[2m', 'reset': '\033[0m', 'purple': '\033[95m'
    }
    return f"{colors.get(code, '')}{text}{colors['reset']}"


def load_run_state(sim_id):
    """Load state dari file."""
    state_file = SIMULATIONS_DIR / sim_id / "state.json"
    run_state_file = SIMULATIONS_DIR / sim_id / "run_state.json"
    config_file = SIMULATIONS_DIR / sim_id / "simulation_config.json"
    twitter_db = SIMULATIONS_DIR / sim_id / "twitter_simulation.db"
    reddit_dir = SIMULATIONS_DIR / sim_id / "reddit"

    state = {}
    if state_file.exists():
        with open(state_file) as f:
            state['sim_state'] = json.load(f)
    if run_state_file.exists():
        with open(run_state_file) as f:
            state['run_state'] = json.load(f)
    if config_file.exists():
        with open(config_file) as f:
            state['config'] = json.load(f)

    state['twitter_db'] = str(twitter_db) if twitter_db.exists() else None
    state['reddit_dir'] = str(reddit_dir) if reddit_dir.exists() else None

    return state


def get_db_data(db_path, query, params=()):
    """Ambil data dari SQLite database."""
    if not db_path or not Path(db_path).exists():
        return []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, params)
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        return [{"error": str(e)}]


def get_round_actions(sim_id, db_path, round_num=None):
    """Ambil aksi untuk suatu putaran."""
    import urllib.request
    try:
        url = f"{BACKEND_URL}/api/simulation/{sim_id}/actions?limit=200"
        if round_num is not None:
            url += f"&round_num={round_num}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get('data', {}).get('actions', [])
    except:
        return []


def get_posts_for_round(db_path, round_num, round_interval=60):
    """Ambil post untuk estimasi waktu putaran."""
    if not db_path:
        return []
    return get_db_data(
        db_path,
        f"""
        SELECT p.*, u.user_name, u.name as real_name
        FROM post p
        JOIN user u ON p.user_id = u.user_id
        ORDER BY p.created_at
        LIMIT 50
        """
    )


def display_posts(db_path, platform, limit=20):
    """Tampilkan posting."""
    rows = get_db_data(
        db_path,
        f"""
        SELECT p.*, u.user_name, u.name as real_name
        FROM post p
        JOIN user u ON p.user_id = u.user_id
        ORDER BY p.created_at DESC
        LIMIT {limit}
        """
    )
    if not rows:
        print(f"    {color('(belum ada posting)', 'dim')}")
        return

    for p in rows:
        created = p.get('created_at', '')[:16] if p.get('created_at') else '-'
        name = p.get('user_name') or p.get('real_name') or f"User#{p['user_id']}"
        content = (p.get('content') or '')[:180]
        likes = p.get('num_likes', 0)
        shares = p.get('num_shares', 0)
        reposts = p.get('num_reposts', 0)

        print(f"    {color(name, 'bold')}: {content}")
        print(f"    {color(f'❤️ {likes}', 'red')} {color(f'🔄 {shares}', 'yellow')}  {color(created, 'dim')}")
        print()


def display_users(db_path):
    """Tampilkan user/agen."""
    rows = get_db_data(db_path, "SELECT * FROM user ORDER BY user_id LIMIT 35")
    if not rows:
        return

    print(f"    {color(f'{len(rows)} agen:', 'bold')}")
    for u in rows:
        uid = u.get('agent_id', u.get('user_id', '?'))
        name = u.get('user_name') or u.get('name') or f"Agent#{uid}"
        bio = (u.get('bio') or '')[:60]
        followers = u.get('num_followers', 0)
        following = u.get('num_followings', 0)
        print(f"    #{uid} {color(name, 'bold')} — {bio}")
        print(f"      Followers: {followers}  Following: {following}")


def display_network(db_path):
    """Tampilkan jaringan sosial."""
    follows = get_db_data(db_path, """
        SELECT f.*, u1.user_name as follower_name, u2.user_name as followee_name
        FROM follow f
        JOIN user u1 ON f.follower_id = u1.user_id
        JOIN user u2 ON f.followee_id = u2.user_id
        LIMIT 20
    """)
    if follows:
        print(f"    {color(f'{len(follows)} relasi follow:', 'bold')}")
        for f in follows[:10]:
            print(f"    {f['follower_name']} → {f['followee_name']}")


def display_traces(db_path):
    """Tampilkan jejak aktivitas."""
    traces = get_db_data(db_path, """
        SELECT * FROM trace ORDER BY created_at DESC LIMIT 20
    """)
    if traces:
        print(f"    {color(f'{len(traces)} jejak aktivitas:', 'bold')}")
        for t in traces[:10]:
            user_id = t.get('user_id', '?')
            action = t.get('action', '?')
            info = (t.get('info') or '')[:80]
            created = str(t.get('created_at', ''))[:16]
            print(f"    User#{user_id}: {color(action, 'yellow')} — {info}  {color(created, 'dim')}")


def display_comments(db_path, limit=15):
    """Tampilkan komentar."""
    rows = get_db_data(
        db_path,
        f"""
        SELECT c.*, u.user_name
        FROM comment c
        JOIN user u ON c.user_id = u.user_id
        ORDER BY c.created_at DESC
        LIMIT {limit}
        """
    )
    if not rows:
        return

    print(f"    {color(f'{len(rows)} komentar:', 'bold')}")
    for c in rows:
        name = c.get('user_name') or f"User#{c['user_id']}"
        content = (c.get('content') or '')[:120]
        print(f"    {name}: \"{content}\"")


def display_group_chats(db_path):
    """Tampilkan pesan grup."""
    msgs = get_db_data(db_path, """
        SELECT gm.*, g.name as group_name, u.user_name
        FROM group_messages gm
        JOIN chat_group g ON gm.group_id = g.group_id
        JOIN user u ON gm.sender_id = u.agent_id
        ORDER BY gm.sent_at DESC
        LIMIT 15
    """)
    if msgs:
        print(f"    {color(f'{len(msgs)} pesan grup:', 'bold')}")
        for m in msgs[:5]:
            name = m.get('user_name') or f"Agent#{m['sender_id']}"
            content = (m.get('content') or '')[:120]
            group = m.get('group_name', '?')
            print(f"    [{group}] {color(name, 'purple')}: \"{content}\"")


def display_likes_dislikes(db_path):
    """Tampilkan interaksi like/dislike."""
    likes = get_db_data(db_path, """
        SELECT l.*, u.user_name
        FROM "like" l
        JOIN user u ON l.user_id = u.user_id
        ORDER BY l.created_at DESC
        LIMIT 10
    """)
    if likes:
        print(f"    {color(f'{len(likes)} like:', 'bold')}")
        for l in likes[:5]:
            name = l.get('user_name') or f"User#{l['user_id']}"
            print(f"    {name} ❤️ post#{l['post_id']}")


# =========================================================================
# REPLAY — Putar Ulang Step by Step
# =========================================================================
def replay_simulation(sim_id, auto_play=False, delay=1):
    """Putar ulang simulasi step by step."""
    state = load_run_state(sim_id)
    config = state.get('config', {})
    run_state = state.get('run_state', {})
    db_path = state.get('twitter_db')

    if not db_path:
        print(color(f"Database simulasi tidak ditemukan.", "red"))
        return

    total_rounds = config.get('total_rounds', config.get('max_rounds', 30))
    max_rounds = min(total_rounds, 30)  # Batasi 30 putaran untuk replay

    print(color(f"\n{'='*70}", "cyan"))
    print(color(f"  🎬 REPLAY SIMULASI: {sim_id}", "bold"))
    print(color(f"{'='*70}", "cyan"))
    print(f"  Lingkungan: {config.get('simulation_hours', '?')} jam simulasi")
    print(f"  Putaran:    {total_rounds} (replay: {max_rounds})")
    print(f"  Agen:       {config.get('total_agents', '?')} agen")
    print(f"  Database:   {db_path}")
    print()

    putaran = 0

    for round_num in range(1, max_rounds + 1):
        putaran += 1
        sim_hour = round_num * (config.get('interval_minutes', 60) / 60)
        sim_time = f"Hari {int(sim_hour/24)+1}, Jam {int(sim_hour%24):02d}:00"

        print(color(f"\n{'─'*70}", "dim"))
        print(color(f"  ⏱️  PUTARAN {round_num}/{max_rounds}  ─  {sim_time}", "bold"))
        print(color(f"{'─'*70}", "dim"))

        # Post
        posts = get_db_data(
            db_path,
            f"""
            SELECT p.*, u.user_name, u.name as real_name
            FROM post p
            JOIN user u ON p.user_id = u.user_id
            ORDER BY p.created_at
            LIMIT 3
            """
        )

        if posts:
            for p in posts:
                name = p.get('user_name') or p.get('real_name') or f"User#{p['user_id']}"
                content = (p.get('content') or '')[:150]
                likes = p.get('num_likes', 0)
                print(f"    {color(name, 'bold')}: {content}")
                print(f"    {color(f'❤️ {likes}', 'red')}")
                print()

        # Aksi
        actions = get_round_actions(sim_id, db_path, round_num)
        if actions:
            for a in actions[:5]:
                agent_id = a.get('agent_id', '-')
                atype = a.get('action', a.get('action_type', '?'))
                content = (a.get('content', a.get('info', '')))[:100]
                print(f"    [{color(atype, 'yellow')}] Agent#{agent_id}: {content}")

        if not auto_play:
            try:
                cmd = input(color(f"\n  ⏎ Enter=lanjut, q=keluar, a=auto: ", "dim"))
                if cmd.lower() == 'q':
                    print(color("\n  Replay dihentikan.", "yellow"))
                    break
                if cmd.lower() == 'a':
                    auto_play = True
                    delay = float(input(color("  Delay (detik) [1]: ", "dim")) or "1")
            except (EOFError, KeyboardInterrupt):
                break
        else:
            time.sleep(delay)

    if putaran >= max_rounds:
        print(color(f"\n  ✅ Replay selesai! {max_rounds} putaran.", "green"))


# =========================================================================
# DUNIA — Lihat Full Lingkungan
# =========================================================================
def show_world(sim_id):
    """Tampilkan seluruh dunia simulasi."""
    state = load_run_state(sim_id)
    config = state.get('config', {})
    run_state = state.get('run_state', {})
    db_path = state.get('twitter_db')
    reddit_dir = state.get('reddit_dir')

    print(color(f"\n{'='*70}", "cyan"))
    print(color(f"  🌍 DUNIA SIMULASI: {sim_id}", "bold"))
    print(color(f"{'='*70}", "cyan"))
    print()

    # Info dunia
    print(color(f"  ── INFO DUNIA ──", "green"))
    print(f"    Durasi:    {config.get('simulation_hours', '?')} jam")
    print(f"    Interval:  {config.get('interval_minutes', '?')} menit/putaran")
    print(f"    Putaran:   {config.get('max_rounds', '?')}")
    print(f"    Platform:  {'Twitter' if config.get('enable_twitter') else ''} {'Reddit' if config.get('enable_reddit') else ''}")
    print()

    # Waktu
    print(color(f"  ── WAKTU ──", "green"))
    jam_kunci = config.get('peak_hours', [])
    if jam_kunci:
        print(f"    Jam sibuk:   {jam_kunci}")
    print(f"    Jam aktif:   {config.get('active_hours', '?')}")
    print(f"    Jam pagi:    {config.get('morning_hours', '?')}")
    print(f"    Jam malam:   {config.get('offpeak_hours', '?')}")
    print()

    # Agen
    if db_path:
        print(color(f"  ── PENDUDUK DUNIA ──", "green"))
        users = get_db_data(db_path, "SELECT * FROM user ORDER BY agent_id")
        print(f"    Total: {len(users)} agen")
        print()

        # Profil
        for u in users[:10]:
            uid = u.get('agent_id', u.get('user_id', '?'))
            name = u.get('user_name') or u.get('name') or f"Agent#{uid}"
            bio = (u.get('bio') or '')[:80]
            followers = u.get('num_followers', 0)
            following = u.get('num_followings', 0)
            print(f"    #{uid} {color(name, 'bold')}")
            print(f"      Bio: {bio}")
            print(f"      Followers: {color(followers, 'cyan')}  Following: {color(following, 'cyan')}")

        if len(users) > 10:
            print(f"    ... dan {len(users)-10} lainnya")
        print()

        # Aktivitas
        print(color(f"  ── AKTIVITAS ──", "green"))
        post_count = get_db_data(db_path, "SELECT COUNT(*) as c FROM post")[0]['c'] if get_db_data(db_path, "SELECT COUNT(*) as c FROM post") else 0
        comment_count = get_db_data(db_path, "SELECT COUNT(*) as c FROM comment")[0]['c']
        like_count = get_db_data(db_path, "SELECT COUNT(*) as c FROM \"like\"")[0]['c']
        follow_count = get_db_data(db_path, "SELECT COUNT(*) as c FROM follow")[0]['c']
        trace_count = get_db_data(db_path, "SELECT COUNT(*) as cnt FROM trace")[0]['cnt']

        print(f"    📝 Post:    {color(post_count, 'bold')}")
        print(f"    💬 Komentar: {color(comment_count, 'bold')}")
        print(f"    ❤️ Like:     {color(like_count, 'bold')}")
        print(f"    👥 Follow:   {color(follow_count, 'bold')}")
        print(f"    📋 Jejak:    {color(trace_count, 'bold')}")
        print()

        # Timeline aktivitas
        print(color(f"  ── TIMELINE AKTIVITAS ──", "green"))
        traces = get_db_data(db_path, """
            SELECT * FROM trace ORDER BY created_at DESC LIMIT 20
        """)
        for t in traces[:10]:
            action = t.get('action', '?')
            info = (t.get('info') or '')[:100]
            created = str(t.get('created_at', ''))[11:19]
            print(f"    [{created}] {color(action, 'yellow')}: {info}")
        print()

        # Jaringan sosial
        print(color(f"  ── JARINGAN SOSIAL ──", "green"))
        display_network(db_path)
        display_group_chats(db_path)


# =========================================================================
# REST API untuk History
# =========================================================================
def show_api_history():
    """Tampilkan history dari API."""
    import urllib.request
    try:
        url = f"{BACKEND_URL}/api/simulation/history?limit=50"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data
    except Exception as e:
        return {"error": str(e)}


# =========================================================================
# MAIN
# =========================================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description='MiroFish — Simulation Replay')
    parser.add_argument('command', nargs='?', default='history',
                       choices=['history', 'world', 'replay', 'db', 'users', 'posts', 'network', 'traces'],
                       help='Perintah')
    parser.add_argument('sim_id', nargs='?', help='Simulation ID')
    parser.add_argument('--auto', action='store_true', help='Auto-play replay')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay replay (detik)')
    parser.add_argument('--limit', type=int, default=20, help='Limit data')

    args = parser.parse_args()

    if args.command == 'history' and not args.sim_id:
        # Tampilkan semua history
        data = show_api_history()
        items = data.get('data', [])
        print(color(f"\n{'='*70}", "cyan"))
        print(color(f"  📜 HISTORY SIMULASI ({data.get('count', len(items))})", "bold"))
        print(color(f"{'='*70}", "cyan"))
        print()
        for s in items:
            sid = s.get('simulation_id', '?')[:20]
            name = s.get('project_name', 'Tanpa Nama')
            status = s.get('status', '?')
            agents = s.get('expected_entities_count', '-')
            created = str(s.get('created_at', ''))[:16]
            report = s.get('report_id', '')
            report_str = color('✓', 'green') if report else color('✗', 'dim')
            print(f"  {color(sid, 'cyan')}")
            print(f"    {color(name, 'bold')}  |  Status: {status}  |  Agen: {agents}")
            print(f"    Dibuat: {created}  |  Report: {report_str}")
            print()
        print(f"  Gunakan: {color('python3 simulation-replay.py world <sim_id>', 'yellow')} untuk lihat dunia")
        print(f"  Gunakan: {color('python3 simulation-replay.py replay <sim_id>', 'yellow')} untuk replay")
        print()

    elif args.command == 'world' and args.sim_id:
        show_world(args.sim_id)

    elif args.command == 'replay' and args.sim_id:
        replay_simulation(args.sim_id, args.auto, args.delay)

    elif args.command == 'history' and args.sim_id:
        # Tampilkan detail dari API
        import urllib.request
        try:
            url = f"{BACKEND_URL}/api/simulation/{args.sim_id}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                if 'error' not in data:
                    print(json.dumps(data.get('data', {}), indent=2, ensure_ascii=False)[:3000])
                else:
                    print(color(f"Error: {data['error']}", "red"))
        except Exception as e:
            print(color(f"Error: {e}", "red"))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
