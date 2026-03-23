"""
智能视频助手 v5.0
完整系统 - 视频编辑、AI助手、智能抠像、积分商城、五级管理员
"""

import streamlit as st
import os
import sys
import json
import time
import hashlib
import sqlite3
import tempfile
import subprocess
import threading
import random
import secrets
import base64
import logging
import gc
import re
import shutil
from datetime import datetime, timedelta
from PIL import Image
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import psutil

# ========== 版本信息 ==========
VERSION = "5.0"
APP_NAME = "智能视频助手"
DEVELOPER = "李国锐"
COPYRIGHT = f"© 2026 {APP_NAME}"

# ========== 页面配置 ==========
st.set_page_config(
    page_title=f"{APP_NAME} v{VERSION}",
    page_icon="static/icon.svg",
    layout="wide",
    initial_sidebar_state="auto"
)

# ========== 语言资源 ==========
LANG = {
    "zh": {
        "title": f"{APP_NAME} v{VERSION}",
        "user_center": "👤 用户中心",
        "login": "登录",
        "register": "注册",
        "username": "用户名",
        "password": "密码",
        "confirm": "确认密码",
        "login_btn": "登录",
        "register_btn": "注册",
        "logout": "注销",
        "welcome": "欢迎回来",
        "points": "⭐ 积分",
        "quick_functions": "快速功能",
        "pro_mode": "⭐ 专业模式",
        "pro_tools": "🔧 专业工具",
        "cut": "剪切视频",
        "merge": "合并视频",
        "add_text": "添加文字水印",
        "apply_filter": "应用滤镜",
        "export": "导出设置",
        "speed": "视频变速",
        "ai_assistant": "AI助手",
        "points_mall": "积分商城",
        "multi_track": "多轨道时间线",
        "current_function": "当前功能",
        "upload_first": "请上传视频后使用",
        "password_mismatch": "两次密码不一致",
        "user_exists": "用户名已存在",
        "register_success": "注册成功",
        "login_success": "登录成功",
        "user_not_exist": "用户名不存在",
        "wrong_password": "密码错误",
        "language": "语言",
        "filters": "滤镜特效",
        "filter_intensity": "强度",
        "preview": "预览",
        "auto_preview": "自动预览",
        "apply": "应用",
        "download": "下载视频",
        "video_sites": "📺 视频网站",
        "movie_search": "🔍 影视搜索",
        "security": "🛡️ 安全与隐私",
        "about": "📄 关于",
        "report_bug": "🐛 报告问题",
        "contact": "📧 联系我们",
        "smart_matting": "✨ 智能抠像",
        "remove_bg": "移除背景",
        "replace_bg": "替换背景",
        "bg_color": "背景颜色",
        "bg_image": "自定义背景图片",
        "mode_fast": "快速模式",
        "mode_precise": "精确模式",
        "material_library": "📚 素材库",
        "search_material": "搜索素材",
        "hot_materials": "热门推荐",
        "video_materials": "视频素材",
        "image_materials": "图片素材",
        "audio_materials": "音频素材"
    },
    "en": {
        "title": f"{APP_NAME} v{VERSION}",
        "user_center": "👤 User Center",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "confirm": "Confirm Password",
        "login_btn": "Login",
        "register_btn": "Register",
        "logout": "Logout",
        "welcome": "Welcome back",
        "points": "⭐ Points",
        "quick_functions": "Quick Functions",
        "pro_mode": "⭐ Pro Mode",
        "pro_tools": "🔧 Pro Tools",
        "cut": "Cut Video",
        "merge": "Merge Videos",
        "add_text": "Add Text Overlay",
        "apply_filter": "Apply Filter",
        "export": "Export Settings",
        "speed": "Video Speed",
        "ai_assistant": "AI Assistant",
        "points_mall": "Points Mall",
        "multi_track": "Multi-Track Timeline",
        "current_function": "Current Function",
        "upload_first": "Please upload a video first",
        "password_mismatch": "Passwords do not match",
        "user_exists": "Username already exists",
        "register_success": "Registration successful",
        "login_success": "Login successful",
        "user_not_exist": "Username does not exist",
        "wrong_password": "Wrong password",
        "language": "Language",
        "filters": "Filters & Effects",
        "filter_intensity": "Intensity",
        "preview": "Preview",
        "auto_preview": "Auto Preview",
        "apply": "Apply",
        "download": "Download Video",
        "video_sites": "📺 Video Sites",
        "movie_search": "🔍 Movie Search",
        "security": "🛡️ Security & Privacy",
        "about": "📄 About",
        "report_bug": "🐛 Report Issue",
        "contact": "📧 Contact Us",
        "smart_matting": "✨ Smart Matting",
        "remove_bg": "Remove Background",
        "replace_bg": "Replace Background",
        "bg_color": "Background Color",
        "bg_image": "Custom Background",
        "mode_fast": "Fast Mode",
        "mode_precise": "Precise Mode",
        "material_library": "📚 Material Library",
        "search_material": "Search Materials",
        "hot_materials": "Hot Recommendations",
        "video_materials": "Video Materials",
        "image_materials": "Image Materials",
        "audio_materials": "Audio Materials"
    }
}

