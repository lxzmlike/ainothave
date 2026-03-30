"""
小智 - 智能视频助手 v8.9
新增：AI 助手自然语言理解 + 智能推荐 + 真实视频合成
"""

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
import cv2
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip, concatenate_videoclips

st.set_page_config(page_title="小智 - 智能视频助手", page_icon="🤖", layout="wide")

# ========== PWA支持 ==========
st.markdown("""
<link rel="manifest" href="manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="小智">
<link rel="apple-touch-icon" href="https://img.icons8.com/color/96/000000/brain.png">
""", unsafe_allow_html=True)

# ========== 美化CSS ==========
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px 20px;
    border-radius: 30px;
    text-align: center;
    margin-bottom: 30px;
}
.main-header h1 {
    color: white;
    font-size: 2.5rem;
}
.main-header p {
    color: rgba(255,255,255,0.9);
}
.dashboard-card {
    background: white;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.stat-row {
    display: flex;
    justify-content: space-around;
    text-align: center;
    margin-bottom: 20px;
}
.stat-item {
    flex: 1;
}
.stat-number {
    font-size: 28px;
    font-weight: bold;
    color: #667eea;
}
.stat-label {
    font-size: 12px;
    color: #666;
}
.hot-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}
.hot-item {
    background: #f5f5f5;
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    font-size: 12px;
    cursor: pointer;
}
.hot-item:hover {
    background: #e0e0e0;
}
.upload-card {
    background: white;
    border-radius: 24px;
    padding: 30px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}
.section-title {
    font-size: 24px;
    font-weight: bold;
    color: white;
    margin-bottom: 20px;
    text-align: center;
}
.feature-card {
    background: white;
    border-radius: 20px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    margin-bottom: 15px;
}
.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.feature-icon {
    font-size: 48px;
    margin-bottom: 10px;
}
.feature-name {
    font-size: 18px;
    font-weight: bold;
}
.feature-desc {
    font-size: 12px;
    color: #666;
}
.stButton button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 10px 20px;
    font-weight: bold;
    width: 100%;
}
.points-badge {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    display: inline-block;
}
.grid-card {
    background: white;
    border-radius: 20px;
    padding: 15px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.grid-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    display: flex;
    justify-content: space-around;
    padding: 8px 0;
    border-top: 1px solid #ddd;
    z-index: 1000;
}
.nav-item {
    text-align: center;
    flex: 1;
    cursor: pointer;
    color: #666;
    transition: 0.2s;
}
.nav-item.active {
    color: #667eea;
    font-weight: bold;
}
.nav-icon {
    font-size: 24px;
}
.nav-label {
    font-size: 12px;
}
.voice-card {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    border-radius: 20px;
    padding: 15px;
    margin-bottom: 20px;
    text-align: center;
    cursor: pointer;
    transition: 0.2s;
}
.voice-card:hover {
    transform: scale(1.02);
}
.example-card {
    background: rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 10px;
    margin: 10px 0;
    text-align: center;
    font-size: 12px;
    color: #666;
}
.task-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    padding: 10px;
    border-radius: 15px;
    margin-bottom: 10px;
}
.task-name {
    font-weight: bold;
}
.task-status {
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 20px;
}
.task-status.done {
    background: #4caf50;
    color: white;
}
.task-status.pending {
    background: #ff9800;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ========== 语言 ==========
LANG = {
    "zh": {
        "title": "小智 - 智能视频助手",
        "subtitle": "你的AI视频创作伙伴",
        "login": "登录",
        "register": "注册",
        "logout": "退出",
        "points": "积分",
        "upload_first": "请先上传视频"
    },
    "en": {
        "title": "XiaoZhi - AI Video Assistant",
        "subtitle": "Your AI Video Creation Partner",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "points": "Points",
        "upload_first": "Please upload a video first"
    }
}

def t(key):
    lang = st.session_state.get('language', 'zh')
    return LANG[lang].get(key, key)

# ========== 辅助函数 ==========
def save_uploaded_file(uploaded):
    if uploaded is None:
        return None
    suffix = os.path.splitext(uploaded.name)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getbuffer())
    return tmp.name

