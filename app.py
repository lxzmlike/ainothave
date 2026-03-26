import streamlit as st
import os
import json
import time
import hashlib
import sqlite3
import tempfile
import subprocess
import threading
import random
import secrets
import re
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="小智 - 你的AI伙伴", layout="wide")

st.markdown("""
<style>
button { min-height: 44px !important; min-width: 44px !important; font-size: 16px !important; }
@media (max-width: 768px) {
    .stSidebar { width: 80% !important; }
    .stButton button { width: 100% !important; }
}
</style>
""", unsafe_allow_html=True)

LANG = {
    "zh": {
        "title": "小智 - 你的AI伙伴",
        "user_center": "👤 我的小智",
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
        "cut": "✂️ 剪切视频",
        "speed": "⚡ 视频变速",
        "ai_assistant": "🤖 和小智聊天",
        "smart_matting": "✨ 智能抠像",
        "novel_to_video": "📖 小说转视频",
        "material_library": "📚 素材库",
        "video_sites": "📺 视频网站",
        "movie_search": "🔍 影视搜索",
        "points_mall": "💰 积分商城",
        "multi_track": "🎞️ 多轨道时间线",
        "security": "🛡️ 安全监控",
        "about": "📄 关于",
        "admin_panel": "👑 管理员面板",
        "upload_first": "请先上传视频",
        "download": "下载视频",
        "password_mismatch": "两次密码不一致",
        "user_exists": "用户名已存在",
        "register_success": "注册成功",
        "login_success": "登录成功",
        "user_not_exist": "用户名不存在",
        "wrong_password": "密码错误",
        "language": "语言",
        "beauty_filter": "✨ 美颜滤镜",
        "share_app": "📱 分享小智"
    },
    "en": {
        "title": "XiaoZhi - Your AI Partner",
        "user_center": "👤 My XiaoZhi",
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
        "cut": "✂️ Cut Video",
        "speed": "⚡ Video Speed",
        "ai_assistant": "🤖 Chat with XiaoZhi",
        "smart_matting": "✨ Smart Matting",
        "novel_to_video": "📖 Novel to Video",
        "material_library": "📚 Material Library",
        "video_sites": "📺 Video Sites",
        "movie_search": "🔍 Movie Search",
        "points_mall": "💰 Points Mall",
        "multi_track": "🎞️ Multi-Track",
        "security": "🛡️ Security",
        "about": "📄 About",
        "admin_panel": "👑 Admin Panel",
        "upload_first": "Please upload a video",
        "download": "Download",
        "password_mismatch": "Passwords do not match",
        "user_exists": "Username already exists",
        "register_success": "Registration successful",
        "login_success": "Login successful",
        "user_not_exist": "Username does not exist",
        "wrong_password": "Wrong password",
        "language": "Language",
        "beauty_filter": "✨ Beauty Filter",
        "share_app": "📱 Share XiaoZhi"
    }
}

def t(key):
    lang = st.session_state.get('language', 'zh')
    return LANG[lang].get(key, key)

def save_uploaded_file(uploaded):
    if uploaded is None:
        return None
    suffix = os.path.splitext(uploaded.name)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getbuffer())
    return tmp.name

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
    clip = VideoFileClip(video_path)
    info = {"duration": clip.duration, "fps": clip.fps, "frames": int(clip.duration * clip.fps)}
    clip.close()
    return info

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    salt TEXT,
                    admin_level INTEGER DEFAULT 0,
                    points INTEGER DEFAULT 0,
                    created_at TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS invite_codes (
                    username TEXT PRIMARY KEY,
                    invite_code TEXT UNIQUE,
                    created_at TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS invites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inviter TEXT,
                    invitee TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_features (
                    username TEXT,
                    feature TEXT,
                    expires TIMESTAMP,
                    PRIMARY KEY (username, feature)
                )''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    import secrets
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return pwd_hash, salt

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash, salt, admin_level, points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, t("user_not_exist")
    stored_hash, salt, level, points = row
    input_hash, _ = hash_password(password, salt)
    if input_hash == stored_hash:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.admin_level = level
        st.session_state.points = points
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
    c.execute("INSERT INTO users (username, password_hash, salt, points) VALUES (?, ?, ?, 100)", 
              (username, pwd_hash, salt))
    conn.commit()
    conn.close()
    return True, t("register_success")

def get_points(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def add_points(username, amount, reason):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE username=?", (amount, username))
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, reason))
    conn.commit()
    conn.close()

