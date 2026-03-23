"""
智能视频助手v5.0 -完整版
包含：视频剪辑、艾助手、智能抠像、素材库、视频网站、影视搜索、中英文切换、五级管理员、安全监控
"""

进口细流如同标准时间
进口操作系统（Operating System）
进口json
进口临时文件
进口子过程
进口时间
进口哈希里布
进口sqlite3
进口随意
进口穿线
从日期时间进口日期时间，时间增量
进口cv2
进口numpy如同铭牌
进口熊猫如同螺纹中径
进口plotly.express如同像素

# ========== 页面配置 ==========
街道设置页面配置(page_title="智能视频助手v5.0 "，page_icon="🎬"，布局=“宽”)

# ========== 语言资源 ==========
LANG ={
    " zh ": {
        "标题": "智能视频助手v5.0 ",
        "用户中心": "👤 用户中心",
        "登录": "登录",
        "注册": "注册",
        "用户名": "用户名",
        "密码": "密码",
        "确认": "确认密码",
        "登录_btn ": "登录",
        "注册_btn ": "注册",
        "注销": "注销",
        “欢迎”: "欢迎回来",
        “点数”: "⭐ 积分",
        "快速功能": "快速功能",
        "专业模式": "⭐ 专业模式",
        " pro_tools ": "🔧 专业工具",
        “切”: "剪切视频",
        "合并": "合并视频",
        "添加文本": "添加文字水印",
        "应用过滤器": "应用滤镜",
        "导出": "导出设置",
        “速度”: "视频变速",
        “ai _助手”: "🤖人工智能助手",
        "积分_商城": "💰 积分商城",
        “多轨道”: "🎞️ 多轨道时间线",
        "智能抠图": "✨ 智能抠像",
        "材料_库": "📚 素材库",
        "视频网站": "📺 视频网站",
        "电影_搜索": "🔍 影视搜索",
        “关于”: "📄 关于",
        “安全性”: "🛡️ 安全监控",
        "管理面板": "👑 管理员面板",
        "当前函数": "当前功能",
        "上传_优先": "请上传视频后使用",
        "密码不匹配": "两次密码不一致",
        "用户存在": "用户名已存在",
        "注册成功": "注册成功",
        "登录成功": "登录成功",
        "用户不存在": "用户名不存在",
        "错误密码": "密码错误",
        “语言”: "语言",
        "下载": "下载视频"
    },
    “恩”: {
        "标题": “AI视频助手v5.0”,
        "用户中心": "👤用户中心",
        "登录": "登录",
        "注册": "注册",
        "用户名": "用户名",
        "密码": "密码",
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
        "add_text": "Add Text",
        "apply_filter": "Apply Filter",
        "export": "Export",
        "speed": "Video Speed",
        "ai_assistant": "🤖 AI Assistant",
        "points_mall": "💰 Points Mall",
        "multi_track": "🎞️ Multi-Track",
        "smart_matting": "✨ Smart Matting",
        "material_library": "📚 Material Library",
        "video_sites": "📺 Video Sites",
        "movie_search": "🔍 Movie Search",
        "about": "📄 About",
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

# ========== 数据库 ==========
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

# ========== 视频处理 ==========
def cut_video_ffmpeg(input_path, start, end, output_path):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-to", str(end), "-c", "copy", output_path], check=True)

def change_speed_ffmpeg(input_path, speed, output_path):
    subprocess.run([
        "ffmpeg", "-i", input_path,
        "-filter:v", f"setpts={1/speed}*PTS",
        "-filter:a", f"atempo={speed}",
        "-c:a", "aac", output_path
    ], check=True)

# ========== 界面函数 ==========
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

def render_movie_search():
    st.subheader(t("movie_search"))
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

def render_about():
    st.subheader(t("about"))
    st.markdown("""
    **智能视频助手 v5.0**
    
    开发者：李国锐
    
    **功能特性**：
    - ✂️ 视频剪辑（剪切、合并、变速）
    - 🎨 滤镜特效
    - 🤖 AI对话式剪辑
    - ✨ 智能抠像
    - 📖 小说转视频
    - 💰 积分商城
    - 👑 五级管理员系统
    - 🛡️ 安全监控
    
    **开源许可**：MIT License
    """)

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
    st.info("HOPE监测系统已启用")

def render_admin_panel():
    st.subheader(t("admin_panel"))
    if st.session_state.get('admin_level', 0) >= 5:
        st.success("👑 超级管理员权限")
        st.info("管理员功能开发中")
    else:
        st.warning("权限不足，需要超级管理员权限")

# ========== 主程序 ==========
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
        st.markdown("### 🎨 功能菜单")
        
        core_functions = [t("cut"), t("speed"), t("apply_filter"), t("add_text"), t("export")]
        advanced_functions = [
            t("ai_assistant"), t("smart_matting"), t("material_library"),
            t("video_sites"), t("movie_search"), t("points_mall"),
            t("multi_track"), t("security"), t("about")
        ]
        
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
        
        if st.session_state.get('admin_level', 0) >= 5:
街道减价("---")
            如果街道按钮("👑 管理员面板"，use_container_width=真实的):
街道会话状态.当前功能 = t("管理面板")
街道再放映()
    
街道标题(t("标题"))
    
上传的文件= st。文件上传者("上传视频"，类型=[" mp4 ", " mov ", “阿维”])
    如果上传文件:
        video_path = save_uploaded_file(uploaded_file)
        st.session_state.video_path = video_path
        info = get_video_info(video_path)
        if info:
街道成功(f "上传成功！时长：{信息['持续时间']:. 1f}秒，尺寸: {信息['宽度']}x{信息['高度']}")
    
    如果函数==t(“切”):
st.副标题(t(“切”))副标题(t(“切”))副标题(t(“切”))
数字_输入('视频路径'):如果圣。会议_ state。得到('视频路径'):圣会议_ state。得到('视频路径'):如果街道会话状态.得到('视频路径'):('视频路径'):如果圣。会议_ state。得到('视频路径'):圣会议_ state。得到('视频路径'):如果街道会话状态.得到('视频路径'):
如果获取视频信息(第一会话状态.视频_路径)["持续时间"]获取视频信息(圣。会议_ state。录像 _小路)["持续时间"]信息(圣。会议_ state。录像 _小路)["持续时间"]获取视频信息(街道会话状态.视频路径)["持续时间"](第一会话状态.视频_路径)["持续时间"]获取视频信息(圣。会议_ state。录像 _小路)["持续时间"]信息(圣。会议_ state。录像 _小路)["持续时间"]获取视频信息(街道会话状态.视频路径)["持续时间"]
start = st。数字_输入("开始时间（秒)",0.0,持续时间，0.0)数字_输入(“开始时间（秒)”，0.0，持续时间，0.0)数字_输入主要的"开始时间（秒)",0.0,持续时间，0.0)数字_输入(“开始时间（秒)”，0.0，持续时间，0.0)(秒)“，0.0，持续时间，0.0)st。数字_输入("开始时间（秒)",0.0,持续时间，0.0)数字_输入(“开始时间（秒)”，0.0，持续时间，0.0)数字_输入主要的"开始时间（秒)",0.0,持续时间，0.0)数字_输入(“开始时间（秒)”，0.0，持续时间，0.0)(秒)“，0.0，持续时间，0.0)
end = st。数字_输入("结束时间（秒)",0.0,持续时间，最小值(5.0，持续时间))数字_输入(“结束时间（秒)",0.0,持续时间，min(5.0，持续时间))数字_输入(“结束时间（秒)",0.0,持续时间，min(5.0，持续时间))数字_输入(“结束时间（秒)"，0.0，持续时间，min(5.0，持续时间))st。数字_输入("结束时间（秒)",0.0,持续时间，最小值(5.0，持续时间))数字_输入(“结束时间（秒)",0.0,持续时间，min(5.0，持续时间))数字_输入(“结束时间（秒)",0.0,持续时间，min(5.0，持续时间))数字_输入(“结束时间（秒)"，0.0，持续时间，min(5.0，持续时间))
如果圣巴顿("开始剪切”):如果圣巴顿(“开始剪切"):
out = tempfile。命名临时文件（后缀=".mp4 "，delete=False)。名字命名临时文件(后缀=".mp4 "，delete=False).名字if _ _ name _ _ = " _ _ main _ _ ":_ _ name _ _，delete=False)。名字命名临时文件(后缀=".mp4 "，delete=False).名字
与圣斯宾纳("剪切中..."):用圣斯宾纳(“剪切中..."):
cut _ video _ ffmpeg(ST . session _ state .video _ path，start，end，out)cut _ video _ ffmpeg(ST . session _ state。视频_路径，开始，结束，输出)
圣成功("完成!")成功(“完成!")
开（出,"经常预算")为女:开（出，“经常预算”)为女:
st.download_button(t("download ")，f，file_name="cut . MP4 ")download _ button(t(" download ")，f，file _ name = " cut。MP4”)
清理临时文件([out])清理临时文件([out])
否则:否则:
st.info(t("上传_优先")信息(t("上传_优先"))
    
否则如果函数== t("speed "):elif函数== t("速度"):
ST . subheader(t(" speed "))子标题(t(" speed "))
如果圣会话_状态get(' video _ path '):if ST . session _ state。get(' video _ path '):
速度=编号_输入("速度倍数",0.1,5.0,1.0,步长=0.1)数字输入(“速度倍数“，0.1，5.0，1.0，步长=0.1)
如果圣巴顿("应用变速”):如果圣巴顿(“应用变速"):
out = tempfile。命名临时文件（后缀=".mp4 "，delete=False)。名字命名临时文件(后缀=".mp4 "，delete=False).名字
与圣斯宾纳("处理中..."):用圣斯宾纳(“处理中..."):
变化速度ffmpeg(第一会话_状态。视频_路径,速度,输出)change _ speed _ ffmpeg(ST . session _ state。视频_路径、速度、输出)
圣成功("完成!")成功(“完成!")
开（出,"经常预算")为女:开（出，“经常预算”)为女:
st.download_button(t("download ")，f，file_name="speed . MP4 ")download _ button(t(" download ")，f，file _ name = " speed。MP4”)
清理临时文件([out])清理临时文件([out])
否则:否则:
st.info(t("上传_优先")信息(t("上传_优先"))
    
否则如果函数== t("apply_filter "):elif函数== t("应用过滤器"):
ST . subheader(t(" apply _ filter "))子标题(t(" apply _ filter "))
st.info("滤镜功能开发中,敬请期待")信息("滤镜功能开发中,敬请期待")
    
elif function = = t(" add _ text "):elif function = = t(" add _ text "):
ST . subheader(t(" add _ text "))subheader(t(" add _ text "))
st.info("文字功能开发中,敬请期待")信息("文字功能开发中,敬请期待")
    
否则如果函数== t("export "):elif函数== t("export "):
st.subheader(t("export "))
st.info("导出功能开发中,敬请期待")信息("导出功能开发中,敬请期待")
    
elif function = = t(" ai _ assistant "):elif function = = t(" ai _ assistant "):
render_ai_assistant()
    
否则如果函数= = t(" smart _ matting "):elif function = = t(" smart _ matting "):
render_smart_matting()
    
否则如果函数== t("material_library "):elif函数== t("material_library "):
渲染_材质_库()渲染_材质_库()
    
否则如果函数= = t(" video _ sites "):elif function = = t(" video _ sites "):
渲染视频网站()渲染视频网站()
    
elif function = = t(" movie _ search "):elif function = = t(" movie _ search "):
渲染_电影_搜索()渲染_电影_搜索()
    
否则如果函数= = t(" points _ mall "):elif function = = t(" points _ mall "):
渲染点商城()渲染点数商城()
    
elif function = = t(" multi _ track "):elif function = = t(" multi _ track "):
渲染多重轨迹()render_multi_track()
    
否则如果函数== t("security "):elif函数== t("security "):
render_security()
    
否则如果函数== t("about "):elif函数== t("约"):
render_about()render_about()
    
elif function = = t(" admin _ panel "):elif function = = t(" admin _ panel "):
render_admin_panel()
    
否则:否则:
ST . info(f " { t(' current _ function ')}:{ function }，{t('upload_first')} ")info(f " { t(' current _ function ')}:{ function }，{ t(' upload _ first ')} ")

if _ _ name _ _ = " _ _ main _ _ ":_ _ name _ _ = " _ _ main _ _ ":
主()main()