def get_video_info(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return {"duration": total_frames/fps if fps > 0 else 0}

def cut_video(input_path, start, end, output_path):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-to", str(end), "-c", "copy", output_path])

def speed_video(input_path, speed, output_path):
    subprocess.run(["ffmpeg", "-i", input_path, "-filter:v", f"setpts={1/speed}*PTS", "-c:a", "aac", output_path])

def video_to_gif(input_path, output_path, start=0, duration=5):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-t", str(duration), "-vf", "fps=10,scale=320:-1", output_path])

# ========== 数据库 ==========
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
        return False, "用户不存在"
    stored_hash, salt, points, admin_level = row
    input_hash, _ = hash_password(password, salt)
    if input_hash == stored_hash:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.points = points
        st.session_state.admin_level = admin_level
        st.session_state.remember_me = True
        return True, "登录成功"
    return False, "密码错误"

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

# ========== 消息中心 ==========
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
        system.append(("🎖️ 感谢您的公益捐赠！获得爱心勋章", datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.close()
    return interact, system

def render_messages():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📬 消息中心")
    interact, system = get_notifications(st.session_state.username)
    if not interact and not system:
        st.info("暂无新消息")
    else:
        if interact:
            st.markdown("#### 💬 互动消息")
            for action, ts in interact:
                st.markdown(f"""
                <div class="message-item">
                    📢 {action}<br>
                    <div class="message-time">{ts}</div>
                </div>
                """, unsafe_allow_html=True)
        if system:
            st.markdown("#### 📢 系统通知")
            for msg, ts in system:
                st.markdown(f"""
                <div class="message-item">
                    🔔 {msg}<br>
                    <div class="message-time">{ts}</div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 版图系统 ==========
POSTER_DIR = "poster_images"
os.makedirs(POSTER_DIR, exist_ok=True)

def save_poster_image(frame, poster_id):
    height, width = frame.shape[:2]
    max_size = 300
    if width > max_size:
        ratio = max_size / width
        new_width = max_size
        new_height = int(height * ratio)
        frame = cv2.resize(frame, (new_width, new_height))
    filepath = os.path.join(POSTER_DIR, f"{poster_id}.jpg")
    cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
    return filepath

def extract_frame_from_video(video_path, poster_id):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_frame = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
    ret, frame = cap.read()
    cap.release()
    if ret:
        return save_poster_image(frame, poster_id)
    return None

def render_poster_generator():
    st.markdown("### 🎨 生成版图")
    if not st.session_state.get('video_path'):
        st.info("请先上传视频")
        return
    video_path = st.session_state.video_path
    st.video(video_path)
    title = st.text_input("版图标题")
    price = st.number_input("价格（积分）", min_value=10, value=100)
    rarity = st.selectbox("稀有度", ["普通", "稀有", "史诗", "传说"])
    if st.button("✨ 生成版图"):
        if title:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO posters (creator, title, price_points, rarity) VALUES (?, ?, ?, ?)",
                      (st.session_state.username, title, price, rarity))
            poster_id = c.lastrowid
            conn.commit()
            image_path = extract_frame_from_video(video_path, poster_id)
            if image_path:
                c.execute("UPDATE posters SET image_path = ? WHERE id = ?", (image_path, poster_id))
                conn.commit()
                st.success(f"✅ 版图「{title}」生成成功！")
                st.balloons()
            conn.close()

def render_poster_mall():
    st.markdown("### 🛒 版图商城")
    if 'poster_page' not in st.session_state:
        st.session_state.poster_page = 1
    page_size = 12
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM posters")
    total = c.fetchone()[0]
    total_pages = (total + page_size - 1) // page_size
    offset = (st.session_state.poster_page - 1) * page_size
    c.execute("SELECT id, creator, title, price_points, rarity, likes, buys, image_path FROM posters ORDER BY created_at DESC LIMIT ? OFFSET ?", (page_size, offset))
    posters = c.fetchall()
    conn.close()
    if not posters:
        st.info("暂无版图")
        return
    cols = st.columns(4)
    for i, poster in enumerate(posters):
        poster_id, creator, title, price, rarity, likes, buys, image_path = poster
        with cols[i % 4]:
            st.markdown('<div class="grid-card">', unsafe_allow_html=True)
            if image_path and os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
            st.markdown(f"**{title[:20]}**")
            st.caption(f"👤 {creator} | 🏷️ {rarity}")
            st.caption(f"💰 {price}积分 | ❤️ {likes} | 🛒 {buys}")
            if st.button(f"购买", key=f"buy_poster_{poster_id}"):
                if spend_points(st.session_state.username, price, f"购买版图{title}"):
                    conn2 = sqlite3.connect('users.db')
                    c2 = conn2.cursor()
                    c2.execute("INSERT INTO poster_collections (user, poster_id) VALUES (?, ?)", (st.session_state.username, poster_id))
                    c2.execute("UPDATE posters SET buys = buys + 1 WHERE id = ?", (poster_id,))
                    c2.execute("INSERT INTO poster_earnings (creator, poster_id, buyer, amount_points) VALUES (?, ?, ?, ?)",
                               (creator, poster_id, st.session_state.username, price))
                    conn2.commit()
                    conn2.close()
                    creator_points = int(price * 0.8)
                    add_points(creator, creator_points, f"版图{title}被购买")
                    st.success(f"购买成功！{creator}获得{creator_points}积分")
                    st.rerun()
                else:
                    st.error("积分不足")
            st.markdown('</div>', unsafe_allow_html=True)
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            col_prev, col_page, col_next = st.columns(3)
            if st.session_state.poster_page > 1:
                if col_prev.button("◀"):
                    st.session_state.poster_page -= 1
                    st.rerun()
            col_page.markdown(f"<div style='text-align:center'>{st.session_state.poster_page}/{total_pages}</div>", unsafe_allow_html=True)
            if st.session_state.poster_page < total_pages:
                if col_next.button("▶"):
                    st.session_state.poster_page += 1
                    st.rerun()

def render_my_posters():
    st.markdown("### 🖼️ 我的版图")
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT title, price_points, rarity, likes, buys, image_path FROM posters WHERE creator = ?", (st.session_state.username,))
    posters = c.fetchall()
    conn.close()
    if not posters:
        st.info("还没有版图")
        return
    cols = st.columns(3)
    for i, poster in enumerate(posters):
        title, price, rarity, likes, buys, image_path = poster
        with cols[i % 3]:
            if image_path and os.path.exists(image_path):
                st.image(image_path, width=150)
            st.markdown(f"**{title}** | 💰 {price}积分 | 🏷️ {rarity}")
            st.caption(f"❤️ {likes} | 🛒 {buys}")

def render_my_collections():
    st.markdown("### 💎 我的收藏")
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT p.title, p.creator, p.price_points, p.rarity, p.image_path FROM poster_collections c JOIN posters p ON c.poster_id = p.id WHERE c.user = ?", (st.session_state.username,))
    collections = c.fetchall()
    conn.close()
    if not collections:
        st.info("还没有收藏")
        return
    cols = st.columns(3)
    for i, col in enumerate(collections):
        title, creator, price, rarity, image_path = col
        with cols[i % 3]:
            if image_path and os.path.exists(image_path):
                st.image(image_path, width=150)
            st.markdown(f"**{title}** | 创作者：{creator} | 💰 {price}积分 | 🏷️ {rarity}")

def render_poster_stats():
    st.markdown("### 📊 版图统计")
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM posters WHERE creator = ?", (st.session_state.username,))
    total = c.fetchone()[0]
    c.execute("SELECT SUM(buys) FROM posters WHERE creator = ?", (st.session_state.username,))
    sales = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount_points) FROM poster_earnings WHERE creator = ?", (st.session_state.username,))
    earnings = c.fetchone()[0] or 0
    conn.close()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("我的版图", total)
    with col2:
        st.metric("总销量", sales)
    with col3:
        st.metric("总收益", f"{earnings} 积分")

# ========== 壁纸系统 ==========
WALLPAPER_DIR = "wallpapers"
os.makedirs(WALLPAPER_DIR, exist_ok=True)

def save_wallpaper_image(uploaded_file, signature_info):
    ext = uploaded_file.name.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.jpg"
    final_path = os.path.join(WALLPAPER_DIR, filename)
    with open(final_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return final_path

def render_wallpaper_generator():
    st.markdown("### 🖼️ 生成壁纸")
    uploaded_file = st.file_uploader("选择图片", type=["jpg", "jpeg", "png"], key="wallpaper_upload")
    if uploaded_file:
        st.image(uploaded_file, caption="预览", use_column_width=True)
        title = st.text_input("壁纸标题")
        category = st.selectbox("分类", ["风景", "人物", "抽象", "动漫", "科技", "其他"])
        price = st.number_input("价格（积分）", min_value=10, value=100)
        if st.button("✨ 上架壁纸"):
            if title:
                image_path = save_wallpaper_image(uploaded_file, {})
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute("INSERT INTO wallpapers (creator, title, price_points, category, image_path) VALUES (?, ?, ?, ?, ?)",
                          (st.session_state.username, title, price, category, image_path))
                conn.commit()
                conn.close()
                st.success(f"✅ 壁纸「{title}」上架成功！")
                st.balloons()

def render_wallpaper_mall():
    st.markdown("### 🛒 壁纸商城")
    st.info("壁纸商城开发中")

def render_my_wallpapers():
    st.markdown("### 🖼️ 我的壁纸")
    st.info("我的壁纸")

def render_wallpaper_stats():
    st.markdown("### 📊 壁纸统计")
    st.info("壁纸统计")

# ========== 公益系统 ==========
WELFARE_PROJECTS = [
    {"id": 1, "name": "乡村儿童视频课", "points": 100, "icon": "🏫", "impact": "支持1个孩子上一节视频课"},
    {"id": 2, "name": "环保视频计划", "points": 50, "icon": "🌍", "impact": "支持1个环保视频拍摄"},
    {"id": 3, "name": "残障创作者支持", "points": 200, "icon": "❤️", "impact": "支持1位残障创作者"},
    {"id": 4, "name": "动物保护视频", "points": 30, "icon": "🐕", "impact": "帮助1只流浪动物"},
]
WELFARE_BADGES = [
    {"name": "爱心萌芽", "points": 100, "icon": "🌱"},
    {"name": "爱心使者", "points": 500, "icon": "🌟"},
    {"name": "爱心大使", "points": 1000, "icon": "💎"},
    {"name": "公益之星", "points": 5000, "icon": "🏆"},
    {"name": "公益传奇", "points": 10000, "icon": "👑"},
]

def get_welfare_points(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT total_donated FROM welfare_points WHERE user = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def add_welfare_points(username, points, project_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO welfare_points (user, total_donated) VALUES (?, 0)", (username,))
    c.execute("UPDATE welfare_points SET total_donated = total_donated + ? WHERE user = ?", (points, username))
    c.execute("INSERT INTO welfare_donations (user, project_id, points) VALUES (?, ?, ?)", (username, project_id, points))
    conn.commit()
    conn.close()

def render_welfare():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌍 公益积分")
    total_donated = get_welfare_points(st.session_state.username)
    st.markdown(f"**累计捐赠：{total_donated} 积分**")
    badges = []
    for badge in WELFARE_BADGES:
        if total_donated >= badge["points"]:
            badges.append(badge)
    if badges:
        st.markdown("**🏅 已获得勋章**")
        cols = st.columns(len(badges))
        for i, badge in enumerate(badges):
            with cols[i]:
                st.markdown(f"<div style='text-align:center'><div style='font-size:40px'>{badge['icon']}</div><div>{badge['name']}</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🌱 公益项目")
    for project in WELFARE_PROJECTS:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"<div style='font-size:40px'>{project['icon']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{project['name']}**")
            st.caption(project['impact'])
        with col3:
            st.markdown(f"💰 {project['points']}积分")
            if st.button(f"捐赠", key=f"donate_{project['id']}"):
                if spend_points(st.session_state.username, project['points'], f"公益捐赠-{project['name']}"):
                    add_welfare_points(st.session_state.username, project['points'], project['id'])
                    st.success(f"✅ 感谢你的爱心！已捐赠 {project['points']} 积分")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("积分不足")
        st.markdown("---")
    st.markdown("### 🏆 公益排行榜")
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user, total_donated FROM welfare_points ORDER BY total_donated DESC LIMIT 10")
    leaders = c.fetchall()
    if leaders:
        for i, leader in enumerate(leaders):
            st.markdown(f"{i+1}. {leader[0]} - 累计捐赠 {leader[1]} 积分")
    else:
        st.info("暂无公益记录")
    conn.close()
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 奖池金 ==========
def get_current_jackpot():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    current_month = time.strftime("%Y-%m")
    c.execute("SELECT total_points FROM jackpot WHERE month = ?", (current_month,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def render_jackpot():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💰 小智奖池金")
    current_jackpot = get_current_jackpot()
    st.markdown(f"**本月奖池金：{current_jackpot} 积分**")
    st.markdown("---")
    st.markdown("### 📊 奖池金来源")
    st.markdown("""
    | 来源 | 比例 | 说明 |
    |-----|------|------|
    | 版图/壁纸交易 | 10% | 平台抽成的50% |
    | 广告收益 | 20% | 广告收益的40% |
    | 创作者认证 | 100% | 认证费用 |
    """)
    st.markdown("---")
    st.markdown("### 🏆 本月排行榜")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🏅 创作者榜**")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT creator, SUM(amount_points) as total FROM poster_earnings GROUP BY creator ORDER BY total DESC LIMIT 5")
        creators = c.fetchall()
        if creators:
            for i, creator in enumerate(creators):
                st.markdown(f"{i+1}. {creator[0]} - {creator[1]}积分")
        else:
            st.info("暂无数据")
    with col2:
        st.markdown("**🌱 公益榜**")
        c.execute("SELECT user, total_donated FROM welfare_points ORDER BY total_donated DESC LIMIT 5")
        donors = c.fetchall()
        if donors:
            for i, donor in enumerate(donors):
                st.markdown(f"{i+1}. {donor[0]} - {donor[1]}积分")
        else:
            st.info("暂无数据")
        conn.close()
    st.markdown("---")
    st.markdown("🎁 奖池金分配规则")
    st.markdown("""
    - **50%** 分配给创作者榜Top5
    - **30%** 分配给公益榜Top5
    - **10%** 分配给新星榜Top4
    - **10%** 滚入下月奖池
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 智能推荐辅助函数 ==========
def get_user_preferences(username):
    """获取用户偏好标签（基于购买和当前视频）"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT p.title 
        FROM poster_collections pc 
        JOIN posters p ON pc.poster_id = p.id 
        WHERE pc.user = ? 
        ORDER BY pc.bought_at DESC LIMIT 5
    """, (username,))
    bought_titles = [row[0] for row in c.fetchall()]
    conn.close()
    
    video_path = st.session_state.get('video_path', '')
    video_name = os.path.basename(video_path) if video_path else ''
    
    keywords = []
    all_text = " ".join(bought_titles) + " " + video_name
    keyword_map = {
        "夏天": ["夏天", "夏日", "summer"],
        "海边": ["海边", "沙滩", "海", "beach"],
        "旅行": ["旅行", "旅游", "trip"],
        "美食": ["美食", "food"],
        "宠物": ["宠物", "猫", "狗", "pet"],
        "科技": ["科技", "tech"],
        "夜景": ["夜景", "night"],
        "城市": ["城市", "city"],
    }
    for tag, words in keyword_map.items():
        if any(w in all_text.lower() for w in words):
            keywords.append(tag)
    if not keywords:
        keywords = ["创意", "热门"]
    return keywords

# ========== 素材库（扩充） ==========
VIDEO_MATERIALS = [
    {"name": "夏日海滩", "tags": ["夏天", "海边"], "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    {"name": "城市夜景", "tags": ["城市", "夜景"], "url": "https://www.w3schools.com/html/movie.mp4"},
    {"name": "美食特写", "tags": ["美食"], "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    {"name": "萌宠日常", "tags": ["宠物"], "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    {"name": "旅行Vlog", "tags": ["旅行"], "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    {"name": "科技未来", "tags": ["科技"], "url": "https://www.w3schools.com/html/movie.mp4"},
    {"name": "春日樱花", "tags": ["春天", "浪漫"], "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    {"name": "雪山风景", "tags": ["冬天", "自然"], "url": "https://www.w3schools.com/html/movie.mp4"},
    {"name": "街拍时尚", "tags": ["城市", "潮流"], "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
]

MUSIC_MATERIALS = [
    {"name": "轻快吉他", "tags": ["轻快"], "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"},
    {"name": "舒缓钢琴", "tags": ["舒缓"], "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"},
    {"name": "动感节奏", "tags": ["动感"], "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"},
    {"name": "治愈系", "tags": ["治愈"], "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"},
    {"name": "电子舞曲", "tags": ["电子"], "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"},
]

TEXT_TEMPLATES = [
    {"name": "夏日文案", "text": "夏天的风，吹过海面", "tags": ["夏天"]},
    {"name": "旅行标语", "text": "在路上，遇见自己", "tags": ["旅行"]},
    {"name": "美食语录", "text": "唯有美食与爱不可辜负", "tags": ["美食"]},
    {"name": "春日寄语", "text": "春风十里，不如你", "tags": ["春天"]},
    {"name": "励志金句", "text": "努力是奇迹的另一个名字", "tags": ["励志"]},
]

def get_materials_for_story(story_text):
    """根据故事文本返回匹配的素材列表（名称和URL）"""
    story_lower = story_text.lower()
    selected = set()
    for material in VIDEO_MATERIALS:
        for tag in material["tags"]:
            if tag in story_lower:
                selected.add(material["name"])
    if not selected:
        selected = {VIDEO_MATERIALS[0]["name"], VIDEO_MATERIALS[1]["name"]}
    result = [m for m in VIDEO_MATERIALS if m["name"] in selected]
    return result

# ========== 视频合成辅助函数 ==========
CACHE_DIR = "cached_videos"
os.makedirs(CACHE_DIR, exist_ok=True)

def download_video(url, save_path):
    """下载远程视频到本地"""
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_path

def get_cached_video(url):
    """获取本地缓存的视频路径，如果不存在则下载"""
    filename = hashlib.md5(url.encode()).hexdigest() + ".mp4"
    cache_path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(cache_path):
        download_video(url, cache_path)
    return cache_path

def synthesize_video_from_story(materials, output_path, progress_callback=None):
    """将匹配到的素材列表合成视频"""
    clips = []
    for i, material in enumerate(materials):
        local_path = get_cached_video(material['url'])
        clip = VideoFileClip(local_path)
        # 可选：截取片段（比如只取前5秒）
        # clip = clip.subclip(0, min(5, clip.duration))
        clips.append(clip)
        if progress_callback:
            progress_callback((i+1)/len(materials))
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    for clip in clips:
        clip.close()

# ========== 小智AI助手（重构为AI创作页） ==========
def render_ai_creation_page():
    st.markdown("### 🤖 AI创作工具箱")
    
    # 今日推荐工具
    st.markdown("#### 🌟 今日推荐")
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("<div style='font-size: 48px;'>🎬</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("**AI故事成片**\n只需输入故事梗概，AI自动生成分镜脚本并匹配素材，一键合成视频。")
            if st.button("立即体验", key="today_tool"):
                st.session_state.current_ai_tool = "story_to_video"
                st.rerun()
    st.markdown("---")
    
    # 工具列表
    tools = [
        {"icon": "🎬", "name": "AI故事成片", "desc": "输入故事，生成分镜脚本和视频", "func": "story_to_video"},
        {"icon": "📝", "name": "图文成片", "desc": "输入文字，自动生成视频", "func": "text_to_video"},
        {"icon": "✂️", "name": "AI剪视频", "desc": "智能分析视频，推荐剪辑点", "func": "ai_cut"},
        {"icon": "🎬", "name": "AI视频生成", "desc": "文本描述生成视频", "func": "text_to_video_advanced"},
        {"icon": "🎤", "name": "智能提词拍摄", "desc": "提词器+AI台词生成", "func": "teleprompter"},
        {"icon": "🎭", "name": "表情包工厂", "desc": "从视频制作GIF表情", "func": "meme_factory"},
        {"icon": "🎵", "name": "变声器", "desc": "改变音频音色", "func": "voice_changer"},
        {"icon": "🏆", "name": "每日挑战", "desc": "完成创作任务赢积分", "func": "daily_challenge"},
    ]
    
    # 2列网格
    cols = st.columns(2)
    for i, tool in enumerate(tools):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"""
                <div style="background: white; border-radius: 16px; padding: 15px; margin-bottom: 15px;">
                    <div style="font-size: 32px;">{tool['icon']}</div>
                    <div><strong>{tool['name']}</strong></div>
                    <div style="color: gray; font-size: 12px;">{tool['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"使用 {tool['name']}", key=tool['func'], use_container_width=True):
                    st.session_state.current_ai_tool = tool['func']
                    st.rerun()
    
    # 显示选中的工具界面
    if 'current_ai_tool' in st.session_state:
        tool = st.session_state.current_ai_tool
        st.markdown("---")
        tool_names = {t['func']: t['name'] for t in tools}
        st.markdown(f"### {tool_names[tool]}")
        
        if tool == "story_to_video":
            story_prompt = st.text_area("输入故事梗概", height=100, placeholder="例如：一个宇航员在火星上发现了一朵花")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("生成分镜脚本", use_container_width=True):
                    if story_prompt:
                        with st.spinner("正在生成分镜..."):
                            script = f"""
                            镜头1：{story_prompt[:20]}... 引入场景（5秒）
                            镜头2：细节特写，展示关键元素（8秒）
                            镜头3：情感爆发或转折（5秒）
                            镜头4：结局，留下想象空间（4秒）
                            """
                            st.success("分镜脚本已生成")
                            st.text(script)
                    else:
                        st.warning("请输入故事梗概")
            with col2:
                if st.button("一键成片", use_container_width=True):
                    if story_prompt:
                        with st.spinner("正在从素材库选取片段..."):
                            materials = get_materials_for_story(story_prompt)
                            if materials:
                                st.info(f"✅ 已匹配到 {len(materials)} 个相关素材：{', '.join([m['name'] for m in materials])}")
                                progress_bar = st.progress(0)
                                def update_progress(p):
                                    progress_bar.progress(int(p * 100))
                                output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                                try:
                                    synthesize_video_from_story(materials, output_file, progress_callback=update_progress)
                                    st.success("视频合成完成！点击下载")
                                    with open(output_file, "rb") as f:
                                        st.download_button("下载视频", f, file_name="story_video.mp4", mime="video/mp4")
                                except Exception as e:
                                    st.error(f"合成失败：{e}")
                                progress_bar.empty()
                            else:
                                st.warning("未能匹配到素材，请尝试更具体的故事描述")
                    else:
                        st.warning("请输入故事梗概")
        
        elif tool == "text_to_video":
            st.markdown("#### 图文成片")
            title = st.text_input("标题", placeholder="请输入视频标题")
            content = st.text_area("正文", height=150, placeholder="输入你想表达的内容...")
            if st.button("生成视频", use_container_width=True):
                if title and content:
                    with st.spinner("正在生成视频..."):
                        time.sleep(2)
                        st.success("视频生成完成！点击下载（演示）")
                        st.download_button("下载视频", data=b"fake video", file_name="text2video.mp4")
                else:
                    st.warning("请填写标题和正文")
        
        elif tool == "ai_cut":
            st.info("AI剪视频功能开发中，敬请期待！")
        elif tool == "text_to_video_advanced":
            st.info("AI视频生成功能开发中，敬请期待！")
        elif tool == "teleprompter":
            render_teleprompter()
        elif tool == "meme_factory":
            render_meme_factory()
        elif tool == "voice_changer":
            st.info("变声器功能开发中，敬请期待！")
        elif tool == "daily_challenge":
            st.info("每日挑战功能开发中，敬请期待！")
        
        if st.button("← 返回工具箱", use_container_width=True):
            del st.session_state.current_ai_tool
            st.rerun()

# ========== 剪辑页面 ==========
def render_clip_page():
    # 模板中心
    st.markdown("#### 🎨 热门模板")
    templates = [
        {"name": "春日回忆", "image": "https://picsum.photos/300/200?random=1", "desc": "春天主题，温暖治愈"},
        {"name": "旅行Vlog", "image": "https://picsum.photos/300/200?random=2", "desc": "旅行风景，自由轻松"},
        {"name": "美食诱惑", "image": "https://picsum.photos/300/200?random=3", "desc": "美食特写，诱人口感"},
    ]
    cols = st.columns(3)
    for i, tpl in enumerate(templates):
        with cols[i]:
            st.image(tpl["image"], use_column_width=True)
            st.caption(f"**{tpl['name']}**\n{tpl['desc']}")
            if st.button(f"使用模板", key=f"tpl_{i}"):
                st.info(f"模板 {tpl['name']} 已添加到待编辑列表（功能开发中）")
    st.markdown("---")
    
    st.markdown("### 🎬 开始创作")
    uploaded = st.file_uploader("", type=["mp4", "mov", "avi"], label_visibility="collapsed", key="clip_upload")
    if uploaded:
        video_path = save_uploaded_file(uploaded)
        st.session_state.video_path = video_path
        st.video(video_path)
        st.success("✅ 上传成功！")
        
        st.markdown("#### ✂️ 剪辑工具")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("剪切视频", use_container_width=True):
                if st.session_state.get('video_path'):
                    dur = get_video_info(st.session_state.video_path)["duration"]
                    with st.expander("设置剪切时间", expanded=True):
                        start = st.number_input("开始(秒)", 0.0, dur, 0.0)
                        end = st.number_input("结束(秒)", 0.0, dur, min(5.0, dur))
                        if st.button("确认剪切"):
                            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                            cut_video(st.session_state.video_path, start, end, out)
                            with open(out, "rb") as f:
                                st.download_button("下载", f, file_name="cut.mp4")
                else:
                    st.warning("请先上传视频")
        with col2:
            if st.button("视频变速", use_container_width=True):
                if st.session_state.get('video_path'):
                    with st.expander("选择速度", expanded=True):
                        def apply_speed(s):
                            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                            speed_video(st.session_state.video_path, s, out)
                            with open(out, "rb") as f:
                                st.download_button("下载", f, file_name=f"speed_{s}x.mp4")
                        cols_s = st.columns(4)
                        with cols_s[0]:
                            if st.button("0.5x"): apply_speed(0.5)
                        with cols_s[1]:
                            if st.button("1.0x"): apply_speed(1.0)
                        with cols_s[2]:
                            if st.button("1.5x"): apply_speed(1.5)
                        with cols_s[3]:
                            if st.button("2.0x"): apply_speed(2.0)
                        speed = st.number_input("自定义倍数", 0.5, 2.0, 1.0, step=0.1)
                        if st.button("应用自定义"):
                            apply_speed(speed)
                else:
                    st.warning("请先上传视频")
        with col3:
            if st.button("导出GIF", use_container_width=True):
                if st.session_state.get('video_path'):
                    with st.expander("设置GIF参数", expanded=True):
                        start = st.number_input("开始时间(秒)", 0.0, 10.0, 0.0)
                        duration = st.number_input("时长(秒)", 1.0, 10.0, 3.0)
                        if st.button("确认导出"):
                            out = tempfile.NamedTemporaryFile(suffix=".gif", delete=False).name
                            video_to_gif(st.session_state.video_path, out, start, duration)
                            with open(out, "rb") as f:
                                st.download_button("下载", f, file_name="output.gif")
                else:
                    st.info("请先上传视频")
        with col4:
            if st.button("美颜滤镜", use_container_width=True):
                st.info("美颜滤镜开发中，敬请期待")
    else:
        # 未上传时显示大按钮
        st.markdown("""
        <div style="text-align:center; padding: 50px; border: 2px dashed #ccc; border-radius: 20px;">
            <div style="font-size: 48px;">📤</div>
            <p>点击或拖拽视频开始创作</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("#### 🔥 热门工具")
    hot_tools = [
        ("🎬 AI故事成片", "ai_story"),
        ("📝 图文成片", "text2video"),
        ("✂️ AI剪视频", "ai_cut"),
        ("🎤 智能提词", "teleprompter"),
    ]
    cols = st.columns(2)
    for i, (name, key) in enumerate(hot_tools):
        with cols[i % 2]:
            if st.button(name, use_container_width=True):
                st.session_state.nav_index = 1
                st.session_state.current_ai_tool = key
                st.rerun()

# ========== 素材页面 ==========
def render_material_page():
    st.markdown("### 📦 素材库")
    
    # 智能推荐
    st.markdown("#### 🧠 为你推荐")
    preferences = get_user_preferences(st.session_state.username)
    recommended = []
    for m in VIDEO_MATERIALS:
        score = sum(1 for tag in m["tags"] if tag in preferences)
        if score > 0:
            recommended.append((score, m))
    recommended.sort(reverse=True, key=lambda x: x[0])
    recommended = [m for score, m in recommended][:3]
    if not recommended:
        recommended = VIDEO_MATERIALS[:2]
    cols = st.columns(len(recommended))
    for i, m in enumerate(recommended):
        with cols[i]:
            st.video(m["url"], format="video/mp4", start_time=0)
            st.caption(f"**{m['name']}**  /  {' '.join(['#'+t for t in m['tags']])}")
            if st.button(f"应用", key=f"rec_{i}"):
                st.info(f"已将 {m['name']} 添加到待编辑列表")
    
    st.markdown("---")
    
    # 分类标签
    tab1, tab2, tab3, tab4 = st.tabs(["🎬 视频素材", "🎵 背景音乐", "📝 文字模板", "🎨 数字资产"])
    
    with tab1:
        cols = st.columns(3)
        for i, m in enumerate(VIDEO_MATERIALS):
            with cols[i % 3]:
                st.video(m["url"], format="video/mp4", start_time=0)
                st.caption(f"**{m['name']}**  /  {' '.join(['#'+t for t in m['tags']])}")
                if st.button(f"应用", key=f"video_{i}"):
                    st.info(f"已将 {m['name']} 添加到待编辑列表")
    
    with tab2:
        cols = st.columns(3)
        for i, m in enumerate(MUSIC_MATERIALS):
            with cols[i % 3]:
                st.audio(m["url"], format="audio/mp3")
                st.caption(f"**{m['name']}**")
                if st.button(f"应用", key=f"music_{i}"):
                    st.info(f"已将 {m['name']} 添加到配乐列表")
    
    with tab3:
        cols = st.columns(3)
        for i, tpl in enumerate(TEXT_TEMPLATES):
            with cols[i % 3]:
                st.markdown(f"<div style='background:#f5f5f5; padding:10px; border-radius:10px;'>{tpl['text']}</div>", unsafe_allow_html=True)
                st.caption(f"**{tpl['name']}**")
                if st.button(f"复制", key=f"text_{i}"):
                    st.info(f"已复制到剪贴板")
    
    with tab4:
        st.markdown("#### 版图系统")
        if st.button("进入版图系统", use_container_width=True):
            with st.expander("版图系统", expanded=True):
                poster_tabs = st.tabs(["✨ 生成版图", "🛒 版图商城", "🖼️ 我的版图", "💎 我的收藏", "📊 版图统计"])
                with poster_tabs[0]:
                    render_poster_generator()
                with poster_tabs[1]:
                    render_poster_mall()
                with poster_tabs[2]:
                    render_my_posters()
                with poster_tabs[3]:
                    render_my_collections()
                with poster_tabs[4]:
                    render_poster_stats()
        st.markdown("#### 壁纸系统")
        if st.button("进入壁纸系统", use_container_width=True):
            with st.expander("壁纸系统", expanded=True):
                wallpaper_tabs = st.tabs(["🎨 创作壁纸", "🛒 壁纸商城", "🖼️ 我的壁纸", "📊 壁纸统计"])
                with wallpaper_tabs[0]:
                    render_wallpaper_generator()
                with wallpaper_tabs[1]:
                    render_wallpaper_mall()
                with wallpaper_tabs[2]:
                    render_my_wallpapers()
                with wallpaper_tabs[3]:
                    render_wallpaper_stats()

# ========== 社区页面 ==========
def render_community_page():
    st.markdown("### 🌐 灵感社区")
    
    # 热门话题
    st.markdown("#### 🔥 热门话题")
    topics = ["#夏日创作", "#AI故事", "#旅行Vlog", "#美食日记"]
    cols = st.columns(len(topics))
    for i, topic in enumerate(topics):
        with cols[i]:
            if st.button(topic, use_container_width=True):
                st.info(f"话题 {topic} 功能开发中，敬请期待！")
    st.markdown("---")
    
    # 展示作品
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, title, price_points, image_path FROM posters WHERE status='on_sale' ORDER BY created_at DESC LIMIT 6")
    rec = c.fetchall()
    conn.close()
    if rec:
        cols = st.columns(2)
        for i, (pid, title, price, img) in enumerate(rec):
            with cols[i%2]:
                if img and os.path.exists(img):
                    st.image(img, use_column_width=True)
                st.markdown(f"**{title}**")
                st.caption(f"💰 {price}积分")
                if st.button(f"查看详情", key=f"com_{pid}"):
                    st.info("详情页开发中")
    else:
        st.markdown("### 🎨 灵感示例")
        st.image("https://picsum.photos/300/200?random=1", caption="示例作品1")
        st.image("https://picsum.photos/300/200?random=2", caption="示例作品2")
        st.caption("快去创作你的第一个作品吧！")

# ========== 我的页面 ==========
def render_my_page():
    st.markdown("### 👤 我的")
    
    points = get_points(st.session_state.username)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM posters WHERE creator = ?", (st.session_state.username,))
    poster_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM wallpapers WHERE creator = ?", (st.session_state.username,))
    wallpaper_count = c.fetchone()[0]
    conn.close()
    welfare = get_welfare_points(st.session_state.username)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("积分", points)
    with col2:
        st.metric("作品", poster_count + wallpaper_count)
    with col3:
        st.metric("公益", welfare)
    
    # 创作日历（模拟）
    st.markdown("#### 📅 创作日历")
    days = ["一", "二", "三", "四", "五", "六", "日"]
    import random
    active = [random.choice([0,1,1,1,2,2]) for _ in range(7)]
    cols = st.columns(7)
    for i, (day, act) in enumerate(zip(days, active)):
        with cols[i]:
            color = "#4caf50" if act >= 2 else "#ff9800" if act == 1 else "#ddd"
            st.markdown(f"<div style='text-align:center; background:{color}; border-radius:8px; padding:5px;'>{day}<br>{'🔥'*act}</div>", unsafe_allow_html=True)
    st.caption("绿色：高产日 | 橙色：有创作 | 灰色：无活动")
    
    # 任务中心
    st.markdown("#### 🎯 今日任务")
    tasks = [
        {"name": "上传一个视频", "reward": "+10积分", "done": False},
        {"name": "使用一次AI故事成片", "reward": "+20积分", "done": False},
        {"name": "公益捐赠", "reward": "+5积分", "done": welfare > 0},
    ]
    for task in tasks:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{task['name']}**")
        with col2:
            st.markdown(f"奖励: {task['reward']}")
        with col3:
            if task["done"]:
                st.success("已完成")
            else:
                if st.button("去完成", key=f"task_{task['name']}"):
                    st.info("功能开发中，敬请期待！")
    st.markdown("---")
    
    # 原有 tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📦 我的作品", "❤️ 我的收藏", "🌍 公益", "⚙️ 设置"])
    with tab1:
        st.markdown("#### 🖼️ 我的版图")
        render_my_posters()
        st.markdown("#### 🖼️ 我的壁纸")
        render_my_wallpapers()
    with tab2:
        st.markdown("#### 💎 我的收藏")
        render_my_collections()
    with tab3:
        render_welfare()
        st.markdown("---")
        render_jackpot()
    with tab4:
        if st.button("消息中心"):
            render_messages()
        st.markdown("---")
        render_language()
        st.markdown("---")
        if st.button("退出登录"):
            st.session_state.clear()
            st.rerun()

# ========== 界面函数 ==========
def render_auth():
    with st.sidebar:
        st.markdown("### 👤 用户中心")
        if not st.session_state.get('logged_in', False):
            tab = st.radio("", ["登录", "注册"], horizontal=True)
            if tab == "登录":
                username = st.text_input("用户名")
                password = st.text_input("密码", type="password")
                if st.button("登录"):
                    ok, msg = login_user(username, password)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                username = st.text_input("用户名")
                password = st.text_input("密码", type="password")
                confirm = st.text_input("确认密码", type="password")
                if st.button("注册"):
                    if password != confirm:
                        st.error("两次密码不一致")
                    else:
                        ok, msg = register_user(username, password)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            st.stop()
        else:
            points = get_points(st.session_state.username)
            st.success(f"欢迎，{st.session_state.username}")
            st.markdown(f'<div class="points-badge">⭐ 积分：{points}</div>', unsafe_allow_html=True)
            if st.button("退出登录"):
                st.session_state.clear()
                st.rerun()

def render_language():
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("中文"):
                st.session_state.language = 'zh'
                st.rerun()
        with col2:
            if st.button("English"):
                st.session_state.language = 'en'
                st.rerun()

def render_teleprompter():
    st.markdown("### 🎤 提词拍摄")
    st.markdown("在摄像头画面上显示台词，滚动提词，告别忘词！")
    script = st.text_area("请输入你的台词", height=100, placeholder="例如：大家好，欢迎来到我的直播间……")
    scroll_speed = st.slider("滚动速度（字/秒）", 1, 10, 3)
    camera_image = st.camera_input("点击拍照", key="teleprompter_camera")
    if camera_image:
        st.image(camera_image, caption="拍摄的照片", use_column_width=True)
        if script:
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 10px; font-family: monospace; font-size: 20px; white-space: pre-wrap;">
                {script}
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"滚动速度：{scroll_speed} 字/秒")
        else:
            st.warning("请输入台词")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("生成版图"):
                st.info("提词拍摄的照片已保存，可到「数字资产系统」中生成版图")
        with col2:
            if st.button("制作壁纸"):
                st.info("提词拍摄的照片已保存，可到「数字资产系统」中制作壁纸")

def render_meme_factory():
    st.markdown("### 🎭 表情包工厂")
    st.markdown("从视频中截取精彩片段，添加文字，生成专属表情包GIF")
    uploaded = st.file_uploader("上传视频", type=["mp4", "mov", "avi"], key="meme_upload")
    if uploaded:
        video_path = save_uploaded_file(uploaded)
        st.video(video_path)
        st.markdown("#### 截取片段")
        col1, col2 = st.columns(2)
        with col1:
            start = st.number_input("开始时间(秒)", 0.0, 10.0, 0.0, step=0.5)
        with col2:
            duration = st.number_input("时长(秒)", 1.0, 10.0, 3.0, step=0.5)
        st.markdown("#### 添加文字")
        text_options = ["我太难了", "惊呆了", "哈哈哈", "奥利给", "自定义"]
        selected_text = st.selectbox("选择模板", text_options)
        if selected_text == "自定义":
            custom_text = st.text_input("输入文字", placeholder="例如：这操作太秀了")
            meme_text = custom_text if custom_text else ""
        else:
            meme_text = selected_text
        if st.button("生成表情包"):
            if meme_text:
                with st.spinner("正在生成GIF..."):
                    out = tempfile.NamedTemporaryFile(suffix=".gif", delete=False).name
                    video_to_gif(video_path, out, start, duration)
                    try:
                        from PIL import Image, ImageDraw, ImageFont
                        gif = Image.open(out)
                        draw = ImageDraw.Draw(gif)
                        try:
                            font = ImageFont.truetype("arial.ttf", 30)
                        except:
                            font = ImageFont.load_default()
                        draw.text((50, 50), meme_text, fill="white", font=font)
                        gif.save(out)
                        st.success("GIF生成成功！")
                        with open(out, "rb") as f:
                            st.download_button("下载GIF", f, file_name="meme.gif")
                    except Exception as e:
                        st.error(f"添加文字失败：{e}")
            else:
                st.warning("请输入文字")

# ========== 主程序 ==========
def main():
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    if st.session_state.get('remember_me', False):
        if 'username' in st.session_state:
            st.session_state.logged_in = True
    
    init_db()
    init_poster_tables()
    init_wallpaper_tables()
    init_welfare_tables()
    init_jackpot_tables()
    
    render_language()
    render_auth()
    
    if not st.session_state.get('logged_in', False):
        st.markdown("""
        <div class="main-header">
            <div style="font-size: 60px;">🤖</div>
            <h1>小智 - 智能视频助手</h1>
            <p>你的AI视频创作伙伴</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("👈 请先在左侧登录或注册")
        return
    
    # 底部导航栏
    if 'nav_index' not in st.session_state:
        st.session_state.nav_index = 0
    
    nav_items = ["🎬 剪辑", "🤖 AI创作", "📦 素材", "🌐 社区", "👤 我的"]
    cols = st.columns(len(nav_items))
    for i, name in enumerate(nav_items):
        with cols[i]:
            if st.button(name, use_container_width=True):
                st.session_state.nav_index = i
                st.rerun()
    
    # 根据导航显示不同页面
    if st.session_state.nav_index == 0:
        render_clip_page()
    elif st.session_state.nav_index == 1:
        render_ai_creation_page()
    elif st.session_state.nav_index == 2:
        render_material_page()
    elif st.session_state.nav_index == 3:
        render_community_page()
    else:
        render_my_page()

if __name__ == "__main__":
    main()
