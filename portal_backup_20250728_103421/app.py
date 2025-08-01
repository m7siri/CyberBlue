#!/usr/bin/env python3
"""
CyberBlueBox Portal - Python Flask Backend
Central access point for all security tools with changelog functionality
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('portal.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
PORT = int(os.environ.get('PORT', 5500))
CHANGELOG_FILE = 'changelog.json'

class ChangelogManager:
    """Manages changelog entries for all system activities"""
    
    def __init__(self, changelog_file):
        self.changelog_file = changelog_file
        self.load_changelog()
    
    def load_changelog(self):
        """Load existing changelog from file"""
        try:
            if os.path.exists(self.changelog_file):
                with open(self.changelog_file, 'r') as f:
                    self.changelog = json.load(f)
            else:
                self.changelog = {
                    "entries": [],
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "1.0.0",
                        "total_entries": 0
                    }
                }
                self.save_changelog()
        except Exception as e:
            logger.error(f"Error loading changelog: {e}")
            self.changelog = {"entries": [], "metadata": {"created": datetime.now().isoformat(), "version": "1.0.0", "total_entries": 0}}
    
    def save_changelog(self):
        """Save changelog to file"""
        try:
            with open(self.changelog_file, 'w') as f:
                json.dump(self.changelog, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving changelog: {e}")
    
    def add_entry(self, action, details, user="system", level="info"):
        """Add a new changelog entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "user": user,
            "level": level,
            "id": len(self.changelog["entries"]) + 1
        }
        
        self.changelog["entries"].append(entry)
        self.changelog["metadata"]["total_entries"] = len(self.changelog["entries"])
        self.save_changelog()
        
        logger.info(f"Changelog entry added: {action} - {details}")
        return entry
    
    def get_entries(self, limit=None, level=None):
        """Get changelog entries with optional filtering"""
        entries = self.changelog["entries"]
        
        if level:
            entries = [e for e in entries if e["level"] == level]
        
        if limit:
            entries = entries[-limit:]
        
        return entries
    
    def get_stats(self):
        """Get changelog statistics"""
        entries = self.changelog["entries"]
        stats = {
            "total_entries": len(entries),
            "by_level": {},
            "by_action": {},
            "recent_activity": len([e for e in entries if self._is_recent(e["timestamp"])])
        }
        
        for entry in entries:
            # Count by level
            level = entry["level"]
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Count by action
            action = entry["action"]
            stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
        
        return stats
    
    def _is_recent(self, timestamp, hours=24):
        """Check if timestamp is within recent hours"""
        try:
            entry_time = datetime.fromisoformat(timestamp)
            return (datetime.now() - entry_time).total_seconds() < hours * 3600
        except:
            return False

# Initialize changelog manager
changelog_manager = ChangelogManager(CHANGELOG_FILE)

# Log initial startup
changelog_manager.add_entry(
    "system_startup",
    "CyberBlueBox Portal started successfully",
    level="info"
)

@app.route('/')
def index():
    """Serve the main portal page"""
    changelog_manager.add_entry("page_access", "Portal main page accessed", user="web_user")
    return render_template('index.html')

@app.route('/api/containers')
def get_containers():
    """Get container count API endpoint"""
    try:
        # Simple container count for now
        count = 0
        changelog_manager.add_entry("api_call", f"Container count requested: {count} containers")
        return jsonify({"count": count})
    except Exception as e:
        logger.error(f"Error in container count API: {e}")
        return jsonify({"count": "Unknown", "error": str(e)}), 500

@app.route('/api/changelog')
def get_changelog():
    """Get changelog entries API endpoint"""
    try:
        limit = request.args.get('limit', type=int)
        level = request.args.get('level')
        entries = changelog_manager.get_entries(limit=limit, level=level)
        return jsonify({"entries": entries})
    except Exception as e:
        logger.error(f"Error in changelog API: {e}")
        return jsonify({"entries": [], "error": str(e)}), 500

@app.route('/api/changelog/stats')
def get_changelog_stats():
    """Get changelog statistics API endpoint"""
    try:
        stats = changelog_manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in changelog stats API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/changelog/add', methods=['POST'])
def add_changelog_entry():
    """Add a new changelog entry API endpoint"""
    try:
        data = request.get_json()
        action = data.get('action', 'unknown')
        details = data.get('details', '')
        user = data.get('user', 'api_user')
        level = data.get('level', 'info')
        
        entry = changelog_manager.add_entry(action, details, user, level)
        return jsonify({"success": True, "entry": entry})
    except Exception as e:
        logger.error(f"Error adding changelog entry: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/server-info')
def get_server_info():
    """Get server information API endpoint"""
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        return jsonify({
            "hostname": hostname,
            "local_ip": local_ip,
            "port": PORT,
            "server_url": f"http://{local_ip}:{PORT}"
        })
    except Exception as e:
        logger.error(f"Error getting server info: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "changelog_entries": len(changelog_manager.changelog["entries"])
    })