def t(key):
    current_lang = st.session_state.get('language', 'zh')
    return LANG[current_lang].get(key, key)


# ========== 辅助函数 ==========

def save_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    suffix = os.path.splitext(uploaded_file.name)[1]
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tfile.write(uploaded_file.getbuffer())
    return tfile.name

def cleanup_temp_files(paths):
    for p in paths:
        if p and os.path.exists(p):
            try:
                os.unlink(p)
            except:
                pass

def cleanup_all_temp():
    temp_dir = tempfile.gettempdir()
    cleaned = 0
    for f in os.listdir(temp_dir):
        if f.startswith("tmp") and f.endswith((".mp4", ".jpg", ".mp3", ".srt")):
            try:
                os.unlink(os.path.join(temp_dir, f))
                cleaned += 1
            except:
                pass
    return cleaned

@st.cache_data(ttl=3600, show_spinner=False)
def get_video_info(video_path):
    if not os.path.exists(video_path):
        return None
    from moviepy.editor import VideoFileClip
    clip = VideoFileClip(video_path)
    info = {
        "duration": clip.duration,
        "width": clip.w,
        "height": clip.h,
        "fps": clip.fps
    }
    clip.close()
    return info

def is_mobile():
    ua = st.context.headers.get("User-Agent", "").lower()
    return "mobile" in ua or "android" in ua or "iphone" in ua

def get_client_ip():
    try:
        headers = st.context.headers
        if headers:
            forwarded = headers.get("X-Forwarded-For")
            if forwarded:
                return forwarded.split(",")[0].strip()
    except:
        pass
    return "127.0.0.1"


# ========== 数据库初始化 ==========

def init_all_dbs():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    salt TEXT,
                    email TEXT UNIQUE,
                    email_verified INTEGER DEFAULT 0,
                    admin_level INTEGER DEFAULT 0,
                    is_admin INTEGER DEFAULT 0,
                    is_super_admin INTEGER DEFAULT 0,
                    phone TEXT UNIQUE,
                    phone_verified INTEGER DEFAULT 0,
                    agreed_version TEXT DEFAULT '0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_settings (
                    username TEXT PRIMARY KEY,
                    default_output_format TEXT DEFAULT 'mp4',
                    default_bitrate TEXT DEFAULT '2000k',
                    default_fontsize INTEGER DEFAULT 50,
                    default_text_color TEXT DEFAULT '#FFFFFF',
                    default_filter TEXT DEFAULT '无',
                    receive_messages INTEGER DEFAULT 1,
                    preview_quality REAL DEFAULT 0.25
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_points (
                    username TEXT PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    last_daily_login TIMESTAMP
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS point_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    amount INTEGER,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action TEXT,
                    params TEXT,
                    ip TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ip_blacklist (
                    ip TEXT PRIMARY KEY,
                    reason TEXT,
                    blocked_until TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    conn.commit()
    conn.close()


def hash_password(password, salt=None):
    import hashlib, secrets
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return pwd_hash, salt


def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash, salt, admin_level FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False, t("user_not_exist")
    
    stored_hash, salt, admin_level = row
    input_hash, _ = hash_password(password, salt)
    
    if input_hash == stored_hash:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.admin_level = admin_level
        return True, t("login_success")
    
    return False, t("wrong_password")


def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False, t("user_exists")
    
    pwd_hash, salt = hash_password(password)
    c.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, pwd_hash, salt))
    conn.commit()
    conn.close()
    return True, t("register_success")