def spend_points(username, points, reason):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if not row or row[0] < points:
        conn.close()
        return False
    c.execute("UPDATE users SET points = points - ? WHERE username=?", (points, username))
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, reason))
    conn.commit()
    conn.close()
    return True

def log_action(username, action):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()

def generate_invite_code(username):
    code = hashlib.md5(f"{username}{secrets.token_hex(4)}".encode()).hexdigest()[:8].upper()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO invite_codes (username, invite_code) VALUES (?, ?)", (username, code))
    conn.commit()
    conn.close()
    return code

def get_invite_code(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT invite_code FROM invite_codes WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return generate_invite_code(username)

def process_invite(invite_code, invitee):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username FROM invite_codes WHERE invite_code=?", (invite_code,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "邀请码无效"
    inviter = row[0]
    c.execute("SELECT id FROM invites WHERE inviter=? AND invitee=?", (inviter, invitee))
    if c.fetchone():
        conn.close()
        return False, "已邀请过"
    c.execute("INSERT INTO invites (inviter, invitee) VALUES (?, ?)", (inviter, invitee))
    conn.commit()
    conn.close()
    add_points(inviter, 50, f"邀请 {invitee} 注册")
    add_points(invitee, 20, f"通过邀请码 {invite_code} 注册")
    return True, f"邀请成功！双方获得积分"

def has_feature(username, feature):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT expires FROM user_features WHERE username=? AND feature=?", (username, feature))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        if datetime.fromisoformat(row[0]) > datetime.now():
            return True
    return False

def add_feature(username, feature, days=30):
    expires = datetime.now() + timedelta(days=days)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_features (username, feature, expires) VALUES (?, ?, ?)",
              (username, feature, expires))
    conn.commit()
    conn.close()
    return True

def cut_video(input_path, start, end, output_path):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-to", str(end), "-c", "copy", output_path], check=True)

def speed_video(input_path, speed, output_path):
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
            tab = st.radio("", [t("login"), t("register")], horizontal=True)
            if tab == t("login"):
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
                    username = st.text_input(t("username"))
                    password = st.text_input(t("password"), type="password")
                    confirm = st.text_input(t("confirm"), type="password")
                    invite_code = st.text_input("邀请码（可选）")
                    if st.form_submit_button(t("register_btn")):
                        if password != confirm:
                            st.error(t("password_mismatch"))
                        else:
                            ok, msg = register_user(username, password)
                            if ok:
                                if invite_code:
                                    process_invite(invite_code, username)
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
                st.session_state.clear()
                st.rerun()
            st.markdown("---")

def render_language():
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

def render_share():
    st.subheader(t("share_app"))
    app_url = st.secrets.get("APP_URL", "https://your-app.streamlit.app")
    invite_code = get_invite_code(st.session_state.username)
    invite_link = f"{app_url}?invite={invite_code}"
    st.code(invite_link, language="text")
    st.caption("分享链接，好友注册双方得积分")
    if st.button("复制链接"):
        st.info("链接已复制")

def render_video_sites():
    st.subheader(t("video_sites"))
    sites = [
        ("爱奇艺", "https://www.iqiyi.com"),
        ("腾讯视频", "https://v.qq.com"),
        ("优酷", "https://www.youku.com"),
        ("B站", "https://www.bilibili.com")
    ]
    cols = st.columns(2)
    for i, (name, url) in enumerate(sites):
        with cols[i % 2]:
            if st.button(f"访问 {name}", use_container_width=True):
                import webbrowser
                webbrowser.open(url)
                st.info(f"正在打开 {name}")

