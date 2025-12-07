# auth.py
import pandas as pd
import bcrypt
from datetime import datetime
from utils import get_ip, get_device_info, get_browser_info
from data_handler import load_users, save_users
import cv2
import os
from data_handler import load_users, save_users
from video import capture_video # Make sure this is imported

def hash_password(password: str) -> str:
    """Hash the password and return a UTF-8 string to store in CSV."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Check password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False



# auth.py
import pandas as pd
from datetime import datetime
from utils import get_ip, get_device_info, get_browser_info
from data_handler import load_users, save_users
from video import capture_video
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def register_user(username, password, mfa_enabled):
    users = load_users()

    if username in users['Username'].values:
        print("Username already exists!")
        return None

    # Capture video first
    video_path = capture_video(username)
    if video_path is None:
        print("Face not detected. Registration failed.")
        return None

    hashed_password = hash_password(password)

    # Compute next UID at the very start
    if users.empty:
        new_uid = 1001
    else:
        users['UID_numeric'] = pd.to_numeric(users['UID'], errors='coerce')
        new_uid = int(users['UID_numeric'].max()) + 1

    # Collect system info
    ip = get_ip()
    device = get_device_info()
    browser = get_browser_info()
    timestamp = datetime.now().isoformat()

    # **Create new row with UID first**
    new_row = {
        "UID": new_uid,
        "Username": username,
        "Password": hashed_password,
        "MFA Enabled": int(mfa_enabled),
        "IP": ip,
        "Device": device,
        "Browser": browser,
        "Video Path": video_path,
        "Registration Timestamp": timestamp
    }

    # Append and save immediately
    users = pd.concat([users, pd.DataFrame([new_row])], ignore_index=True)
    save_users(users)

    print(f"User {username} registered successfully with UID {new_uid}!")
    return new_uid
