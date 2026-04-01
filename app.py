我来为您创建一个完整的修复版本代码。我发现了几个关键问题并进行了修复：

```python
import streamlit as st
import os
import hashlib
import sqlite3
import tempfile
import subprocess
import secrets
import uuid
import json
import time
import random
import re
import base64
import numpy as np
import pandas as pd
import plotly.express as px
import cv2
import requests
import jieba.analyse
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, vfx
from moviepy.video.fx import crossfadein
from gtts import gTTS

st.set_page_config(page_title="小智 - 智能视频助手", page_icon="🤖", layout="wide")

# ========== CSS样式 ==========
st.markdown("""
<style>
.grid-card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 10px;
    margin: 5px;
    background: white;
    transition: transform 0.2s;
}
.grid-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.points-badge {
    background: linear-gradient(45deg, #FFD700, #FFA500);
    color: white;
    padding: 10px;
    border-radius: 20px;
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
}
.message-item {
    background: #f5f5f5;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
    border-left: 4px solid #4CAF50;
}
.message-time {
    font-size: 12px;
    color: #888;
    text-align: right;
}
.card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.main-header {
    text-align: center;
    padding: 40px 0;
}
.post-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ========== 全局配置 ==========
POSTER_DIR = "poster_images"
WALLPAPER_DIR = "wallpapers"
CACHE_DIR = "cached_videos"
UPLOAD_DIR = "uploads"
os.makedirs(POSTER_DIR, exist_ok=True)
os.makedirs(WALLPAPER_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== 数据库初始化（所有表） ==========
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        salt TEXT,
        points INTEGER DEFAULT 100,
        admin_level INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_poster_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator TEXT,
        title TEXT,
        description TEXT,
        price_points INTEGER DEFAULT 100,
        rarity TEXT DEFAULT '普通',
        image_path TEXT,
        likes INTEGER DEFAULT 0,
        buys INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS poster_collections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        poster_id INTEGER,
        bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS poster_earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator TEXT,
        poster_id INTEGER,
        buyer TEXT,
        amount_points INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_wallpaper_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS wallpapers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator TEXT,
        title TEXT,
        description TEXT,
        image_path TEXT,
        price_points INTEGER DEFAULT 100,
        category TEXT DEFAULT '其他',
        signature_info TEXT,
        likes INTEGER DEFAULT 0,
        buys INTEGER DEFAULT 0,
        status TEXT DEFAULT 'on_sale',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS wallpaper_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        wallpaper_id INTEGER,
        price_points INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS wallpaper_earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator TEXT,
        wallpaper_id INTEGER,
        buyer TEXT,
        amount_points INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_welfare_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS welfare_donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        project_id INTEGER,
        points INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS welfare_points (
        user TEXT PRIMARY KEY,
        total_donated INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def init_jackpot_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jackpot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT,
        total_points INTEGER DEFAULT 0,
        distributed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS jackpot_winners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT,
        winner TEXT,
        category TEXT,
        rank INTEGER,
        points INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_community_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        type TEXT,
        title TEXT,
        content TEXT,
        media_path TEXT,
        media_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        tips_total INTEGER DEFAULT 0,
        views INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        post_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user, post_id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        post_id INTEGER,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user TEXT,
        to_user TEXT,
        post_id INTEGER,
        amount INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_material_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS video_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        tags TEXT,
        url TEXT,
        duration INTEGER,
        thumbnail TEXT,
        source TEXT,
        uploader TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS music_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        tags TEXT,
        url TEXT,
        artist TEXT,
        duration INTEGER,
        source TEXT,
        uploader TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_user_actions_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action_type TEXT,
        target_type TEXT,
        target_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_promotions_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS promotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        points_cost INTEGER,
        status TEXT DEFAULT 'active'
    )''')
    conn.commit()
    conn.close()

def init_tasks_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        task_id TEXT,
        completed_at TIMESTAMP,
        date DATE
    )''')
    conn.commit()
    conn.close()

def init_economy_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        ad_type TEXT,
        points_gained INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS recharge_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        amount_cents INTEGER,
        points_gained INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS withdraw_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        points INTEGER,
        amount_cents INTEGER,
        fee_cents INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS referral_earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer TEXT,
        buyer TEXT,
        transaction_id INTEGER,
        amount_points INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        type TEXT,
        points_cost INTEGER,
        start_date DATE,
        end_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tool_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        tool_id INTEGER,
        points_cost INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS license_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        asset_id INTEGER,
        points_cost INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS lottery_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        points_cost INTEGER,
        prize TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_cabinet_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS digital_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator TEXT,
        title TEXT,
        description TEXT,
        type TEXT,
        price_points INTEGER,
        file_path TEXT,
        preview_path TEXT,
        tags TEXT,
        likes INTEGER DEFAULT 0,
        buys INTEGER DEFAULT 0,
        status TEXT DEFAULT 'on_sale',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS digital_asset_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        asset_id INTEGER,
        points_cost INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS creator_earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator TEXT,
        asset_id INTEGER,
        buyer TEXT,
        amount_points INTEGER,
        platform_fee INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def init_social_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        start_date DATE,
        end_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        topic_id INTEGER,
        post_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        icon TEXT,
        description TEXT,
        condition TEXT,
        points_reward INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        badge_id INTEGER,
        obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

# ========== 用户认证与积分 ==========
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return pwd_hash, salt

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash, salt, points, admin_level FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, "用户不存在", None, None
    stored_hash, salt, points, admin_level = row
    input_hash, _ = hash_password(password, salt)
    if input_hash == stored_hash:
        return True, "登录成功", points, admin_level
    return False, "密码错误", None, None

def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False, "用户名已存在"
    pwd_hash, salt = hash_password(password)
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    admin_level = 5 if count == 0 else 0
    c.execute("INSERT INTO users (username, password_hash, salt, points, admin_level) VALUES (?, ?, ?, 100, ?)",
              (username, pwd_hash, salt, admin_level))
    conn.commit()
    conn.close()
    return True, "注册成功"

def get_points(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def spend_points(username, points, reason):
    conn = sqlite3.connect('users.db')
    conn.execute("BEGIN")
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=? FOR UPDATE", (username,))
    row = c.fetchone()
    if not row or row[0] < points:
        conn.rollback()
        conn.close()
        return False
    c.execute("UPDATE users SET points = points - ? WHERE username=?", (points, username))
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, reason))
    conn.commit()
    conn.close()
    return True

def add_points(username, amount, reason):
    conn = sqlite3.connect('users.db')
    conn.execute("BEGIN")
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=? FOR UPDATE", (username,))
    row = c.fetchone()
    if not row:
        conn.rollback()
        conn.close()
        return False
    c.execute("UPDATE users SET points = points + ? WHERE username=?", (amount, username))
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, reason))
    conn.commit()
    conn.close()
    return True

def get_notifications(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT action, timestamp FROM user_logs 
        WHERE username = ? AND (action LIKE '%点赞%' OR action LIKE '%评论%' OR action LIKE '%购买%')
        ORDER BY timestamp DESC LIMIT 20
    """, (username,))
    interact = c.fetchall()
    system = []
    c.execute("SELECT total_donated FROM welfare_points WHERE user = ?", (username,))
    welfare = c.fetchone()
    if welfare and welfare[0] > 0:
        system.append(("🎖️ 感谢您的公益捐赠！获得爱心勋章", datetime.now().strftime("%Y-%m-%d %H