@app.route('/api/tools')
def get_tools():
    """Get available tools configuration"""
    tools = [
        {
            "name": "Velociraptor",
            "description": "Digital Forensics and Incident Response platform for live endpoint forensics and threat hunting.",
            "port": 7000,
            "icon": "fas fa-search",
            "category": "dfir",
            "categoryName": "DFIR",
            "protocols": ["https"]
        },
        {
            "name": "Wazuh Dashboard",
            "description": "SIEM dashboard for log analysis, alerting, and security monitoring with Kibana-style interface.",
            "port": 7001,
            "icon": "fas fa-chart-line",
            "category": "siem",
            "categoryName": "SIEM",
            "protocols": ["https"]
        },
        {
            "name": "MISP",
            "description": "Threat Intelligence Platform for sharing, storing, and correlating indicators of compromise.",
            "port": 7003,
            "icon": "fas fa-brain",
            "category": "cti",
            "categoryName": "CTI",
            "protocols": ["https"]
        },
        {
            "name": "CyberChef",
            "description": "Cyber Swiss Army Knife for data analysis, encoding, decoding, and forensics operations.",
            "port": 7004,
            "icon": "fas fa-utensils",
            "category": "utility",
            "categoryName": "Utility",
            "protocols": ["http"]
        },
        {
            "name": "TheHive",
            "description": "Incident Response and Case Management platform for security operations teams.",
            "port": 7005,
            "icon": "fas fa-bug",
            "category": "soar",
            "categoryName": "SOAR",
            "protocols": ["http"]
        },
        {
            "name": "Cortex",
            "description": "Automated threat analysis platform with analyzers for TheHive integration.",
            "port": 7006,
            "icon": "fas fa-robot",
            "category": "soar",
            "categoryName": "SOAR",
            "protocols": ["http"]
        },
        {
            "name": "FleetDM",
            "description": "Osquery-based endpoint visibility and fleet management platform.",
            "port": 7007,
            "icon": "fas fa-desktop",
            "category": "management",
            "categoryName": "Management",
            "protocols": ["http"]
        },
        {
            "name": "Arkime",
            "description": "Full packet capture and session search engine for network analysis.",
            "port": 7008,
            "icon": "fas fa-network-wired",
            "category": "ids",
            "categoryName": "IDS",
            "protocols": ["http"]
        },
        {
            "name": "Caldera",
            "description": "Automated adversary emulation platform for security testing and red team operations.",
            "port": 7009,
            "icon": "fas fa-chess-king",
            "category": "soar",
            "categoryName": "SOAR",
            "protocols": ["http"]
        },
        {
            "name": "Evebox",
            "description": "Web-based viewer for Suricata EVE JSON logs and alert management.",
            "port": 7010,
            "icon": "fas fa-eye",
            "category": "ids",
            "categoryName": "IDS",
            "protocols": ["https"]
        },
        {
            "name": "Wireshark",
            "description": "Network protocol analyzer for deep packet inspection and network troubleshooting.",
            "port": 7011,
            "icon": "fas fa-filter",
            "category": "utility",
            "categoryName": "Utility",
            "protocols": ["http", "https"]
        },
        {
            "name": "MITRE Navigator",
            "description": "Interactive ATT&CK matrix for threat modeling and attack path visualization.",
            "port": 7013,
            "icon": "fas fa-sitemap",
            "category": "cti",
            "categoryName": "CTI",
            "protocols": ["http"]
        },
        {
            "name": "Portainer",
            "description": "Web-based container management interface for Docker and Kubernetes.",
            "port": 9443,
            "icon": "fas fa-ship",
            "category": "management",
            "categoryName": "Management",
            "protocols": ["https"]
        }
    ]
    return jsonify({"tools": tools})

if __name__ == '__main__':
    logger.info(f"🚀 Starting CyberBlueBox Portal on port {PORT}")
    logger.info(f"📱 Access the portal at: http://localhost:{PORT}")
    logger.info(f"🔧 API endpoints available at: http://localhost:{PORT}/api/")
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down CyberBlueBox Portal...")
        changelog_manager.add_entry("system_shutdown", "CyberBlueBox Portal shut down gracefully")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        changelog_manager.add_entry("system_error", f"Server startup error: {e}", level="error") 