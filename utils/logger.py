import os
from datetime import datetime

# 📁 مجلد السجلات (logs)
LOG_DIR = "logs"
ACTION_LOG = os.path.join(LOG_DIR, "admin_actions.log")
ERROR_LOG = os.path.join(LOG_DIR, "errors.log")

def ensure_log_dir():
    """🛠️ التأكد من وجود مجلد logs"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def log_admin_action(action: str):
    """📝 تسجيل فعل الأدمن مع وقت التنفيذ"""
    ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Admin action: {action}\n"

    with open(ACTION_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

def log_error(error: str):
    """❌ تسجيل الأخطاء التي تظهر في الكود"""
    ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Error: {error}\n"

    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)