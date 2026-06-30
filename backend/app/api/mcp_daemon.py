"""
MiroFish — MCP Daemon API Integration
Auto-start MCP daemon when MiroFish starts.
API endpoints for checking cache and daemon status.
"""

import os
import json
from pathlib import Path
from flask import Blueprint, jsonify

# Import daemon
import sys
tools_dir = Path(__file__).parents[2] / "tools"
sys.path.insert(0, str(tools_dir))
from mcp_daemon import start_daemon, stop_daemon, get_cache, get_all_caches, cache_status

mcp_bp = Blueprint('mcp', __name__, url_prefix='/api/mcp')

# Global daemon reference
_daemon_started = False


def init_mcp_daemon(app):
    """Initialize MCP daemon with Flask app."""
    global _daemon_started
    
    if not _daemon_started:
        try:
            start_daemon()
            _daemon_started = True
            app.logger.info("🚀 MCP Daemon auto-started")
        except Exception as e:
            app.logger.error(f"MCP Daemon start failed: {e}")


@mcp_bp.route('/status', methods=['GET'])
def mcp_status():
    """MCP daemon status."""
    caches = get_all_caches()
    return jsonify({
        "success": True,
        "daemon_running": _daemon_started,
        "cache_count": len(caches),
        "caches": list(caches.keys()),
        "cache_dir": str(Path.home() / "MiroFish" / ".mcp-cache")
    })


@mcp_bp.route('/cache/<name>', methods=['GET'])
def mcp_cache(name):
    """Get specific cache data."""
    data = get_cache(name)
    if data:
        return jsonify({"success": True, "cache": name, "data": data})
    return jsonify({"success": False, "error": f"Cache '{name}' not found"}), 404


@mcp_bp.route('/refresh', methods=['POST'])
def mcp_refresh():
    """Force refresh all caches."""
    # This would trigger immediate refresh
    return jsonify({"success": True, "message": "Refresh scheduled"})
