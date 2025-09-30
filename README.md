# 京都民宿管理系统

一个现代化的京都民宿预订和管理系统，提供多语言支持、响应式设计和完整的后台管理功能。

## 🌟 主要特性

### 前端功能
- **多语言支持** - 日语、英语、中文三种语言
- **响应式设计** - 完美适配桌面端和移动端
- **房源展示** - 精美的房源卡片和详情页面
- **在线预订** - 集成Airbnb预订系统
- **SEO优化** - 完整的meta标签和结构化数据
- **简洁设计** - 无动画干扰的纯净用户体验

### 后台管理
- **仪表盘** - 实时数据统计和概览
- **房源管理** - 添加、编辑、删除房源信息
- **预订管理** - 查看和管理客户预订
- **消息管理** - 处理客户咨询和反馈
- **新闻管理** - 发布和管理网站新闻
- **内容管理** - 编辑首页和联系页面内容
- **用户管理** - 管理员账户管理
- **数据备份** - 自动备份和手动导出功能

## 🚀 快速开始

### 环境要求
- Python 3.8+
- SQLite 3
- 现代浏览器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd GuestHouse
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python app.py
```
首次运行会自动创建数据库和默认管理员账户。

5. **启动应用**
```bash
python app.py
```

6. **访问应用**
- 前端：http://localhost:5000
- 后台：http://localhost:5000/admin
- 默认管理员：admin / admin123

## 📁 项目结构

```
GuestHouse/
├── app.py                 # 主应用文件
├── models.py              # 数据模型
├── forms.py               # 表单定义
├── translations.py        # 多语言翻译
├── db.db                  # SQLite数据库
├── users.json             # 用户配置文件
├── requirements.txt       # Python依赖
├── static/                # 静态资源
│   ├── css/
│   │   └── style.css      # 主样式文件
│   ├── js/
│   │   └── script.js      # JavaScript文件
│   └── img/               # 图片资源
├── templates/             # HTML模板
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页
│   ├── rooms.html         # 房源列表
│   ├── room_detail.html   # 房源详情
│   ├── management.html    # 管理服务页面
│   ├── contact.html       # 联系页面
│   ├── booking.html       # 预订页面
│   └── admin_*.html       # 后台管理页面
├── backups/               # 数据库备份目录
└── README.md              # 项目说明
```

## 🎨 设计特色

### 视觉设计
- **日式美学** - 采用传统京都风格的设计语言
- **色彩搭配** - 温暖的米色和棕色系主色调
- **字体选择** - 日式衬线字体与无衬线字体的完美结合
- **布局设计** - 简洁优雅的卡片式布局

### 用户体验
- **无动画干扰** - 去除所有动画效果，提供纯净的浏览体验
- **快速加载** - 优化的图片和资源加载
- **直观导航** - 清晰的信息架构和导航结构
- **移动优先** - 响应式设计确保各设备完美显示

## 🔧 技术栈

### 后端
- **Flask** - Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **Flask-Login** - 用户认证管理
- **Flask-WTF** - 表单处理和CSRF保护
- **SQLite** - 轻量级数据库

### 前端
- **Bootstrap 5** - CSS框架
- **HTML5** - 语义化标记
- **CSS3** - 现代样式特性
- **JavaScript** - 交互功能
- **Font Awesome** - 图标库

### 开发工具
- **Python 3.8+** - 编程语言
- **Git** - 版本控制
- **SQLite** - 数据库

## 📱 功能详解

### 多语言支持
系统支持三种语言：
- **日语** (ja) - 默认语言
- **英语** (en) - 国际用户
- **中文** (zh) - 中文用户

语言切换通过URL参数实现：
- 日语：`/` 或 `/ja/`
- 英语：`/en/`
- 中文：`/zh/`

### 房源管理
- 支持多语言房源信息
- 图片上传和管理
- 价格和容量设置
- 设施和描述管理
- Airbnb链接集成

### 预订系统
- 集成Airbnb预订
- 预订状态跟踪
- 客户信息管理
- 预订历史记录

### 内容管理
- 首页内容编辑
- 联系页面管理
- 新闻发布系统
- JSON格式内容存储

### 数据备份
- 自动数据库备份
- 手动导出功能
- 备份文件管理
- 历史备份查看

## 🛠️ 配置说明

### 数据库配置
数据库文件位于根目录的 `db.db`，包含以下表：
- `room` - 房源信息
- `booking` - 预订记录
- `message` - 客户消息
- `news` - 新闻内容
- `site_content` - 网站内容
- `admin` - 管理员账户

### 用户管理
用户信息存储在 `users.json` 文件中，支持：
- 添加新用户
- 修改密码
- 删除用户
- 权限管理

### 备份配置
备份文件存储在 `backups/` 目录：
- 自动保留最近10个备份
- 支持手动下载
- 备份时间记录

## 🚀 部署指南

### 生产环境部署

1. **服务器要求**
   - Linux/Unix系统
   - Python 3.8+
   - Nginx或Apache
   - SQLite支持

2. **部署步骤**
```bash
# 1. 上传代码到服务器
git clone <repository-url>
cd GuestHouse

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
export FLASK_ENV=production
export FLASK_APP=app.py

# 5. 启动应用
python app.py
```

3. **Nginx配置示例**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/GuestHouse/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Docker部署（可选）

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## 🔒 安全特性

- **CSRF保护** - 所有表单都有CSRF令牌
- **SQL注入防护** - 使用SQLAlchemy ORM
- **XSS防护** - 模板自动转义
- **用户认证** - 安全的登录系统
- **文件上传安全** - 限制文件类型和大小

## 📊 性能优化

- **图片优化** - 使用现代图片格式（AVIF、WebP）
- **CSS优化** - 去除不必要的动画和过渡
- **JavaScript优化** - 最小化JS代码
- **数据库优化** - 合理的索引和查询
- **缓存策略** - 静态资源缓存

## 🐛 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查 `db.db` 文件权限
   - 确保SQLite已安装

2. **图片不显示**
   - 检查 `static/img/` 目录
   - 验证图片路径正确性

3. **多语言不工作**
   - 检查 `translations.py` 文件
   - 验证语言代码正确性

4. **后台无法访问**
   - 检查管理员账户
   - 验证登录凭据

### 日志查看
应用日志会显示在控制台，包括：
- 数据库操作
- 用户登录
- 错误信息
- 系统状态

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 邮箱：info@kakuka-anbo.com
- 电话：+81-75-XXX-XXXX
- 地址：京都府京都市

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户。

---

**Kakuka Anbo Co., Ltd.** - 专业的京都民宿管理解决方案