def get_points(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT points FROM user_points WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def add_points(username, amount, reason):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_points (username, points) VALUES (?, 0)", (username,))
    c.execute("UPDATE user_points SET points = points + ? WHERE username=?", (amount, username))
    c.execute("INSERT INTO point_transactions (username, amount, reason) VALUES (?, ?, ?)", (username, amount, reason))
    conn.commit()
    conn.close()


def log_action(username, action, params=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_logs (username, action, params, ip) VALUES (?, ?, ?, ?)",
              (username, action, json.dumps(params), get_client_ip()))
    conn.commit()
    conn.close()


def is_ip_banned(ip):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT blocked_until FROM ip_blacklist WHERE ip=?", (ip,))
    row = c.fetchone()
    conn.close()
    if row:
        blocked_until = datetime.fromisoformat(row[0])
        if blocked_until > datetime.now():
            return True
    return False


def ban_ip(ip, reason, expire_seconds=3600):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    expires = datetime.now() + timedelta(seconds=expire_seconds)
    c.execute("INSERT OR REPLACE INTO ip_blacklist (ip, reason, blocked_until) VALUES (?, ?, ?)",
              (ip, reason, expires))
    conn.commit()
    conn.close()


def get_user_settings(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_settings WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "default_output_format": row[1],
            "default_bitrate": row[2],
            "default_fontsize": row[3],
            "default_text_color": row[4],
            "default_filter": row[5],
            "receive_messages": row[6],
            "preview_quality": row[7]
        }
    return {
        "default_output_format": "mp4",
        "default_bitrate": "2000k",
        "default_fontsize": 50,
        "default_text_color": "#FFFFFF",
        "default_filter": "无",
        "receive_messages": 1,
        "preview_quality": 0.25
    }


def save_user_settings(username, settings):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO user_settings 
        (username, default_output_format, default_bitrate, default_fontsize,
         default_text_color, default_filter, receive_messages, preview_quality)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username,
          settings.get("default_output_format", "mp4"),
          settings.get("default_bitrate", "2000k"),
          settings.get("default_fontsize", 50),
          settings.get("default_text_color", "#FFFFFF"),
          settings.get("default_filter", "无"),
          settings.get("receive_messages", 1),
          settings.get("preview_quality", 0.25)))
    conn.commit()
    conn.close()


# ========== 视频处理函数 ==========

def cut_video_ffmpeg(input_path, start, end, output_path):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-to", str(end), "-c", "copy", output_path], check=True)

def change_speed_ffmpeg(input_path, speed, output_path):
    subprocess.run([
        "ffmpeg", "-i", input_path,
        "-filter:v", f"setpts={1/speed}*PTS",
        "-filter:a", f"atempo={speed}",
        "-c:a", "aac", output_path
    ], check=True)


# ========== 用户认证界面 ==========

def render_auth():
    with st.sidebar:
        st.header(t("user_center"))
        
        if not st.session_state.get('logged_in', False):
            auth_tab = st.radio("", [t("login"), t("register")], horizontal=True)
            
            if auth_tab == t("login"):
                with st.form("login_form"):
                    username = st.text_input(t("username"))
                    password = st.text_input(t("password"), type="password")
                    
                    if st.form_submit_button(t("login_btn")):
                        ip = get_client_ip()
                        if is_ip_banned(ip):
                            st.error("您的IP已被封禁")
                        else:
                            ok, msg = login_user(username, password)
                            if ok:
                                log_action(username, "login", {"ip": ip})
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                                log_action(username, "login_failed", {"ip": ip})
            
            else:
                with st.form("register_form"):
                    new_username = st.text_input(t("username"))
                    new_password = st.text_input(t("password"), type="password")
                    confirm = st.text_input(t("confirm"), type="password")
                    
                    if st.form_submit_button(t("register_btn")):
                        if new_password != confirm:
                            st.error(t("password_mismatch"))
                        else:
                            ok, msg = register_user(new_username, new_password)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            
            st.stop()
        
        else:
            st.success(f"{t('welcome')}，{st.session_state.username}")
            
            points = get_points(st.session_state.username)
            st.write(f"{t('points')}：{points}")
            
            if st.button(t("logout")):
                log_action(st.session_state.username, "logout", {})
                st.session_state.clear()
                st.rerun()
            
            st.markdown("---")


