import streamlit as st
import os
import json
import tempfile
import subprocess
import time
import hashlib
import sqlite3
import random
import threading
from datetime import datetime, timedelta
from PIL import Image
import cv2
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="智能视频助手", page_icon="static/icon.svg", layout="wide")

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
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT, salt TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_admin INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_settings (username TEXT PRIMARY KEY, default_output_format TEXT DEFAULT 'mp4', default_bitrate TEXT DEFAULT '2000k', default_fontsize INTEGER DEFAULT 50, default_text_color TEXT DEFAULT '#FFFFFF', default_filter TEXT DEFAULT '无')''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_points (username TEXT PRIMARY KEY, points INTEGER DEFAULT 0)''')
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
    c.execute("SELECT password_hash, salt, is_admin FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, "用户名不存在"
    stored_hash, salt, is_admin = row
    input_hash, _ = hash_password(password, salt)
    if input_hash == stored_hash:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.is_admin = is_admin
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
    c.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, pwd_hash, salt))
    conn.commit()
    conn.close()
    return True, "注册成功"

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

def render_auth():
    with st.sidebar:
        st.header("👤 用户中心")
        if not st.session_state.get('logged_in', False):
            auth_tab = st.radio("选择操作", ["登录", "注册"], horizontal=True)
            if auth_tab == "登录":
                with st.form("login_form"):
                    username = st.text_input("用户名")
                    password = st.text_input("密码", type="password")
                    if st.form_submit_button("登录"):
                        ok, msg = login_user(username, password)
                        if ok:
                            st.success(msg)
                            st.experimental_rerun()
                        else:
                            st.error(msg)
            else:
                with st.form("register_form"):
                    new_username = st.text_input("用户名")
                    new_password = st.text_input("密码", type="password")
                    confirm = st.text_input("确认密码", type="password")
                    if st.form_submit_button("注册"):
                        if new_password != confirm:
                            st.error("两次密码不一致")
                        else:
                            ok, msg = register_user(new_username, new_password)
                            if ok:
                                st.success(msg)
                                st.experimental_rerun()
                            else:
                                st.error(msg)
            st.stop()
        else:
            st.success(f"欢迎回来，{st.session_state.username}")
            if st.button("注销"):
                st.session_state.clear()
                st.experimental_rerun()
            st.markdown("---")

def main():
    init_all_dbs()
    render_auth()
    if not st.session_state.get('logged_in', False):
        return
    points = get_points(st.session_state.username)
    with st.sidebar:
        st.write(f"⭐ 积分：{points}")
        core_functions = ["剪切视频", "合并视频", "添加文字水印", "应用滤镜", "导出设置"]
        advanced_functions = ["视频变速", "AI助手", "积分商城", "多轨道时间线"]
        professional_mode = st.checkbox("⭐ 专业模式", value=False)
        if professional_mode:
            function = st.selectbox("选择功能", core_functions + advanced_functions)
        else:
            function = st.selectbox("快速功能", core_functions)
            with st.expander("🔧 专业工具"):
                for adv in advanced_functions:
                    if st.button(adv, key=f"adv_{adv}"):
                        st.session_state.current_function = adv
                        st.experimental_rerun()
        if 'current_function' in st.session_state:
            function = st.session_state.current_function
            del st.session_state.current_function
    st.info(f"当前功能：{function}，请上传视频后使用")

if __name__ == "__main__":
    main()
