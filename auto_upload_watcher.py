#!/usr/bin/env python3
"""
Salesforce Auto-Upload Watcher
Watches Downloads folder and automatically uploads any new CSV files
"""

import os
import time
import glob
import requests
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
DASHBOARD_API_URL = "http://localhost:5001/api/upload"


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def upload_to_dashboard(csv_file):
    """Upload CSV to dashboard"""
    try:
        log(f"📤 Uploading: {os.path.basename(csv_file)}")

        with open(csv_file, 'rb') as f:
            files = {'file': (os.path.basename(csv_file), f, 'text/csv')}
            response = requests.post(DASHBOARD_API_URL, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            log(f"✅ UPLOAD SUCCESSFUL!")
            log(f"   New: {result.get('new', 0)} | Updated: {result.get('updated', 0)}")

            # Archive the file
            archive_dir = os.path.join(DOWNLOAD_DIR, "salesforce_archive")
            os.makedirs(archive_dir, exist_ok=True)
            try:
                archive_path = os.path.join(archive_dir, os.path.basename(csv_file))
                os.rename(csv_file, archive_path)
                log(f"📁 Archived to: salesforce_archive/")
            except Exception as e:
                log(f"⚠️  Could not archive: {e}")

            return True
        else:
            log(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        log(f"❌ Upload error: {e}")
        return False


class CSVHandler(FileSystemEventHandler):
    """Handles new CSV file events"""

    def __init__(self):
        self.processing = set()

    def on_created(self, event):
        """Called when a new file is created"""
        if event.is_directory:
            return

        filepath = event.src_path

        # Only process report*.csv files
        if not filepath.endswith('.csv'):
            return

        if 'report' not in os.path.basename(filepath).lower():
            return

        # Avoid processing same file twice
        if filepath in self.processing:
            return

        self.processing.add(filepath)

        # Wait a moment to ensure file is fully written
        time.sleep(2)

        # Check file still exists and has size
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            log("")
            log("="*80)
            log(f"🆕 NEW CSV DETECTED!")
            log(f"📄 {os.path.basename(filepath)}")
            log(f"📏 {os.path.getsize(filepath) / 1024:.1f} KB")
            log("="*80)

            upload_to_dashboard(filepath)

        self.processing.discard(filepath)


def main():
    """Main watcher function"""
    log("="*80)
    log("🤖 SALESFORCE AUTO-UPLOAD WATCHER")
    log("="*80)
    log(f"📁 Watching: {DOWNLOAD_DIR}")
    log(f"🎯 Looking for: report*.csv files")
    log(f"📤 Auto-uploads to: {DASHBOARD_API_URL}")
    log("="*80)
    log("")
    log("✨ READY! Export from Salesforce and files will upload automatically.")
    log("")
    log("💡 How to use:")
    log("   1. Go to Salesforce and export your report as CSV")
    log("   2. File downloads to ~/Downloads")
    log("   3. This script detects it INSTANTLY")
    log("   4. Auto-uploads to dashboard")
    log("   5. File gets archived")
    log("")
    log("Press Ctrl+C to stop watching")
    log("="*80)
    log("")

    # Set up file system observer
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOAD_DIR, recursive=False)
    observer.start()

    log("👀 Watching for new CSV files...")
    log("")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("")
        log("🛑 Stopping watcher...")
        observer.stop()

    observer.join()
    log("✅ Watcher stopped")


if __name__ == "__main__":
    # Check if watchdog is installed
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("❌ Error: 'watchdog' package not installed")
        print("Installing now...")
        os.system("pip install watchdog")
        print("\nPlease run the script again!")
        exit(1)

    main()