# ========== 语言切换 ==========

def render_language_switcher():
    with st.sidebar:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇨🇳 中文", use_container_width=True):
                st.session_state.language = 'zh'
                st.rerun()
        with col2:
            if st.button("🇬🇧 English", use_container_width=True):
                st.session_state.language = 'en'
                st.rerun()
        st.markdown("---")


# ========== 用户设置界面 ==========

def render_user_settings():
    with st.sidebar.expander("⚙️ 用户设置", expanded=False):
        settings = get_user_settings(st.session_state.username)
        
        with st.form("user_settings_form"):
            output_format = st.selectbox("导出格式", ["mp4", "mov", "avi"], 
                                        index=["mp4","mov","avi"].index(settings["default_output_format"]))
            bitrate = st.selectbox("码率", ["1000k", "2000k", "5000k", "10000k"],
                                  index=["1000k","2000k","5000k","10000k"].index(settings["default_bitrate"]))
            fontsize = st.number_input("默认文字大小", 20, 100, settings["default_fontsize"])
            text_color = st.color_picker("默认文字颜色", settings["default_text_color"])
            preview_quality = st.slider("预览质量", 0.1, 0.5, settings["preview_quality"], step=0.05)
            receive_messages = st.checkbox("接收系统消息", value=settings["receive_messages"] == 1)
            
            if st.form_submit_button("保存设置"):
                new_settings = settings.copy()
                new_settings.update({
                    "default_output_format": output_format,
                    "default_bitrate": bitrate,
                    "default_fontsize": fontsize,
                    "default_text_color": text_color,
                    "preview_quality": preview_quality,
                    "receive_messages": 1 if receive_messages else 0
                })
                save_user_settings(st.session_state.username, new_settings)
                st.success("设置已保存")
                st.rerun()


# ========== 素材库界面 ==========

def render_material_library():
    st.subheader("📚 素材库")
    st.info("素材库开发中，敬请期待")


# ========== 智能抠像界面 ==========

def render_smart_matting():
    st.subheader("✨ 智能抠像")
    st.info("智能抠像开发中，敬请期待")


# ========== 视频网站入口 ==========

def render_video_sites():
    st.subheader("📺 视频网站")
    sites = [
        {"name": "爱奇艺", "url": "https://www.iqiyi.com", "icon": "🎬"},
        {"name": "腾讯视频", "url": "https://v.qq.com", "icon": "🐧"},
        {"name": "优酷", "url": "https://www.youku.com", "icon": "▶️"},
        {"name": "B站", "url": "https://www.bilibili.com", "icon": "📺"},
    ]
    cols = st.columns(2)
    for i, site in enumerate(sites):
        with cols[i % 2]:
            st.write(f"{site['icon']} **{site['name']}**")
            if st.button(f"访问", key=f"visit_{site['name']}", use_container_width=True):
                import webbrowser
                webbrowser.open(site['url'])
                st.info(f"正在打开 {site['name']}")


# ========== 影视搜索 ==========

def render_movie_search():
    st.subheader("🔍 影视搜索")
    keyword = st.text_input("请输入电影/电视剧名称")
    if keyword:
        st.markdown("### 🔗 在以下平台搜索")
        search_links = [
            ("爱奇艺", f"https://www.iqiyi.com/search?q={keyword}"),
            ("腾讯视频", f"https://v.qq.com/search?q={keyword}"),
            ("B站", f"https://search.bilibili.com/all?keyword={keyword}"),
        ]
        for name, url in search_links:
            st.markdown(f'<a href="{url}" target="_blank">🔍 在{name}搜索</a>', unsafe_allow_html=True)


# ========== 关于页面 ==========

def render_about():
    st.subheader("📄 关于")
    st.markdown(f"""
    **{APP_NAME} v{VERSION}**
    
    开发者：{DEVELOPER}
    
    **功能特性**：
    - ✂️ 视频剪辑（剪切、合并、变速）
    - 🎨 50+滤镜特效
    - 🤖 AI对话式剪辑
    - ✨ 智能抠像
    - 📖 小说转视频
    - 💰 积分商城
    - 👑 五级管理员系统
    - 🛡️ 银行级安全防护
    
    **开源许可**：MIT License
    
    {COPYRIGHT}
    """)


# ========== 主程序 ==========

