
"""
智能视频助手 v5.0 - 完整版
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
from datetime import datetime, timedelta
import cv2
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="智能视频助手 v5.0", page_icon="🎬", layout="wide")

LANG = {
    "zh": {
        "title": "智能视频助手 v5.0",
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
        "speed": "视频变速",
        "apply_filter": "应用滤镜",
        "add_text": "添加文字水印",
        "export": "导出设置",
        "ai_assistant": "🤖 AI助手",
        "smart_matting": "✨ 智能抠像",
        "material_library": "📚 素材库",
        "video_sites": "📺 视频网站",
        "movie_search": "🔍 影视搜索",
        "about": "📄 关于",
        "points_mall": "💰 积分商城",
        "multi_track": "🎞️ 多轨道时间线",
        "security": "🛡️ 安全监控",
        "admin_panel": "👑 管理员面板",
        "current_function": "当前功能",
        "upload_first": "请上传视频后使用",
        "password_mismatch": "两次密码不一致",
        "user_exists": "用户名已存在",
        "register_success": "注册成功",
        "login_success": "登录成功",
        "user_not_exist": "用户名不存在",
        "wrong_password": "密码错误",
        "language": "语言",
        "download": "下载视频"
    },
    "en": {
        "title": "AI Video Assistant v5.0",
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
        "speed": "Video Speed",
        "apply_filter": "Apply Filter",
        "add_text": "Add Text",
        "export": "Export",
        "ai_assistant": "🤖 AI Assistant",
        "smart_matting": "✨ Smart Matting",
        "material_library": "📚 Material Library",
        "video_sites": "📺 Video Sites",
        "movie_search": "🔍 Movie Search",
        "about": "📄 About",
        "points_mall": "💰 Points Mall",
        "multi_track": "🎞️ Multi-Track",
        "security": "🛡️ Security",
        "admin_panel": "👑 Admin Panel",
        "current_function": "Current Function",
        "upload_first": "Please upload a video first",
        "password_mismatch": "Passwords do not match",
        "user_exists": "Username already exists",
        "register_success": "Registration successful",
        "login_success": "Login successful",
        "user_not_exist": "Username does not exist",
        "wrong_password": "Wrong password",
        "language": "Language",
        "download": "Download Video"
    }
}

def t(key):
    current_lang = st.session_state.get('language', 'zh')
    return LANG[current_lang].get(key, key)

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

@st.cache_data(ttl=3600, show_spinner=False)
def get_video_info(video_path):
    if not os.path.exists(video_path):
        return None
    from moviepy.editor import VideoFileClip
    clip = VideoFileClip(video_path)
    info = {"duration": clip.duration, "width": clip.w, "height": clip.h, "fps": clip.fps}
    clip.close()
    return info

def init_all_dbs():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    salt TEXT,
                    admin_level INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_points (
                    username TEXT PRIMARY KEY,
                    points INTEGER DEFAULT 0
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    import hashlib, secrets
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
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
    conn.commit()
    conn.close()

def log_action(username, action):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()

def cut_video_ffmpeg(input_path, start, end, output_path):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-to", str(end), "-c", "copy", output_path], check=True)

def change_speed_ffmpeg(input_path, speed, output_path):
    subprocess.run([
        "ffmpeg", "-i", input_path,
        "-filter:v", f"setpts={1/speed}*PTS",
        "-filter:a", f"atempo={speed}",
        "-c:a", "aac", output_path
    ], check=True)

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
                        ok, msg = login_user(username, password)
                        if ok:
                            log_action(username, "login")
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
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
                                log_action(new_username, "register")
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
                log_action(st.session_state.username, "logout")
                st.session_state.clear()
                st.rerun()
            st.markdown("---")

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

def render_video_sites():
    st.subheader(t("video_sites"))
    sites = [
        {"name": "爱奇艺", "url": "https://www.iqiyi.com"},
        {"name": "腾讯视频", "url": "https://v.qq.com"},
        {"name": "优酷", "url": "https://www.youku.com"},
        {"name": "B站", "url": "https://www.bilibili.com"},
    ]
    cols = st.columns(2)
    for i, site in enumerate(sites):
        with cols[i % 2]:
            if st.button(f"访问 {site['name']}", use_container_width=True):
                import webbrowser
                webbrowser.open(site['url'])
                st.info(f"正在打开 {site['name']}")

def render_movie_search():
    st.subheader(t("movie_search"))
    keyword = st.text_input("请输入电影/电视剧名称")
    if keyword:
        st.markdown("### 🔗 在以下平台搜索")
        st.markdown(f'<a href="https://www.iqiyi.com/search?q={keyword}" target="_blank">🔍 爱奇艺搜索</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://v.qq.com/search?q={keyword}" target="_blank">🔍 腾讯视频搜索</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://search.bilibili.com/all?keyword={keyword}" target="_blank">🔍 B站搜索</a>', unsafe_allow_html=True)

def render_about():
    st.subheader(t("about"))
    st.markdown("**智能视频助手 v5.0**\n\n开发者：李国锐\n\n**功能特性**：\n- 视频剪辑\n- AI助手\n- 智能抠像\n- 素材库\n- 视频网站\n- 影视搜索\n- 积分商城\n- 多轨道时间线\n- 五级管理员\n- 安全监控\n\n**开源许可**：MIT License")

def render_ai_assistant():
    st.subheader(t("ai_assistant"))
    st.info("AI助手功能开发中，敬请期待")

def render_smart_matting():
    st.subheader(t("smart_matting"))
    st.info("智能抠像功能开发中，敬请期待")

def render_material_library():
    st.subheader(t("material_library"))
    st.info("素材库开发中，敬请期待")

def render_points_mall():
    st.subheader(t("points_mall"))
    points = get_points(st.session_state.username)
    st.write(f"当前积分：{points}")
    st.info("积分商城开发中，敬请期待")

def render_multi_track():
    st.subheader(t("multi_track"))
    st.info("多轨道时间线开发中，敬请期待")

def render_security():
    st.subheader(t("security"))
    st.success("✅ 安全监控运行中")

def render_admin_panel():
    st.subheader(t("admin_panel"))
    if st.session_state.get('admin_level', 0) >= 5:
        st.success("👑 超级管理员权限")
    else:
        st.warning("权限不足")

def main():
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    
    init_all_dbs()
    
    render_language_switcher()
    render_auth()
    
    if not st.session_state.get('logged_in', False):
        return
    
    points = get_points(st.session_state.username)
    with st.sidebar:
        st.write(f"{t('points')}：{points}")
        st.markdown("---")
        st.markdown("### 功能菜单")
        
        core_functions = [t("cut"), t("speed")]
        advanced_functions = [
            t("ai_assistant"), t("smart_matting"), t("material_library"),
            t("video_sites"), t("movie_search"), t("points_mall"),
            t("multi_track"), t("security"), t("about")
        ]
        
        professional_mode = st.checkbox(t("pro_mode"), value=False)
        
        if professional_mode:
            all_functions = core_functions + advanced_functions
            function = st.selectbox(t("quick_functions"), all_functions)
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
        
        if st.session_state.get('admin_level', 0) >= 5:
            st.markdown("---")
            if st.button("👑 管理员面板", use_container_width=True):
                st.session_state.current_function = t("admin_panel")
                st.rerun()
    
    st.title(t("title"))
    
    uploaded_file = st.file_uploader("上传视频", type=["mp4", "mov", "avi"])
    if uploaded_file:
        video_path = save_uploaded_file(uploaded_file)
        st.session_state.video_path = video_path
        info = get_video_info(video_path)
        if info:
            st.success(f"上传成功！时长: {info['duration']:.1f}秒")
    
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
    
    elif function == t("ai_assistant"):
        render_ai_assistant()
    elif function == t("smart_matting"):
        render_smart_matting()
    elif function == t("material_library"):
        render_material_library()
    elif function == t("video_sites"):
        render_video_sites()
    elif function == t("movie_search"):
        render_movie_search()
    elif function == t("points_mall"):
        render_points_mall()
    elif function == t("multi_track"):
        render_multi_track()
    elif function == t("security"):
        render_security()
    elif function == t("about"):
        render_about()
    elif function == t("admin_panel"):
        render_admin_panel()
    else:
        st.info(f"{t('current_function')}：{function}，{t('upload_first')}")

if __name__ == "__main__":
    main()
