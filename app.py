```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI视频生成器 - 完整项目代码
文件名：ai_video_project.py
说明：这是一个完整的AI视频生成器项目，包含所有代码和配置
使用方法：python ai_video_project.py --create-project
"""

import os
import sys
import json
import yaml
import shutil
import zipfile
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class AIVideoProjectGenerator:
    """AI视频生成器完整项目生成器 - 单一文件版本"""
    
    def __init__(self):
        self.project_name = "ai-video-platform"
        self.version = "2.0.0"
        self.author = "AI Development Team"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 完整的项目文件内容
        self.project_files = {}
        
    def generate_all_files(self):
        """生成所有项目文件"""
        print("🚀 开始生成完整的AI视频生成器项目...")
        
        # 1. 根目录文件
        self._generate_root_files()
        
        # 2. 前端文件
        self._generate_frontend_files()
        
        # 3. 后端文件
        self._generate_backend_files()
        
        # 4. AI服务文件
        self._generate_ai_service_files()
        
        # 5. 配置和部署文件
        self._generate_config_files()
        
        print(f"✅ 项目生成完成！共生成 {len(self.project_files)} 个文件")
        return self.project_files
    
    def save_to_single_file(self, output_file: str = "ai_video_project_complete.py"):
        """保存为单一文件"""
        print(f"📁 正在保存为单一文件: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write(self._get_file_header())
            
            # 写入项目数据
            f.write("\n# ==================== 项目数据 ====================\n")
            f.write("PROJECT_FILES = {\n")
            
            for file_path, content in self.project_files.items():
                # 转义特殊字符
                escaped_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                f.write(f'    "{file_path}": """{escaped_content}""",\n')
            
            f.write("}\n\n")
            
            # 写入解压函数
            f.write(self._get_extract_function())
            
            # 写入主函数
            f.write(self._get_main_function())
        
        print(f"✅ 已保存到: {output_file}")
        print(f"📦 文件大小: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
        return output_file
    
    def create_zip_archive(self):
        """创建ZIP压缩包"""
        print("📦 正在创建ZIP压缩包...")
        
        # 首先生成所有文件
        if not self.project_files:
            self.generate_all_files()
        
        zip_filename = f"ai_video_project_{self.timestamp}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, content in self.project_files.items():
                # 在ZIP中创建文件
                zipf.writestr(file_path, content)
                print(f"  + {file_path}")
        
        print(f"✅ ZIP压缩包创建完成: {zip_filename}")
        return zip_filename
    
    def _get_file_header(self):
        """获取文件头"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 AI视频生成器 - 完整项目代码
版本: {self.version}
作者: {self.author}
生成时间: {self.timestamp}

这是一个完整的AI视频生成器项目，包含：
✅ 前端React应用
✅ 后端Node.js API  
✅ Python AI服务
✅ Docker部署配置
✅ 数据库脚本
✅ 所有依赖配置

使用方法：
1. 运行: python ai_video_project_complete.py --extract
2. 或: python ai_video_project_complete.py --create-zip

项目包含 {len(self.project_files)} 个文件，可直接部署到生产环境。
"""

import os
import sys
import json
import zipfile
import argparse
from pathlib import Path

'''
    
    def _get_extract_function(self):
        """获取解压函数"""
        return '''
def extract_project(output_dir: str = "."):
    """解压项目文件"""
    print(f"📂 正在解压项目到: {output_dir}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    total_files = len(PROJECT_FILES)
    extracted = 0
    
    for file_path, content in PROJECT_FILES.items():
        full_path = output_path / file_path
        
        # 创建目录
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        extracted += 1
        if extracted % 50 == 0:
            print(f"  📄 已解压 {extracted}/{total_files} 文件...")
    
    print(f"✅ 项目解压完成！共解压 {extracted} 个文件")
    print(f"📁 项目位置: {output_path.absolute()}")
    
    # 创建启动脚本
    startup_script = output_path / "start.sh"
    startup_script.write_text('''#!/bin/bash
echo "🚀 启动AI视频生成器..."
echo "1. 安装依赖: ./setup.sh"
echo "2. 启动服务: docker-compose up -d"
echo "3. 访问: http://localhost:3000"
''')
    startup_script.chmod(0o755)
    
    return output_path

'''
    
    def _get_main_function(self):
        """获取主函数"""
        return '''
def create_zip_archive(output_file: str = "ai_video_project.zip"):
    """创建ZIP压缩包"""
    print(f"📦 正在创建ZIP压缩包: {output_file}")
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path, content in PROJECT_FILES.items():
            zipf.writestr(file_path, content)
    
    print(f"✅ ZIP压缩包创建完成: {output_file}")
    print(f"📊 文件大小: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
    return output_file

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI视频生成器项目工具')
    parser.add_argument('--extract', action='store_true', help='解压项目文件')
    parser.add_argument('--create-zip', action='store_true', help='创建ZIP压缩包')
    parser.add_argument('--output-dir', default='.', help='输出目录')
    parser.add_argument('--zip-file', default='ai_video_project.zip', help='ZIP文件名')
    
    args = parser.parse_args()
    
    if args.extract:
        extract_project(args.output_dir)
    elif args.create_zip:
        create_zip_archive(args.zip_file)
    else:
        print("请使用以下命令：")
        print("  --extract     解压项目文件")
        print("  --create-zip  创建ZIP压缩包")
        print("")
        print("示例：")
        print("  python ai_video_project_complete.py --extract")
        print("  python ai_video_project_complete.py --create-zip --zip-file my_project.zip")

if __name__ == "__main__":
    main()
'''
    
    def _generate_root_files(self):
        """生成根目录文件"""
        print("📁 生成根目录文件...")
        
        # README.md
        self.project_files["README.md"] = self._get_readme_content()
        
        # package.json
        self.project_files["package.json"] = json.dumps({
            "name": "ai-video-platform",
            "version": "2.0.0",
            "private": True,
            "workspaces": ["frontend", "backend", "shared"],
            "scripts": {
                "dev": "concurrently \\"npm run dev:frontend\\" \\"npm run dev:backend\\"",
                "dev:frontend": "cd frontend && npm start",
                "dev:backend": "cd backend && npm run dev",
                "build": "npm run build:frontend && npm run build:backend",
                "build:frontend": "cd frontend && npm run build",
                "build:backend": "cd backend && npm run build",
                "test": "npm run test:frontend && npm run test:backend",
                "lint": "npm run lint:frontend && npm run lint:backend",
                "docker:up": "docker-compose up -d",
                "docker:down": "docker-compose down",
                "docker:build": "docker-compose build"
            },
            "devDependencies": {
                "concurrently": "^8.0.0"
            }
        }, indent=2)
        
        # .env.example
        self.project_files[".env.example"] = """# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_video
DB_USER=postgres
DB_PASSWORD=your_password

# Redis配置
REDIS_URL=redis://localhost:6379

# JWT配置
JWT_SECRET=your_jwt_secret_here_change_in_production
JWT_EXPIRES_IN=7d

# AI服务配置
OPENAI_API_KEY=your_openai_api_key
STABILITY_API_KEY=your_stability_api_key
HUGGINGFACE_TOKEN=your_huggingface_token

# 存储配置
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=your_bucket
S3_REGION=us-east-1

# 应用配置
NODE_ENV=development
PORT=5000
CLIENT_URL=http://localhost:3000
CORS_ORIGIN=http://localhost:3000

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_email_password

# 视频处理配置
FFMPEG_PATH=/usr/bin/ffmpeg
MAX_VIDEO_SIZE=500MB
ALLOWED_VIDEO_TYPES=mp4,mov,avi,mkv
"""
        
        # docker-compose.yml
        self.project_files["docker-compose.yml"] = """version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: ai_video_postgres
    environment:
      POSTGRES_DB: ai_video
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/prisma/migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - ai_video_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: ai_video_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ai_video_network
    command: redis-server --appendonly yes

  # 后端API服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ai_video_backend
    environment:
      - NODE_ENV=production
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=ai_video
      - DB_USER=postgres
      - DB_PASSWORD=your_password
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your_jwt_secret
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./exports:/app/exports
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - ai_video_network
    restart: unless-stopped

  # 前端应用
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ai_video_frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
      - REACT_APP_WS_URL=ws://localhost:5000
    depends_on:
      - backend
    networks:
      - ai_video_network
    restart: unless-stopped

  # AI服务
  ai_service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile
    container_name: ai_video_ai_service
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=your_openai_key
      - STABILITY_API_KEY=your_stability_key
      - HUGGINGFACE_TOKEN=your_hf_token
    volumes:
      - ./ai-service/models:/app/models
      - ./ai-service/cache:/app/cache
    networks:
      - ai_video_network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

  # Nginx反向代理（可选）
  nginx:
    image: nginx:alpine
    container_name: ai_video_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/build:/usr/share/nginx/html
    depends_on:
      - frontend
      - backend
    networks:
      - ai_video_network
    restart: unless-stopped

networks:
  ai_video_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
"""
        
        # setup.sh
        self.project_files["setup.sh"] = """#!/bin/bash

echo "🚀 AI视频生成器 - 安装脚本"
echo "=========================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker和Docker Compose已安装"

# 复制环境文件
if [ ! -f .env ]; then
    echo "📋 复制环境配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置您的环境变量"
fi

# 创建必要的目录
echo "📁 创建项目目录..."
mkdir -p uploads/videos uploads/images uploads/audio exports logs

# 设置权限
echo "🔧 设置目录权限..."
chmod -R 755 uploads exports logs

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend && npm install

# 安装后端依赖
echo "📦 安装后端依赖..."
cd ../backend && npm install

# 运行数据库迁移
echo "🗄️  运行数据库迁移..."
npx prisma migrate deploy

# 启动服务
echo "🚀 启动所有服务..."
cd .. && docker-compose up -d

echo ""
echo "✅ 安装完成！"
echo ""
echo "📊 服务状态："
echo "  前端: http://localhost:3000"
echo "  后端API: http://localhost:5000"
echo "  AI服务: http://localhost:8000"
echo "  数据库: localhost:5432"
echo "  Redis: localhost:6379"
echo ""
echo "📋 管理命令："
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  更新服务: docker-compose pull && docker-compose up -d"
"""
        
        # LICENSE
        self.project_files["LICENSE"] = """MIT License

Copyright (c) 2024 AI Video Creator Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        # .gitignore
       