def main():
    # 初始化
    init_all_dbs()
    
    # 创建必要目录
    os.makedirs("static", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    
    # 语言切换
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    render_language_switcher()
    
    # 显示认证界面
    render_auth()
    
    if not st.session_state.get('logged_in', False):
        return
    
    # 用户设置
    render_user_settings()
    
    # 侧边栏主菜单
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎨 功能菜单")
        
        core_functions = [t("cut"), t("merge"), t("add_text"), t("apply_filter"), t("export")]
        advanced_functions = [t("speed"), t("ai_assistant"), t("points_mall"), t("multi_track"),
                              t("smart_matting"), t("material_library"), t("video_sites"), t("movie_search"), t("about")]
        
        professional_mode = st.checkbox(t("pro_mode"), value=False)
        
        if professional_mode:
            function = st.selectbox(t("quick_functions"), core_functions + advanced_functions)
        else:
            function = st.selectbox(t("quick_functions"), core_functions)
            with st.expander(t("pro_tools")):
                for adv in advanced_functions:
                    if st.button(adv, key=f"adv_{adv}", use_container_width=True):
                        st.session_state.current_function = adv
                        st.rerun()
        
        if 'current_function' in st.session_state:
            function = st.session_state.current_function
            del st.session_state.current_function
    
    # 主界面
    st.title(f"{APP_NAME} v{VERSION}")
    st.caption(COPYRIGHT)
    
    # 文件上传区域
    uploaded_file = st.file_uploader("上传视频", type=["mp4", "mov", "avi"])
    if uploaded_file:
        video_path = save_uploaded_file(uploaded_file)
        st.session_state.video_path = video_path
        info = get_video_info(video_path)
        if info:
            st.success(f"上传成功！时长: {info['duration']:.1f}秒，尺寸: {info['width']}x{info['height']}")
    
    # 功能处理
    if function == t("cut"):
        st.subheader(t("cut"))
        if st.session_state.get('video_path'):
            duration = get_video_info(st.session_state.video_path)["duration"]
            start = st.number_input("开始时间(秒)", 0.0, duration, 0.0)
            end = st.number_input("结束时间(秒)", 0.0, duration, min(5.0, duration))
            if st.button("开始剪切"):
                out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                with st.spinner("剪切中..."):
                    cut_video_ffmpeg(st.session_state.video_path, start, end, out)
                st.success("完成！")
                with open(out, "rb") as f:
                    st.download_button(t("download"), f, file_name="cut.mp4")
                cleanup_temp_files([out])
        else:
            st.info(t("upload_first"))
    
    elif function == t("speed"):
        st.subheader(t("speed"))
        if st.session_state.get('video_path'):
            speed = st.number_input("速度倍数", 0.1, 5.0, 1.0, step=0.1)
            if st.button("应用变速"):
                out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                with st.spinner("处理中..."):
                    change_speed_ffmpeg(st.session_state.video_path, speed, out)
                st.success("完成！")
                with open(out, "rb") as f:
                    st.download_button(t("download"), f, file_name="speed.mp4")
                cleanup_temp_files([out])
        else:
            st.info(t("upload_first"))
    
    elif function == t("smart_matting"):
        render_smart_matting()
    
     否则如果函数=="材料_库"( 否则如果):
        渲染_材质_库()
    
     否则如果函数==t("视频网站"):
渲染视频网站()渲染_视频_网站()
    
     否则如果 function == t("电影_搜索"):
        渲染_电影_搜索()
    
     否则如果 function == t(“关于”):
        渲染_关于()
    
否则如果函数==t(“艾_助手"):
街道副标题(t(“艾_助手"))
街道信息(“艾助手功能开发中,敬请期待")
    
     否则如果 function == t("积分_商城"):
街道副标题(t(“积分_商城"))
点数=获取积分(圣。会话状态。用户名)
街道写(f "当前积分:{points} ")
街道信息("积分商城开发中,敬请期待")
    
    其他:
ST . info(f " { t(' current _ function ')}:{ function }，{t('upload_first')} ")
    
    # 清理临时文件按钮
使用圣侧边栏:
圣马克道(“-”)
如果st.button("🧹清理临时文件"):
cleaned = cleanup_all_temp()
cleaned = cleanup_all_temp()


if __name__ == "__main__ ":
主(主要的
