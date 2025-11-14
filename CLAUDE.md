# CLAUDE.md - AI Assistant Guide for Repair Report Tool

This document provides comprehensive guidance for AI assistants working with the Repair Report Tool codebase. Last updated: 2025-11-14

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Architecture & Design](#architecture--design)
4. [Key Files Reference](#key-files-reference)
5. [Development Workflows](#development-workflows)
6. [Code Conventions](#code-conventions)
7. [Common Tasks Guide](#common-tasks-guide)
8. [Git Workflow](#git-workflow)
9. [Dependencies & Features](#dependencies--features)
10. [Important Notes for AI Assistants](#important-notes-for-ai-assistants)

---

## Project Overview

### What This Is

A modern desktop application for generating repair reports with images. The tool allows users to:
- Create and manage multiple repair projects
- Add images to each repair item
- Export professional reports to Excel and PDF formats
- Save/load projects in JSON format

### Two Versions

The repository contains **two implementations** of the same application:

| File | Version | UI Framework | Status |
|------|---------|--------------|--------|
| `repair_report_modern.py` | v2.0 Modern Edition | CustomTkinter | **Active Development** |
| `repair_report_tool-11.py` | v1.7.4 Original | Standard Tkinter | Maintenance Only |

**Key Difference**: The Modern Edition features a RepoPrompt-inspired glassmorphism UI with light theme, while the original uses traditional Tkinter widgets.

**Data Compatibility**: Both versions use the same JSON format and are fully compatible.

### Technology Stack

- **Language**: Python 3.7+
- **UI Framework**: CustomTkinter (Modern) / Tkinter (Original)
- **Image Processing**: Pillow (PIL)
- **Excel Export**: openpyxl
- **PDF Export**: ReportLab
- **Drag & Drop**: tkinterdnd2 (optional)

### User Audience

- Repair technicians and maintenance workers
- Chinese-speaking users (interface in Simplified Chinese)
- Desktop environment (Windows, macOS, Linux)

---

## Repository Structure

```
repair_report_tool/
├── .git/                           # Git repository data
├── .gitignore                      # Git ignore patterns
│
├── repair_report_modern.py         # Main application - Modern Edition v2.0 ⭐
├── repair_report_tool-11.py        # Original version v1.7.4
├── launcher.py                     # Dependency checker and launcher
│
├── requirements.txt                # Python dependencies
│
├── README_MODERN.md                # Modern Edition documentation
├── QUICKSTART.md                   # Quick start guide
├── COMPARISON.md                   # Version comparison table
└── CLAUDE.md                       # This file - AI assistant guide
```

### File Organization

- **No subdirectories**: All code is in the root directory
- **Flat structure**: Single-file applications (monolithic)
- **No tests directory**: Tests not currently implemented
- **No build/dist**: Direct execution via Python interpreter

---

## Architecture & Design

### Application Type

**Single-window Desktop GUI** with component-based architecture.

### Design Pattern: MVC-like

```
┌─────────────────────────────────────────────────────┐
│                     MODEL                            │
│  self.items = [{'id', 'description', 'images'}]     │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│                   CONTROLLER                         │
│  Event handlers in ModernRepairTool class           │
│  (add_item, delete_item, save_project, etc.)        │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│                      VIEW                            │
│  CustomTkinter widgets (buttons, frames, labels)    │
└─────────────────────────────────────────────────────┘
```

### Main Class: `ModernRepairTool(ctk.CTk)`

**Single class handles everything:**
- Window management and UI layout
- Data model (items list)
- Event handling
- File I/O operations
- Image processing and caching
- Export functionality

### UI Layout Structure

```
┌──────────────────────────────────────────────────────┐
│  Top Bar (80px)                                      │
│  Title | Project Input Field | Export Buttons        │
├────────────────┬─────────────────────────────────────┤
│                │                                     │
│  Sidebar       │  Main Area                          │
│  (380px)       │  (Remaining space)                  │
│                │                                     │
│  - Search      │  - Description TextBox              │
│  - Item Cards  │  - Image Gallery (Grid)             │
│  - Statistics  │                                     │
│  - Save/Load   │                                     │
│                │                                     │
├────────────────┴─────────────────────────────────────┤
│  Status Bar (40px)                                   │
│  Status Message | Feature Indicators (✓DnD ✓Excel)  │
└──────────────────────────────────────────────────────┘
```

### Data Model

#### Item Structure
```python
{
    'id': 1,                           # Auto-incrementing unique ID
    'description': '电机维修',          # Text description
    'images': [                        # List of absolute file paths
        '/path/to/image1.jpg',
        '/path/to/image2.png'
    ]
}
```

#### Project Structure (JSON)
```python
{
    'title': '2024年11月维修报告',      # Project title
    'items': [...]                     # List of item dicts
}
```

### Caching Strategy

- **Image Cache**: `self.image_cache` - Original PIL Image objects
- **Thumbnail Cache**: `self.thumbnail_cache` - Resized PhotoImage objects
- **Cache Key**: Absolute file path
- **Benefits**: Prevents repeated file I/O and image processing

### Design Patterns Used

1. **Factory Pattern**: `create_item_card()`, `create_image_card()`, `create_modern_button()`
2. **Singleton**: Single `ModernRepairTool` instance
3. **Observer/Event Handler**: UI widgets bound to callback methods
4. **Strategy Pattern**: Conditional export strategies (Excel/PDF)
5. **Lazy Loading**: Images loaded only when displayed

---

## Key Files Reference

### `repair_report_modern.py` (Main Application)

**Lines of Code**: ~2,150

**Key Sections**:
- Lines 1-58: Imports and feature detection
- Lines 60-108: Class initialization and configuration
- Lines 109-123: UI setup orchestration
- Lines 124-242: Top bar creation
- Lines 243-467: Sidebar creation (item list)
- Lines 468-685: Main area (image gallery)
- Lines 686-705: Status bar
- Lines 706-800: Menu bar creation
- Lines 801-950: Item management methods
- Lines 951-1250: Image management methods
- Lines 1251-1450: Export functionality (Excel)
- Lines 1451-1650: Export functionality (PDF)
- Lines 1651-1750: File operations (save/load JSON)
- Lines 1751-1811: Drag & drop handlers
- Lines 1812-1850: Keyboard shortcuts
- Lines 1851-2000: Dialog boxes (settings, about, help)
- Lines 2001-2150: Utility methods
- Lines 2153-2186: `main()` entry point

**Key Methods**:

| Method | Line Range | Purpose |
|--------|------------|---------|
| `__init__()` | 63-108 | Initialize application |
| `setup_ui()` | 109-123 | Create main layout |
| `add_item()` | ~850 | Create new repair item |
| `select_item_optimized()` | ~920 | Select item without full refresh |
| `add_images()` | ~1000 | Add images to current item |
| `batch_add_images()` | ~1050 | Batch image assignment |
| `export_excel()` | ~1260 | Generate Excel report |
| `export_pdf()` | ~1460 | Generate PDF report |
| `save_project()` | ~1660 | Save to JSON |
| `open_project()` | ~1700 | Load from JSON |

### `launcher.py` (Dependency Checker)

**Purpose**: Check and install dependencies before launching the app

**Workflow**:
1. Check for required packages (customtkinter, Pillow)
2. Check for optional packages (openpyxl, reportlab, tkinterdnd2)
3. Offer to auto-install missing required packages
4. Warn about missing optional packages
5. Import and run `repair_report_modern.main()`

**Usage**: `python launcher.py`

### `requirements.txt` (Dependencies)

```
customtkinter>=5.2.0    # Required - Modern UI framework
Pillow>=9.0.0           # Required - Image processing
openpyxl>=3.0.0         # Optional - Excel export
reportlab>=3.6.0        # Optional - PDF export
tkinterdnd2>=0.3.0      # Optional - Drag & drop
```

### `.gitignore` (Version Control)

**Key Exclusions**:
- Python cache: `__pycache__/`, `*.pyc`
- Virtual environments: `venv/`, `ENV/`
- Project files: `*.json`, `*.xlsx`, `*.pdf` (except demo files)
- Temp images: `temp_*.png`, `temp_*.jpg`
- IDE files: `.vscode/`, `.idea/`

---

## Development Workflows

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone <repository-url>
cd repair_report_tool

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python repair_report_modern.py
# OR
python launcher.py
```

### Running the Application

```bash
# Method 1: Direct execution
python repair_report_modern.py

# Method 2: Via launcher (checks dependencies)
python launcher.py

# Method 3: Original version
python repair_report_tool-11.py
```

### Testing Changes

**Current State**: No automated tests exist

**Manual Testing Checklist**:
1. Launch application successfully
2. Create new repair item
3. Add images (via dialog and drag & drop)
4. Edit item descriptions
5. Delete items and images
6. Save project to JSON
7. Load project from JSON
8. Export to Excel (if available)
9. Export to PDF (if available)
10. Test all keyboard shortcuts
11. Verify UI updates correctly

### Debugging

**Print Debugging**: The application uses console prints

```python
# Example debug points:
print(f"Items: {self.items}")  # Check data model
print(f"Selected: {self.selected_item_index}")  # Check selection
print(f"Image path: {path}")  # Check file paths
```

**Common Issues**:
- **Images not showing**: Check file paths are absolute
- **Export fails**: Verify openpyxl/reportlab installed
- **DnD not working**: Check tkinterdnd2 installed
- **UI not updating**: Ensure `refresh_item_list()` called after changes

---

## Code Conventions

### Language & Encoding

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

- **Python 3.7+** required
- **UTF-8 encoding** for Chinese text support
- **Shebang** for Unix-like systems

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Class | PascalCase | `ModernRepairTool` |
| Method | snake_case | `add_item()`, `export_excel()` |
| Variable | snake_case | `selected_item_index`, `image_cache` |
| Constant | UPPER_SNAKE_CASE | `EXCEL_AVAILABLE`, `DND_FILES` |
| Private | Leading underscore | `_cleanup_temp_files()`, `_split_dnd_paths()` |

### Code Style

- **Indentation**: 4 spaces (no tabs)
- **Line length**: No strict limit, but keep readable (~80-120 chars)
- **Imports**: Standard library → Third-party → Local
- **Docstrings**: Used for main class and complex methods
- **Comments**: Chinese comments inline with code

### Color Scheme Definition

**Always define in `__init__()` as `self.colors` dict**:

```python
self.colors = {
    'bg_primary': '#F8F9FA',      # Background colors
    'bg_secondary': '#FFFFFF',
    'accent': '#0D6EFD',          # Interactive elements
    'text_primary': '#212529',    # Text colors
    'success': '#198754',         # Status colors
    'error': '#DC3545'
}
```

### UI Widget Creation Pattern

**Standard pattern for creating styled widgets**:

```python
widget = ctk.CTkButton(
    parent,
    text="Button Text",
    width=100,
    height=40,
    corner_radius=10,
    font=ctk.CTkFont(size=14),
    fg_color=self.colors['accent'],
    hover_color=self.colors['accent_hover'],
    command=self.callback_method
)
widget.pack(padx=10, pady=5)
```

### Event Handler Pattern

**Bind events to methods, not lambdas when possible**:

```python
# Good: Named method
button.configure(command=self.add_item)

# Acceptable: Lambda with parameter
button.configure(command=lambda: self.delete_item(idx))

# Avoid: Complex lambdas
```

### Error Handling Pattern

**Use try-except with user feedback**:

```python
try:
    # Operation that might fail
    result = operation()
    self.show_status("✓ Success message", "success")
except FileNotFoundError:
    messagebox.showerror("错误", "文件未找到")
except Exception as e:
    messagebox.showerror("错误", f"操作失败: {str(e)}")
    self.show_status("✗ Error message", "error")
```

---

## Common Tasks Guide

### Adding a New Feature to Modern Edition

#### 1. Add UI Element

```python
def create_new_feature_ui(self):
    """Add UI for new feature"""
    # Create widget
    button = ctk.CTkButton(
        self.sidebar_frame,
        text="New Feature",
        command=self.new_feature_action
    )
    button.pack(pady=5)
```

#### 2. Implement Handler

```python
def new_feature_action(self):
    """Handle new feature action"""
    try:
        # Implement logic
        self.show_status("✓ Feature executed", "success")
    except Exception as e:
        messagebox.showerror("错误", f"Feature failed: {e}")
```

#### 3. Update Data Model (if needed)

```python
def __init__(self):
    # ... existing code ...
    self.new_feature_data = []  # Add to data model
```

#### 4. Add to Save/Load (if persistent)

```python
def save_project(self):
    data = {
        'title': self.project_title_var.get(),
        'items': self.items,
        'new_feature_data': self.new_feature_data  # Include in save
    }
```

### Fixing UI Issues

#### Common UI Bug: Widget Not Updating

**Problem**: UI doesn't reflect data changes

**Solution**:
```python
# After modifying self.items:
self.refresh_item_list()  # Rebuild sidebar
self.display_item_images(idx)  # Update image gallery
```

#### Common UI Bug: Description Text Jumping

**Problem**: Cursor jumps when typing in description

**Solution**: Already fixed in recent commits
- Use `self.description_text.edit_modified(False)` to prevent recursion
- Avoid calling `refresh_item_list()` on every keystroke

### Adding Export Format

#### 1. Check for Library

```python
try:
    import new_export_library
    NEW_FORMAT_AVAILABLE = True
except ImportError:
    NEW_FORMAT_AVAILABLE = False
```

#### 2. Add Export Method

```python
def export_new_format(self):
    """Export to new format"""
    if not NEW_FORMAT_AVAILABLE:
        messagebox.showwarning("警告", "需要安装 new_export_library")
        return

    # Get save path
    path = filedialog.asksaveasfilename(
        defaultextension=".ext",
        filetypes=[("New Format", "*.ext")]
    )
    if not path:
        return

    try:
        # Export logic
        self.show_status("✓ 导出成功", "success")
    except Exception as e:
        messagebox.showerror("错误", f"导出失败: {e}")
```

#### 3. Add UI Button

```python
# In create_top_bar():
if NEW_FORMAT_AVAILABLE:
    ctk.CTkButton(
        action_frame,
        text="📄 New Format",
        command=self.export_new_format
    ).pack(side="left", padx=5)
```

### Modifying Color Scheme

**Location**: `ModernRepairTool.__init__()` around lines 88-101

```python
self.colors = {
    'bg_primary': '#NEW_COLOR',    # Update hex values
    'accent': '#NEW_ACCENT',
    # ... etc
}
```

**Note**: Colors are referenced throughout the code as `self.colors['key']`

---

## Git Workflow

### Branch Strategy

**Main Branch**: `main` (or `master`)
- Production-ready code
- Merge via pull requests only

**Feature Branches**: `claude/feature-description-<session-id>`
- Pattern: `claude/claude-md-mhy68r14d4at1bgs-<unique-id>`
- Must match session ID for push to succeed (403 error otherwise)

### Commit Message Convention

**Pattern**: `<type>: <description>`

**Types**:
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `docs:` - Documentation
- `style:` - Formatting, no code change
- `chore:` - Maintenance tasks

**Examples** (from recent history):
```
feat: Add Modern Edition with RepoPrompt-inspired UI
fix: 修复拖拽功能和描述编辑跳闪问题
refactor: Optimize item selection performance
docs: Update README with new features
```

### Making Changes

```bash
# 1. Ensure on correct branch
git status  # Should show: claude/claude-md-mhy68r14d4at1bgs-<id>

# 2. Make changes to files
# ... edit files ...

# 3. Stage changes
git add <files>

# 4. Commit with clear message
git commit -m "fix: 描述问题和解决方案"

# 5. Push to remote (use -u for first push)
git push -u origin <branch-name>
```

### Pull Request Workflow

**Creating PR**:
1. Push all commits to feature branch
2. Create PR via GitHub web interface
3. Describe changes in PR body
4. Wait for review/merge

**PR Title Format**: Same as commit message conventions

### Git Operations with Retry

**Important**: Network operations should retry with exponential backoff

```bash
# Push with retry (if network fails)
git push -u origin <branch>
# If fails, wait 2s, retry
# If fails, wait 4s, retry
# If fails, wait 8s, retry
# If fails, wait 16s, fail
```

---

## Dependencies & Features

### Required Dependencies

| Package | Version | Purpose | Installation |
|---------|---------|---------|--------------|
| customtkinter | >=5.2.0 | Modern UI framework | `pip install customtkinter` |
| Pillow | >=9.0.0 | Image processing | `pip install Pillow` |

**Without these**: Application won't start

### Optional Dependencies

| Package | Version | Purpose | Fallback Behavior |
|---------|---------|---------|-------------------|
| openpyxl | >=3.0.0 | Excel export | Export button disabled |
| reportlab | >=3.6.0 | PDF export | Export button disabled |
| tkinterdnd2 | >=0.3.0 | Drag & drop | Feature unavailable, file dialog still works |

### Feature Flags

**Global constants set at startup**:

```python
EXCEL_AVAILABLE = True/False    # Set based on openpyxl import
PDF_AVAILABLE = True/False      # Set based on reportlab import
DRAG_DROP_AVAILABLE = True/False # Set based on tkinterdnd2 import
```

**Usage in code**:

```python
if EXCEL_AVAILABLE:
    # Show Excel button
    ctk.CTkButton(..., command=self.export_excel)
else:
    # Hide or disable button
    pass
```

### Platform-Specific Considerations

#### Windows
- Full drag & drop support
- Native file dialogs
- Chinese fonts pre-installed

#### macOS
- May need `brew install tkdnd` for drag & drop
- Native file dialogs
- Chinese fonts pre-installed

#### Linux
- May need `sudo apt-get install python3-tk`
- May need Chinese fonts: `fonts-wqy-microhei fonts-wqy-zenhei`
- Drag & drop may require system libraries

---

## Important Notes for AI Assistants

### When Modifying Code

1. **Always read the file first** before editing
2. **Test changes mentally** - Does this break existing functionality?
3. **Consider data compatibility** - Will saved JSON files still work?
4. **Update both versions?** - Usually only modify Modern Edition
5. **Check feature flags** - Is the feature available to all users?

### Performance Considerations

1. **Image caching is critical** - Don't remove `self.image_cache` logic
2. **Avoid full refreshes** - Use `select_item_optimized()` instead of `refresh_item_list()`
3. **Lazy load images** - Only load when displaying, not at startup
4. **Clean up temp files** - Use `_cleanup_temp_files()` after exports

### UI/UX Principles

1. **Light theme only** - Modern Edition uses light colors, not dark
2. **Glassmorphism style** - Semi-transparent, rounded corners
3. **Chinese language** - All UI text in Simplified Chinese
4. **Consistent spacing** - Use padx/pady consistently (usually 10, 15, 20)
5. **User feedback** - Always show status messages for actions

### Common Pitfalls to Avoid

❌ **Don't**: Modify `self.items` directly without UI update
```python
self.items.append(new_item)  # UI won't update!
```

✅ **Do**: Use methods that handle both data and UI
```python
self.add_item()  # Handles data AND UI
```

---

❌ **Don't**: Use relative paths for images
```python
image_path = "photo.jpg"  # Will break when working directory changes
```

✅ **Do**: Use absolute paths
```python
image_path = os.path.abspath("photo.jpg")
```

---

❌ **Don't**: Call `refresh_item_list()` in tight loops
```python
for item in items:
    self.items.append(item)
    self.refresh_item_list()  # Very slow!
```

✅ **Do**: Update data, then refresh once
```python
for item in items:
    self.items.append(item)
self.refresh_item_list()  # Once at end
```

---

❌ **Don't**: Assume optional features available
```python
def export_pdf():
    # Will crash if reportlab not installed
    from reportlab import ...
```

✅ **Do**: Check feature flags
```python
def export_pdf():
    if not PDF_AVAILABLE:
        messagebox.showwarning("警告", "需要安装 reportlab")
        return
    # ... export logic
```

### Testing Recommendations

**Before committing changes**:

1. ✅ Run application and verify it starts
2. ✅ Test the specific feature you modified
3. ✅ Test save/load (ensure JSON compatibility)
4. ✅ Test with missing optional dependencies
5. ✅ Check for console errors/warnings
6. ✅ Verify UI doesn't have visual glitches
7. ✅ Test keyboard shortcuts if modified

### Documentation Updates

**When adding features**, update:
- This file (CLAUDE.md) - Add to Common Tasks section
- README_MODERN.md - Add to Features section
- QUICKSTART.md - Add to usage instructions if user-facing

**When fixing bugs**:
- Add note to git commit message
- Consider adding to Common Pitfalls section here

### Asking for Clarification

**When uncertain about**:
- **Design decisions**: Ask user about preferred approach
- **UI changes**: Describe proposed change, ask for approval
- **Breaking changes**: Warn user and ask for confirmation
- **Feature scope**: Clarify requirements before implementing

---

## Quick Reference

### File Paths

```python
# Always use absolute paths
abs_path = os.path.abspath(relative_path)

# Prefer pathlib for cross-platform compatibility
from pathlib import Path
path = Path(file_path).resolve()
```

### Image Processing

```python
# Load image
img = Image.open(path)

# Resize for thumbnail
img.thumbnail((200, 200), Image.Resampling.LANCZOS)

# Convert for Tkinter
photo = ImageTk.PhotoImage(img)

# Cache it
self.thumbnail_cache[path] = photo
```

### Status Messages

```python
# Success (green)
self.show_status("✓ 操作成功", "success")

# Error (red)
self.show_status("✗ 操作失败", "error")

# Info (default)
self.show_status("就绪", "")
```

### Dialogs

```python
# File open
path = filedialog.askopenfilename(
    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
)

# File save
path = filedialog.asksaveasfilename(
    defaultextension=".json",
    filetypes=[("JSON files", "*.json")]
)

# Confirmation
result = messagebox.askyesno("确认", "Are you sure?")

# Error message
messagebox.showerror("错误", "Error message here")

# Warning
messagebox.showwarning("警告", "Warning message")

# Info
messagebox.showinfo("信息", "Info message")
```

---

## Version History

### v2.0.0 (Modern Edition) - Current

- ✨ RepoPrompt-inspired glassmorphism UI
- 🎨 Light theme with semi-transparent effects
- 📱 Component-based layout
- 🔧 Performance optimizations
- 🖱️ Improved drag & drop handling
- ⌨️ Full keyboard shortcut support
- 🎯 Menu bar with File/Edit/View/Help
- 📊 Enhanced batch image assignment
- 🔍 Search box UI (functionality pending)

### v1.7.4 (Original) - Maintenance

- Traditional Tkinter interface
- Full feature parity with Modern Edition
- Stable and well-tested

---

## Contact & Support

### For Issues

1. Check existing documentation (README_MODERN.md, QUICKSTART.md)
2. Review COMPARISON.md for version differences
3. Check recent git commits for similar fixes
4. Submit GitHub issue with detailed description

### For Feature Requests

1. Describe use case clearly
2. Explain expected behavior
3. Consider backward compatibility
4. Submit as GitHub issue or PR

---

## Conclusion

This guide provides comprehensive information for AI assistants working with the Repair Report Tool codebase. When in doubt:

1. **Read the code** - The implementation is the source of truth
2. **Test thoroughly** - Manual testing is required
3. **Ask for clarification** - Don't assume user intent
4. **Preserve compatibility** - Don't break existing functionality
5. **Follow conventions** - Maintain consistency with existing code

**Happy coding!** 🚀