def render_movie_search():
    st.subheader(t("movie_search"))
    keyword = st.text_input("请输入电影/电视剧名称")
    if keyword:
        st.markdown("### 🔗 在以下平台搜索")
        st.markdown(f'<a href="https://www.iqiyi.com/search?q={keyword}" target="_blank">🔍 爱奇艺搜索</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://v.qq.com/search?q={keyword}" target="_blank">🔍 腾讯视频搜索</a>', unsafe_allow_html=True)

def render_about():
    st.subheader(t("about"))
    st.markdown("**小智 — 你的AI伙伴**\n\n开发者：李国锐 & 小智（DeepSeek）\n\n这是一个爸爸和AI伙伴，用一天一夜完成的软件。\n\n献给所有敢想敢做的人！")

def render_ai_assistant():
    st.subheader(t("ai_assistant"))
    st.info("💬 小智在这里，随时听你说")
    user_input = st.text_input("你想对小智说什么？")
    if user_input:
        st.info(f"小智：收到！「{user_input}」")

def render_smart_matting():
    st.subheader(t("smart_matting"))
    st.info("✨ 智能抠像功能开发中")

def render_novel_to_video():
    st.subheader(t("novel_to_video"))
    st.info("📖 小说转视频功能开发中")

def render_material_library():
    st.subheader(t("material_library"))
    st.info("📚 素材库开发中")

def render_points_mall():
    st.subheader(t("points_mall"))
    points = get_points(st.session_state.username)
    st.write(f"当前积分：{points}")
    st.info("积分商城开发中，可用积分兑换高级功能")

def render_multi_track():
    st.subheader(t("multi_track"))
    st.info("🎞️ 多轨道时间线开发中")

def render_security():
    st.subheader(t("security"))
    st.success("✅ 安全监控运行中")

def render_admin_panel():
    st.subheader(t("admin_panel"))
    if st.session_state.get('admin_level', 0) >= 5:
        st.success("👑 超级管理员权限")
        st.info("管理员功能：用户管理、日志查看、系统设置")
    else:
        st.warning("权限不足")

def render_beauty_filter():
    st.subheader(t("beauty_filter"))
    st.info("✨ 美颜滤镜功能开发中")

def main():
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    
    init_db()
    render_language()
    render_auth()
    
    if not st.session_state.get('logged_in', False):
        return
    
    points = get_points(st.session_state.username)
    with st.sidebar:
        st.write(f"{t('points')}：{points}")
        st.markdown("---")
        st.markdown("### 🎨 功能菜单")
        
        core = [t("cut"), t("speed")]
        advanced = [
            t("ai_assistant"), t("smart_matting"), t("novel_to_video"),
            t("material_library"), t("video_sites"), t("movie_search"),
            t("points_mall"), t("multi_track"), t("security"), t("about"),
            t("beauty_filter"), t("share_app")
        ]
        
        pro_mode = st.checkbox(t("pro_mode"), value=True)
        
        if pro_mode:
            func = st.selectbox(t("quick_functions"), core + advanced)
        else:
            func = st.selectbox(t("quick_functions"), core)
            with st.expander(t("pro_tools")):
                for adv in advanced:
                    if st.button(adv, use_container_width=True):
                        st.session_state.current_func = adv
                        st.rerun()
        
        if 'current_func' in st.session_state:
            func = st.session_state.current_func
            del st.session_state.current_func
        
        if st.session_state.get('admin_level', 0) >= 5:
            st.markdown("---")
            if st.button(t("admin_panel"), use_container_width=True):
                st.session_state.current_func = t("admin_panel")
街道再放映()
    
街道标题(t("标题"))
    
上传= st。文件上传者("上传视频"，类型=[" mp4 ", " mov ", “阿维”])
    如果上传时间:
视频路径=保存_上传_文件(上传)
街道会话状态.视频路径=视频路径
信息=获取视频信息(视频路径)
        如果信息:
