"""
智能视频助手 v5.0 - 完整版
包含：视频剪辑、AI助手、智能抠像、素材库、视频网站、影视搜索、中英文切换、五级管理员、安全监控
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
C=连接光标()
c。执行("SELECT username FROM users WHERE username=?", (username,))
    如果 c.fetchone():
        conn.关闭()
        return False, t("user_exists")
    pwd_hash, salt = hash_password(password)
c。执行("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, pwd_hash, salt))
Conn.犯罪()
Conn.关闭()
    return True, t("register_success")

定义 get_points(用户名):
Conn=sqlite3。连接('users.db')
C=连接光标()
c。执行("SELECT points FROM user_points WHERE username=?", (username,))
    row = c.fetchone()
Conn.关闭()
    return row[0] 如果 row 其他 0

定义 add_points(username, amount, reason):
Conn=sqlite3。连接('users.db')
C=连接光标()
c。执行("INSERT OR IGNORE INTO user_points (username, points) VALUES (?, 0)", (username,))
c。执行("UPDATE user_points SET points = points + ? WHERE username=?", (amount, username))
Conn.犯罪()
Conn.关闭()

定义 log_action(用户名，操作):
Conn=sqlite3。连接('users.db')
C=连接光标()
c。执行("INSERT INTO用户日志(用户名，操作)值(？，？)", (用户名，操作))
Conn.犯罪()
Conn.关闭()

定义cut_video_ffmpeg(输入路径、开始、结束、输出路径)：
子流程。跑(["ffmpeg"，"-i"，input_path，"-ss"，str(start)，"-to"，str(end)，"-c"，"copy"，output_path]，check=True)

Def change_speed_ffmpeg(输入路径、速度、输出路径)：
子流程.运行([
"ffmpeg"，"-i"，输入路径，
"-filter:v"，f"setpts={1/speed}*PTS"，
"-filter:a"，f"Atempo={speed}"，
"-c:a"，"aac"，输出路径
]，check=True)

Def render_auth()：
带st.sidebar：
st.header(t("user_center"))
如果不是st.session_state.get('logged_in'，False)：
auth_tab=St.radio(""，[t("登录")，t("寄存器")]，horizontal=True)
如果auth_tab==t(“登录”)：
使用st.form("login_form")：
username=st.text_input(t("username"))
password=st.text_input(t("password")，type="password")
如果st.form_submit_button(t("login_btn"))：
OK，msg=login_user(用户名，密码)
                        如果好的：
log_action(用户名，"登录”)
圣。成功(味精)
圣。重新运行()
                        其他:
圣。误差(味精)
            其他:
和……一起圣。形式("register_form")：
new_username=st.text_input(t("username"))
new_password=st.text_input(t("password")，类型="password")
confirm=st.text_input(t("confirm")，类型="password")
如果圣。表单提交按钮(t("register_btn"))：
如果new_password！=确认：
圣。误差(t("password_mismatch"))
                        其他:
OK，msg=register_user(新用户名，新密码)
                            如果好的：
log_action(新用户名(_U)，"register")
圣。成功(味精)
圣。重新运行重新运行重新运行重新运行重新运行重新运行(按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()按钮()
重新运行
)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)(味精)误差(味精)
st.markdownmarkdown"--""--"
其他：其他：
圣。成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")(f"{t('欢迎')}，{圣.会话状态(_state).用户名}")成功(f"{t('欢迎')}，{圣.会话状态(_state)。用户名}")
点数=get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)get_points(圣。会话状态(_state)。用户名)
圣。写(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")(f"{t('分数')}：{积分}")
如果st.按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销")：按钮(t("注销"))：按钮(T("注销")：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：按钮(t("注销"))：
log_action(圣。会话状态(_state)。用户名，"注销")(圣。会话状态(_state)。用户名，"注销")(圣。会话状态(_state)。用户名，"注销")(圣。会话状态(_state)。用户名，"注销")(圣。会话状态(_state)。用户名，"注销")(圣。会话状态(_state)。用户名，"注销")(圣。会话状态(_state)。用户名，"注销")(圣。会话状态(_state)。用户名，"注销")
圣。会话状态(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()(_state)。清楚的()会话状态(_state)。清楚的()
圣。重新运行()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()()重新运行()
圣。降价("--")降价(“---”)(“---”)markdown("---")(“---”)降价(“---”)(“---”)markdown("---")("--")降价(“---”)(“---”)markdown("---")(“---”)降价(“---”)(“---”)markdown("---")("--")降价(“---”)(“---”)markdown("---")(“---”)降价(“---”)(“---”)markdown("---")("--")降价(“---”)(“---”)markdown("---")(“---”)降价(“---”)(“---”)markdown("---")

Def呈现语言切换器()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：渲染语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：渲染语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：()：呈现语言切换器()：
带st.sidebar：带圣。侧边栏：侧边栏：带圣。侧边栏：侧边栏:with圣。侧边栏：侧边栏：带圣。侧边栏：sidebar：带圣。侧边栏：侧边栏：带圣。侧边栏：侧边栏:with圣。侧边栏：侧边栏：带圣。侧边栏：sidebar：带圣。侧边栏：侧边栏：带圣。侧边栏：侧边栏:with圣。侧边栏：侧边栏：带圣。侧边栏：sidebar：带圣。侧边栏：侧边栏：带圣。侧边栏：侧边栏:with圣。侧边栏：侧边栏：带圣。侧边栏：
col1，col2=st.列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)列(2)
带col1：和...一起col1：
如果st.markdown("🇨🇳 中文"，use_container_width=True)：如果st.按钮("🇨🇳 中文"，use_container_width=True)：markdown("🇨🇳 中文"，use_container_width=True)：如果st.button("🇨🇳 中文"，use_container_width=True)：圣。会话状态。语言='en'会话状态.("🇨🇳 中文"，use_container_width=True)：如果st.按钮markdown("🇨🇳 中文"，use_container_width=True)：如果st.按钮("🇨🇳 中文"，use_container_width=True)：markdown("🇨🇳 中文"，use_container_width=True)：如果st.button("🇨🇳 中文"，use_container_width=True)：圣。会话状态。语言='en'会话状态.("🇨🇳 中文"，use_container_width=True)：如果st.按钮("🇨🇳 中文"，use_container_width=True)：markdown("🇨🇳 中文"，use_container_width=True)：如果st.button("🇨🇳 中文"，use_container_width=True)：
圣。会话状态。语言='zh'会话状态.语言='zh'
st.rerun()rerun()
带col2:with col2：
如果st.button("🇬🇧 英语"，use_container_width=True)：如果st.button("🇬🇧 英语"，use_container_width=True)：
圣。会话状态。语言='en'会话状态.语言='en'
st.rerun()rerun()
st.markdownmarkdown"--""--")
