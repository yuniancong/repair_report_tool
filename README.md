# 维修单工具

一个现代化的维修报告生成工具，具有半透明玻璃态界面设计。

## 特性

- 🎨 **现代化 UI** - 采用 CustomTkinter 框架，玻璃态效果和半透明设计
- 📋 **项目管理** - 轻松创建、编辑和管理多个维修项目
- 🖼️ **图片管理** - 支持拖放、批量添加和预览图片
- 📊 **Excel 导出** - 生成带图片的专业 Excel 报告
- 📄 **PDF 导出** - 生成格式化的 PDF 文档
- 💾 **项目保存** - JSON 格式保存和加载项目
- 🌗 **深色/浅色模式** - 支持系统主题切换

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

**使用启动器（推荐）:**

```bash
python launcher.py
```

启动器会自动检查依赖并提示安装缺失的包。

**直接运行:**

```bash
python repair_report_modern.py
```

## 依赖说明

### 必需依赖

- **customtkinter** - 现代化的 Tkinter UI 框架
- **Pillow** - 图像处理库

### 可选依赖

- **openpyxl** - Excel 导出功能
- **reportlab** - PDF 导出功能
- **tkinterdnd2** - 拖放功能支持

如果缺少可选依赖，相应的功能将被禁用，但核心功能仍可正常使用。

## 使用说明

### 1. 创建项目

1. 点击左侧边栏的 **"+ 添加"** 按钮
2. 在主区域输入项目描述（例如："电机维修"）

### 2. 添加图片

**方式一：** 点击 **"📸 添加图片"** 选择图片文件
**方式二：** 点击 **"📁 批量添加"** 一次性选择多张图片
**方式三：** 直接拖动图片文件到窗口中（需要 tkinterdnd2）

### 3. 设置项目标题

在顶部输入框中输入项目标题，例如："2024年11月设备维修报告"

### 4. 导出文档

**Excel:**
1. 点击右上角 **"📊 Excel"** 按钮
2. 选择保存位置
3. 等待生成完成

**PDF:**
1. 点击右上角 **"📄 PDF"** 按钮
2. 选择保存位置
3. 等待生成完成

### 5. 保存项目

- 点击左下角 **"💾 保存"** 按钮保存项目为 JSON 文件
- 使用 **"📁 打开"** 加载已保存的项目

## 界面说明

```
顶部栏
  ├─ 应用标题和图标
  ├─ 项目标题输入框（中央）
  └─ 导出和设置按钮（右侧）

左侧边栏
  ├─ 项目列表标题和添加按钮
  ├─ 搜索框
  ├─ 滚动的项目卡片列表
  ├─ 统计信息
  └─ 打开/保存按钮

主区域
  ├─ 项目描述输入
  ├─ 图片管理按钮
  └─ 图片网格画廊
```

## 故障排除

### CustomTkinter 未安装

```bash
pip install customtkinter
```

### 拖放功能不可用

```bash
# macOS
brew install tkdnd
pip install tkinterdnd2

# Linux
sudo apt-get install python3-tk
pip install tkinterdnd2
```

不安装也可以正常使用，只是无法拖放图片。

### 中文字体显示问题

确保系统已安装中文字体：

- **Windows** - 默认支持
- **macOS** - 默认支持
- **Linux** - 安装 `fonts-wqy-microhei` 或 `fonts-wqy-zenhei`

```bash
# Linux (Ubuntu/Debian)
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
```

## 许可证

MIT License