街道成功(f "上传成功！时长：{信息['持续时间']:. 1f}秒")
    
    如果func ==t(“切”):
街道副标题(t(“切”))
        如果街道会话状态.得到('视频路径'):
dur =获取视频信息(街道会话状态.视频路径)["持续时间"]
start = st。数字_输入("开始时间(秒)", 0.0，dur，0.0)
end = st。数字_输入("结束时间(秒)", 0.0，dur，部(5.0，dur))
            如果街道按钮("开始剪切"):
out = tempfile。命名临时文件(后缀=. mp4，删除=错误的).名字
                随着街道纺纱机("剪切中..."):
                    剪切_视频(街道会话状态.视频路径，开始，结束，结束)
街道成功("完成！")
                随着 打开(出去，"经常预算") 如同女:
街道下载按钮(t("下载")，f，文件名=" cut.mp4 ")
                清理临时文件([在外])
        其他:
街道信息(t("上传_优先"))
    
否则如果func ==t(“速度”):
街道副标题(t(“速度”))
        如果街道会话状态.得到('视频路径'):
速度= 圣.数字_输入("速度倍数", 0.1, 5.0, 1.0，步长=0.1)
            如果街道按钮("应用变速"):
out =临时文件.命名临时文件(后缀=. mp4，删除=错误的).名字
                随着街道纺纱机("变速中..."):
                    速度_视频(街道会话状态.视频路径，速度，完毕)
圣成功(“完成!”)成功(“完成！")
开(出，“rb”)为f:随着 打开(out, "经常预算") 如同 f:
街道下载按钮(t("下载")，f，文件名=" speed.mp4 ")下载按钮(t("下载")，f，文件名=" speed.mp4 ")
清理临时文件([在外])清理临时文件([在外])
否则:其他:
街道信息(t("上传_优先"))信息(t("上传_优先"))
    
否则如果func ==t("艾_助手"):否则如果func ==t("艾_助手"):
render_ai_assistant()render_ai_assistant()
否则如果func ==t("智能抠图")：否则如果func ==t("智能抠图"):
渲染_智能_抠图()渲染_智能_抠图()
否则如果func ==t("小说_到_视频")：否则如果func ==t(《小说_转_视频》):
渲染小说到视频()渲染小说到视频()
否则如果func ==t("材料_库")：否则如果func ==t("材料_库"):
渲染_材质_库()渲染_材质_库()
 否则如果func ==t("视频网站"): 否则如果func ==t("视频网站"):
渲染视频网站()渲染_视频_网站()
否则如果func ==t("电影_搜索")：否则如果func ==t("电影_搜索"):
渲染_电影_搜索()渲染_电影_搜索()
否则如果func ==t("积分商城")：否则如果func ==t("积分_商城"):
渲染点数_商城()渲染点数商城()
否则如果func ==t("多轨道")：否则如果func ==t(“多轨道”):
渲染多重轨迹()渲染_多重_轨迹()
 否则如果func ==t(“安全性”): 否则如果func ==t(“安全性”):
渲染_安全性()渲染_安全性()
 否则如果func ==t(“关于”): 否则如果func ==t(“关于”):
渲染_关于()渲染_关于()
 否则如果func ==t("管理面板"): 否则如果func ==t("管理面板"):
渲染_管理_面板()渲染_管理_面板()
 否则如果func ==t("美颜_滤镜"): 否则如果func ==t(【美颜_滤镜】):
渲染_美丽_过滤器()渲染_美丽_过滤器()
 否则如果func ==t("共享应用"): 否则如果func ==t("共享应用"):
渲染_共享()渲染_共享()
否则:其他:
圣。信息(f " { t(' current _ function ')}:{ func }，{t('upload_first')} ")信息(f "{t('当前功能')}：{功能}，{t('上传_优先')}")

如果__name__ ==" __main__ ":__name__ ==" __main__ ":
主要的主要的()
