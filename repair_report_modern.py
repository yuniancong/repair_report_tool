#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
维修单工具 - Modern UI Edition v2.0.0
RepoPrompt-inspired glassmorphism design with semi-transparent effects
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import os
import json
from datetime import datetime
from pathlib import Path
import tempfile
import uuid
import platform
import sys
import glob
import threading

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

# Excel export
try:
    import openpyxl
    from openpyxl.drawing import image as xl_image
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# PDF export
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RL_Image, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Drag and drop
DRAG_DROP_AVAILABLE = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    import tkinterdnd2 as _tkdnd_pkg
    DRAG_DROP_AVAILABLE = True
except ImportError:
    _tkdnd_pkg = None


class ModernRepairTool(ctk.CTk):
    """Modern repair report tool with glassmorphism UI"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("维修单工具 Modern Edition v2.0")
        self.geometry("1600x1000")

        # Try to set window transparency (works on Windows/macOS)
        try:
            self.attributes('-alpha', 0.98)
        except:
            pass

        # Data model
        self.project_title_var = ctk.StringVar(value="")
        self.items = []
        self.current_item_id = 0
        self.selected_item_index = None
        self.max_images_per_row = 1

        # Caches
        self.image_cache = {}
        self.thumbnail_cache = {}

        # Color scheme - RepoPrompt inspired
        self.colors = {
            'bg_primary': '#0D1117',      # Dark background
            'bg_secondary': '#161B22',    # Slightly lighter
            'bg_tertiary': '#21262D',     # Even lighter
            'accent': '#58A6FF',          # Blue accent
            'accent_hover': '#79C0FF',    # Lighter blue
            'text_primary': '#F0F6FC',    # White text
            'text_secondary': '#8B949E',  # Gray text
            'border': '#30363D',          # Border color
            'success': '#3FB950',         # Green
            'warning': '#D29922',         # Orange
            'error': '#F85149',           # Red
            'glass': 'rgba(255, 255, 255, 0.1)'  # Glassmorphism
        }

        # Initialize UI
        self.setup_ui()
        self.setup_drag_drop()

    def setup_ui(self):
        """Setup the modern UI layout"""
        # Configure grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(0, weight=0)     # Top bar
        self.grid_rowconfigure(1, weight=1)     # Content area
        self.grid_rowconfigure(2, weight=0)     # Status bar

        # Create sections
        self.create_top_bar()
        self.create_sidebar()
        self.create_main_area()
        self.create_status_bar()

    def create_top_bar(self):
        """Create modern top bar with title and controls"""
        top_frame = ctk.CTkFrame(
            self,
            height=80,
            corner_radius=0,
            fg_color=self.colors['bg_secondary']
        )
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        top_frame.grid_columnconfigure(1, weight=1)

        # App icon and title
        title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)

        ctk.CTkLabel(
            title_frame,
            text="🔧",
            font=ctk.CTkFont(size=32)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            title_frame,
            text="维修单工具",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="Modern Edition",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        ).pack(side="left", padx=(10, 0))

        # Project title input (centered)
        title_input_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_input_frame.grid(row=0, column=1, sticky="ew", padx=40, pady=15)

        ctk.CTkLabel(
            title_input_frame,
            text="项目标题",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w", pady=(0, 5))

        self.title_entry = ctk.CTkEntry(
            title_input_frame,
            textvariable=self.project_title_var,
            placeholder_text="输入项目标题...",
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=10
        )
        self.title_entry.pack(fill="x")

        # Action buttons (right side)
        action_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        action_frame.grid(row=0, column=2, sticky="e", padx=20, pady=15)

        # Export buttons with icons
        if EXCEL_AVAILABLE:
            self.create_modern_button(
                action_frame,
                "📊 Excel",
                self.export_excel,
                "left",
                success=False
            )

        if PDF_AVAILABLE:
            self.create_modern_button(
                action_frame,
                "📄 PDF",
                self.export_pdf,
                "left",
                success=False
            )

        # Settings button
        self.create_modern_button(
            action_frame,
            "⚙️",
            self.show_settings,
            "left",
            width=50
        )

    def create_modern_button(self, parent, text, command, side="left", width=120, success=False):
        """Create a modern glassmorphic button"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors['success'] if success else self.colors['accent'],
            hover_color=self.colors['accent_hover']
        )
        btn.pack(side=side, padx=5)
        return btn

    def create_sidebar(self):
        """Create modern sidebar with project list"""
        sidebar = ctk.CTkFrame(
            self,
            width=380,
            corner_radius=0,
            fg_color=self.colors['bg_secondary']
        )
        sidebar.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)

        # Sidebar header
        header = ctk.CTkFrame(sidebar, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="维修项目",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")

        # Add button
        add_btn = ctk.CTkButton(
            header,
            text="+ 添加",
            width=80,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            command=self.add_item
        )
        add_btn.pack(side="right")

        # Search bar
        self.search_entry = ctk.CTkEntry(
            sidebar,
            placeholder_text="🔍 搜索项目...",
            height=36,
            corner_radius=8
        )
        self.search_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Scrollable frame for items
        self.items_scroll = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            corner_radius=0
        )
        self.items_scroll.pack(fill="both", expand=True, padx=15, pady=0)

        # Stats at bottom
        stats_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['bg_tertiary'], height=80)
        stats_frame.pack(fill="x", padx=15, pady=15, side="bottom")

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="0 项目 • 0 图片",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_secondary']
        )
        self.stats_label.pack(pady=15)

        # Action buttons
        btn_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15), side="bottom")

        ctk.CTkButton(
            btn_frame,
            text="📁 打开",
            command=self.open_project,
            height=36,
            corner_radius=8,
            fg_color=self.colors['bg_tertiary'],
            hover_color=self.colors['border']
        ).pack(side="left", expand=True, padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="💾 保存",
            command=self.save_project,
            height=36,
            corner_radius=8,
            fg_color=self.colors['bg_tertiary'],
            hover_color=self.colors['border']
        ).pack(side="right", expand=True, padx=(5, 0))

    def create_main_area(self):
        """Create main content area for images"""
        main_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.colors['bg_primary']
        )
        main_frame.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)

        # Content header
        content_header = ctk.CTkFrame(main_frame, fg_color="transparent", height=70)
        content_header.pack(fill="x", padx=30, pady=(20, 10))

        # Item description area
        desc_frame = ctk.CTkFrame(content_header, fg_color="transparent")
        desc_frame.pack(fill="x")

        ctk.CTkLabel(
            desc_frame,
            text="项目描述",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w", pady=(0, 5))

        self.description_entry = ctk.CTkEntry(
            desc_frame,
            placeholder_text="输入维修项目描述...",
            height=40,
            font=ctk.CTkFont(size=13),
            corner_radius=8
        )
        self.description_entry.pack(fill="x", pady=(0, 10))
        self.description_entry.bind('<KeyRelease>', self.on_description_change)

        # Image controls
        img_control_frame = ctk.CTkFrame(content_header, fg_color="transparent")
        img_control_frame.pack(fill="x")

        ctk.CTkLabel(
            img_control_frame,
            text="图片管理",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        ).pack(side="left")

        # Image action buttons
        ctk.CTkButton(
            img_control_frame,
            text="📸 添加图片",
            command=self.add_images,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover']
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            img_control_frame,
            text="📁 批量添加",
            command=self.batch_add_images,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['bg_tertiary'],
            hover_color=self.colors['border']
        ).pack(side="right", padx=5)

        # Scrollable image gallery
        self.image_gallery = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.image_gallery.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Configure grid for image gallery
        for i in range(4):
            self.image_gallery.grid_columnconfigure(i, weight=1)

        # Drop zone indicator
        self.drop_zone = ctk.CTkFrame(
            self.image_gallery,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15,
            border_width=2,
            border_color=self.colors['border']
        )
        self.drop_zone.pack(fill="both", expand=True, padx=20, pady=50)

        drop_content = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        drop_content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            drop_content,
            text="📁",
            font=ctk.CTkFont(size=64)
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            drop_content,
            text="拖拽图片到这里" if DRAG_DROP_AVAILABLE else "点击'添加图片'按钮",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack()

        ctk.CTkLabel(
            drop_content,
            text="或点击'添加图片'按钮选择文件",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_secondary']
        ).pack(pady=(5, 0))

    def create_status_bar(self):
        """Create modern status bar"""
        status_frame = ctk.CTkFrame(
            self,
            height=40,
            corner_radius=0,
            fg_color=self.colors['bg_secondary']
        )
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="就绪",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        self.status_label.pack(side="left", padx=20)

        # Feature indicators
        features = []
        if DRAG_DROP_AVAILABLE:
            features.append("✓ 拖拽")
        if EXCEL_AVAILABLE:
            features.append("✓ Excel")
        if PDF_AVAILABLE:
            features.append("✓ PDF")

        feature_text = " • ".join(features)
        ctk.CTkLabel(
            status_frame,
            text=feature_text,
            font=ctk.CTkFont(size=11),
            text_color=self.colors['success']
        ).pack(side="right", padx=20)

    def setup_drag_drop(self):
        """Setup drag and drop if available"""
        if not DRAG_DROP_AVAILABLE:
            return
        # Note: CustomTkinter doesn't directly support TkinterDnD
        # This would need additional implementation
        pass

    def add_item(self):
        """Add new repair item"""
        self.current_item_id += 1
        new_item = {
            'id': self.current_item_id,
            'description': f"维修项目 {len(self.items) + 1}",
            'images': []
        }
        self.items.append(new_item)
        self.refresh_item_list()
        self.update_stats()
        self.set_status(f"✓ 已添加新项目")

        # Select the new item
        self.select_item(len(self.items) - 1)

    def refresh_item_list(self):
        """Refresh the sidebar item list"""
        # Clear existing items
        for widget in self.items_scroll.winfo_children():
            widget.destroy()

        # Add item cards
        for idx, item in enumerate(self.items):
            self.create_item_card(idx, item)

    def create_item_card(self, idx, item):
        """Create a modern card for an item"""
        card = ctk.CTkFrame(
            self.items_scroll,
            fg_color=self.colors['bg_tertiary'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border']
        )
        card.pack(fill="x", pady=8)

        # Make card clickable
        card.bind("<Button-1>", lambda e: self.select_item(idx))

        # Card content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Item number badge
        badge = ctk.CTkLabel(
            content,
            text=str(idx + 1),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['accent'],
            width=35,
            height=35,
            fg_color=self.colors['bg_primary'],
            corner_radius=8
        )
        badge.pack(side="left", padx=(0, 12))

        # Item info
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        desc_text = item['description'][:30] + "..." if len(item['description']) > 30 else item['description']
        desc_label = ctk.CTkLabel(
            info_frame,
            text=desc_text,
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        desc_label.pack(anchor="w")

        img_count = len(item.get('images', []))
        count_label = ctk.CTkLabel(
            info_frame,
            text=f"📷 {img_count} 张图片",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        count_label.pack(anchor="w", pady=(2, 0))

        # Delete button
        del_btn = ctk.CTkButton(
            content,
            text="🗑",
            width=35,
            height=35,
            corner_radius=8,
            fg_color=self.colors['bg_primary'],
            hover_color=self.colors['error'],
            command=lambda: self.delete_item(idx)
        )
        del_btn.pack(side="right")

    def select_item(self, idx):
        """Select an item and display its images"""
        if 0 <= idx < len(self.items):
            self.selected_item_index = idx
            item = self.items[idx]

            # Update description
            self.description_entry.delete(0, "end")
            self.description_entry.insert(0, item['description'])

            # Display images
            self.display_item_images(idx)

            # Update card highlights
            self.refresh_item_list()

    def delete_item(self, idx):
        """Delete an item"""
        if 0 <= idx < len(self.items):
            if messagebox.askyesno("确认删除", f"确定要删除项目 {idx + 1} 吗？"):
                del self.items[idx]
                self.refresh_item_list()
                self.update_stats()
                self.clear_image_display()
                self.set_status(f"✓ 已删除项目")

    def on_description_change(self, event):
        """Handle description text change"""
        if self.selected_item_index is not None and 0 <= self.selected_item_index < len(self.items):
            new_desc = self.description_entry.get().strip()
            self.items[self.selected_item_index]['description'] = new_desc if new_desc else f"维修项目 {self.selected_item_index + 1}"
            self.refresh_item_list()

    def add_images(self):
        """Add images to selected item"""
        if self.selected_item_index is None:
            messagebox.showwarning("提示", "请先选择一个项目")
            return

        file_paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("所有文件", "*.*")
            ]
        )

        if file_paths:
            item = self.items[self.selected_item_index]
            added = 0
            for path in file_paths:
                if path not in item['images']:
                    item['images'].append(path)
                    added += 1

            self.refresh_item_list()
            self.display_item_images(self.selected_item_index)
            self.update_stats()
            self.set_status(f"✓ 已添加 {added} 张图片")

    def batch_add_images(self):
        """Batch add images with assignment dialog"""
        if not self.items:
            if messagebox.askyesno("提示", "当前没有项目\n是否创建新项目？"):
                self.add_item()
            else:
                return

        file_paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("所有文件", "*.*")
            ]
        )

        if file_paths:
            self.show_batch_assign_dialog(list(file_paths))

    def show_batch_assign_dialog(self, file_paths):
        """Show dialog to assign multiple images to items"""
        # Simple implementation: assign all to selected item
        if self.selected_item_index is not None:
            item = self.items[self.selected_item_index]
            added = 0
            for path in file_paths:
                if path not in item['images']:
                    item['images'].append(path)
                    added += 1

            self.refresh_item_list()
            self.display_item_images(self.selected_item_index)
            self.update_stats()
            messagebox.showinfo("完成", f"已添加 {added} 张图片到当前项目")
        else:
            messagebox.showwarning("提示", "请先选择一个项目")

    def display_item_images(self, idx):
        """Display images for selected item"""
        if not (0 <= idx < len(self.items)):
            return

        self.clear_image_display()

        images = self.items[idx].get('images', [])
        if not images:
            # Show drop zone
            return

        # Hide drop zone, show images
        self.drop_zone.pack_forget()

        # Display images in grid
        for img_idx, img_path in enumerate(images):
            row = img_idx // 4
            col = img_idx % 4

            img_card = self.create_image_card(img_path, idx)
            img_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def create_image_card(self, img_path, item_idx):
        """Create a modern card for an image"""
        card = ctk.CTkFrame(
            self.image_gallery,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15,
            border_width=2,
            border_color=self.colors['border']
        )

        try:
            # Load and display image
            with Image.open(img_path) as img:
                # Create thumbnail
                img.thumbnail((250, 250), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # Image label
                img_label = ctk.CTkLabel(
                    card,
                    text="",
                    image=photo
                )
                img_label.image = photo  # Keep reference
                img_label.pack(padx=10, pady=10)

            # Image info
            filename = os.path.basename(img_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."

            info_frame = ctk.CTkFrame(card, fg_color=self.colors['bg_tertiary'])
            info_frame.pack(fill="x", padx=10, pady=(0, 10))

            ctk.CTkLabel(
                info_frame,
                text=filename,
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_secondary']
            ).pack(pady=8)

            # Delete button
            del_btn = ctk.CTkButton(
                card,
                text="删除",
                height=28,
                corner_radius=8,
                fg_color=self.colors['error'],
                hover_color="#C62828",
                command=lambda: self.delete_image(img_path, item_idx)
            )
            del_btn.pack(padx=10, pady=(0, 10))

        except Exception as e:
            ctk.CTkLabel(
                card,
                text=f"无法加载图片\n{str(e)[:30]}",
                text_color=self.colors['error']
            ).pack(pady=20)

        return card

    def delete_image(self, img_path, item_idx):
        """Delete an image from an item"""
        if 0 <= item_idx < len(self.items):
            item = self.items[item_idx]
            if img_path in item['images']:
                if messagebox.askyesno("确认删除", f"确定要删除这张图片吗？\n{os.path.basename(img_path)}"):
                    item['images'].remove(img_path)
                    self.refresh_item_list()
                    self.display_item_images(item_idx)
                    self.update_stats()
                    self.set_status("✓ 已删除图片")

    def clear_image_display(self):
        """Clear image gallery"""
        for widget in self.image_gallery.winfo_children():
            if widget != self.drop_zone:
                widget.destroy()

        # Show drop zone again
        if not self.drop_zone.winfo_viewable():
            self.drop_zone.pack(fill="both", expand=True, padx=20, pady=50)

    def update_stats(self):
        """Update statistics display"""
        total_items = len(self.items)
        total_images = sum(len(item.get('images', [])) for item in self.items)

        self.stats_label.configure(text=f"{total_items} 项目 • {total_images} 图片")

        # Update max images per row
        if self.items:
            self.max_images_per_row = max(len(item.get('images', [])) for item in self.items) or 1

    def set_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=message)
        self.update_idletasks()

    def show_settings(self):
        """Show settings dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("设置")
        dialog.geometry("500x400")
        dialog.transient(self)

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text="⚙️ 设置",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)

        # Appearance mode
        ctk.CTkLabel(
            dialog,
            text="外观模式",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(20, 5))

        appearance_var = ctk.StringVar(value=ctk.get_appearance_mode())
        ctk.CTkOptionMenu(
            dialog,
            variable=appearance_var,
            values=["Dark", "Light", "System"],
            command=lambda mode: ctk.set_appearance_mode(mode)
        ).pack(pady=5)

        # About info
        ctk.CTkLabel(
            dialog,
            text=f"\n系统: {platform.system()}\nPython: {sys.version_info.major}.{sys.version_info.minor}\n拖拽: {'✓' if DRAG_DROP_AVAILABLE else '✗'}\nExcel: {'✓' if EXCEL_AVAILABLE else '✗'}\nPDF: {'✓' if PDF_AVAILABLE else '✗'}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        ).pack(pady=20)

        ctk.CTkButton(
            dialog,
            text="关闭",
            command=dialog.destroy,
            height=40,
            corner_radius=10
        ).pack(pady=20)

    def save_project(self):
        """Save project to JSON file"""
        path = filedialog.asksaveasfilename(
            title="保存项目文件",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if path:
            try:
                data = {
                    'title': self.project_title_var.get(),
                    'items': self.items,
                    'created_time': datetime.now().isoformat(),
                    'max_images_per_row': self.max_images_per_row,
                    'version': '2.0.0'
                }

                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                self.set_status(f"✓ 项目已保存: {os.path.basename(path)}")
                messagebox.showinfo("成功", "项目保存成功！")

            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
                self.set_status("✗ 保存失败")

    def open_project(self):
        """Open project from JSON file"""
        path = filedialog.askopenfilename(
            title="打开项目文件",
            filetypes=[("JSON files", "*.json")]
        )

        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.project_title_var.set(data.get('title', ''))
                self.items = data.get('items', [])
                self.max_images_per_row = data.get('max_images_per_row', 1)
                self.current_item_id = max((item.get('id', 0) for item in self.items), default=0)

                self.refresh_item_list()
                self.clear_image_display()
                self.update_stats()

                self.set_status(f"✓ 项目已加载: {os.path.basename(path)}")
                messagebox.showinfo("成功", "项目加载成功！")

            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {str(e)}")
                self.set_status("✗ 加载失败")

    def export_excel(self):
        """Export to Excel (reuse original implementation)"""
        if not EXCEL_AVAILABLE:
            messagebox.showerror("错误", "Excel导出功能需要安装openpyxl库\n请运行: pip install openpyxl")
            return

        if not self.items:
            messagebox.showwarning("警告", "没有数据可导出")
            return

        title = self.project_title_var.get().strip()
        if not title:
            if not messagebox.askyesno("标题提醒", "您还没有设置项目标题！\n是否使用默认标题'维修检查报告'继续导出？"):
                return

        path = filedialog.asksaveasfilename(
            title="保存Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if path:
            self.set_status("正在导出Excel...")
            # Use threading to prevent UI freeze
            thread = threading.Thread(target=self._export_excel_file, args=(path,))
            thread.start()

    def _export_excel_file(self, file_path):
        """Export to Excel file (original implementation)"""
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "维修报告"

            title = self.project_title_var.get() or "维修检查报告"

            # Title
            title_cell = ws['A1']
            title_cell.value = title
            title_cell.font = Font(size=20, bold=True, name='微软雅黑')
            title_cell.alignment = Alignment(horizontal='center', vertical='center')

            # Subtitle
            subtitle_cell = ws['A2']
            subtitle_cell.value = f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}"
            subtitle_cell.font = Font(size=11, italic=True, name='微软雅黑')
            subtitle_cell.alignment = Alignment(horizontal='center')

            total_cols = 2 + self.max_images_per_row
            end_col = chr(64 + total_cols)
            ws.merge_cells(f'A1:{end_col}1')
            ws.merge_cells(f'A2:{end_col}2')

            # Headers
            headers = ['序号', '维修内容描述'] + [f'图片{i+1}' for i in range(self.max_images_per_row)]
            for col, header in enumerate(headers, 1):
                c = ws.cell(row=4, column=col)
                c.value = header
                c.font = Font(bold=True, name='微软雅黑')
                c.alignment = Alignment(horizontal='center', vertical='center')
                c.fill = PatternFill(start_color="E6E6FA", end_color="E6E6FA", fill_type="solid")

            # Data rows
            temp_files = []
            for row_idx, item in enumerate(self.items, 5):
                ws.cell(row=row_idx, column=1).value = row_idx - 4
                ws.cell(row=row_idx, column=1).alignment = Alignment(horizontal='center', vertical='center')

                desc_cell = ws.cell(row=row_idx, column=2)
                desc_cell.value = item['description']
                desc_cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                desc_cell.font = Font(name='微软雅黑')

                images = item.get('images', [])
                row_max_height = 40

                for img_idx, img_path in enumerate(images[:self.max_images_per_row]):
                    col = 3 + img_idx
                    try:
                        if not os.path.exists(img_path):
                            ws.cell(row=row_idx, column=col).value = f"图片文件不存在:\n{os.path.basename(img_path)}"
                            continue

                        with Image.open(img_path) as img:
                            target_w, target_h = 1200, 900
                            r = img.width / img.height
                            if r > target_w/target_h:
                                new_w, new_h = target_w, int(target_w / r)
                            else:
                                new_h, new_w = target_h, int(target_h * r)

                            processed = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            tpath = os.path.join(tempfile.gettempdir(), f"excel_img_{uuid.uuid4().hex}.png")
                            processed.save(tpath, 'PNG')

                        temp_files.append(tpath)
                        excel_img = xl_image.Image(tpath)
                        scale = 0.32
                        excel_img.width = new_w * scale
                        excel_img.height = new_h * scale
                        ws.add_image(excel_img, f'{chr(64 + col)}{row_idx}')
                        row_max_height = max(row_max_height, new_h * scale * 0.8)

                    except Exception as e:
                        ws.cell(row=row_idx, column=col).value = f"图片处理失败:\n{os.path.basename(img_path)}"

                ws.row_dimensions[row_idx].height = row_max_height

            # Column widths
            ws.column_dimensions['A'].width = 8
            ws.column_dimensions['B'].width = 45
            for i in range(self.max_images_per_row):
                ws.column_dimensions[chr(67+i)].width = 52

            # Borders
            thin = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))
            for row in range(4, len(self.items)+5):
                for col in range(1, total_cols+1):
                    ws.cell(row=row, column=col).border = thin

            wb.save(file_path)

            # Cleanup temp files after delay
            self.after(5000, lambda: self._cleanup_temp_files(temp_files))

            self.set_status(f"✓ Excel文件已保存: {os.path.basename(file_path)}")
            messagebox.showinfo("成功", f"Excel文件已保存到:\n{file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"导出Excel失败: {str(e)}")
            self.set_status("✗ Excel导出失败")

    def export_pdf(self):
        """Export to PDF (reuse original implementation)"""
        if not PDF_AVAILABLE:
            messagebox.showerror("错误", "PDF导出功能需要安装reportlab库\n请运行: pip install reportlab")
            return

        if not self.items:
            messagebox.showwarning("警告", "没有数据可导出")
            return

        title = self.project_title_var.get().strip()
        if not title:
            if not messagebox.askyesno("标题提醒", "您还没有设置项目标题！\n是否使用默认标题'维修检查报告'继续导出？"):
                return

        path = filedialog.asksaveasfilename(
            title="保存PDF文件",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if path:
            self.set_status("正在导出PDF...")
            thread = threading.Thread(target=self._export_pdf_file, args=(path,))
            thread.start()

    def _export_pdf_file(self, file_path):
        """Export to PDF file (original implementation)"""
        try:
            self._setup_chinese_fonts()

            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                topMargin=20*mm,
                bottomMargin=20*mm,
                leftMargin=15*mm,
                rightMargin=15*mm
            )

            story = []
            styles = getSampleStyleSheet()

            try:
                chinese = ParagraphStyle(
                    'Chinese',
                    parent=styles['Normal'],
                    fontName='Chinese',
                    fontSize=10,
                    leading=12,
                    wordWrap='CJK'
                )
                title_style = ParagraphStyle(
                    'ChineseTitle',
                    parent=styles['Heading1'],
                    fontName='Chinese',
                    fontSize=20,
                    spaceAfter=20,
                    alignment=TA_CENTER,
                    leading=24
                )
                subtitle_style = ParagraphStyle(
                    'Subtitle',
                    parent=chinese,
                    fontSize=11,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#666666')
                )
            except:
                chinese = styles['Normal']
                title_style = styles['Heading1']
                subtitle_style = styles['Normal']

            title = self.project_title_var.get() or "维修检查报告"
            story.append(Paragraph(title, title_style))
            story.append(Paragraph(
                f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
                subtitle_style
            ))
            story.append(Spacer(1, 30))

            # Add items
            temp_files = []
            for idx, item in enumerate(self.items):
                title_para = Paragraph(
                    f"{idx+1}. {item['description']}",
                    ParagraphStyle(
                        'ItemTitle',
                        parent=chinese,
                        fontSize=12,
                        fontName='Chinese',
                        spaceBefore=10,
                        spaceAfter=10,
                        leftIndent=0,
                        leading=14
                    )
                )
                story.append(title_para)

                images = item.get('images', [])
                if images:
                    img_element = self._create_pdf_images(images, temp_files)
                    if img_element:
                        story.append(img_element)
                    else:
                        story.append(Paragraph("图片加载失败", chinese))
                else:
                    story.append(Paragraph("暂无图片", chinese))

                if idx < len(self.items) - 1:
                    story.append(Spacer(1, 20))

            doc.build(story)

            # Cleanup
            self.after(5000, lambda: self._cleanup_temp_files(temp_files))

            self.set_status(f"✓ PDF文件已保存: {os.path.basename(file_path)}")
            messagebox.showinfo("成功", f"PDF文件已保存到:\n{file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"导出PDF失败: {str(e)}")
            self.set_status("✗ PDF导出失败")

    def _setup_chinese_fonts(self):
        """Setup Chinese fonts for PDF"""
        try:
            system = platform.system()
            if system == "Windows":
                paths = ["C:/Windows/Fonts/simsun.ttc", "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc"]
            elif system == "Darwin":
                paths = ["/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/PingFang.ttc"]
            else:
                paths = ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"]

            for p in paths:
                if os.path.exists(p):
                    pdfmetrics.registerFont(TTFont('Chinese', p))
                    return

            pdfmetrics.registerFont(TTFont('Chinese', 'Helvetica'))
        except:
            pass

    def _create_pdf_images(self, images, temp_files):
        """Create PDF image layout"""
        try:
            if len(images) == 1:
                p = images[0]
                if os.path.exists(p):
                    t = self._process_pdf_image(p, temp_files, 150*mm, 100*mm)
                    if t:
                        img = RL_Image(t, width=150*mm, height=100*mm, kind='proportional')
                        table = Table([[img]], colWidths=[170*mm])
                        table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
                        return table
            else:
                cols = 2 if len(images) <= 4 else 3
                rows, row = [], []
                for i, p in enumerate(images):
                    if os.path.exists(p):
                        size = 70*mm if cols==2 else 50*mm
                        t = self._process_pdf_image(p, temp_files, size, size)
                        row.append(RL_Image(t, width=size, height=size, kind='proportional') if t else "")
                    else:
                        row.append("")

                    if len(row) >= cols or i == len(images)-1:
                        while len(row) < cols:
                            row.append("")
                        rows.append(row)
                        row = []

                if rows:
                    col_w = 85*mm if cols==2 else 56*mm
                    table = Table(rows, colWidths=[col_w]*cols)
                    table.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('LEFTPADDING', (0,0), (-1,-1), 5),
                        ('RIGHTPADDING', (0,0), (-1,-1), 5),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ]))
                    return table
        except:
            pass
        return None

    def _process_pdf_image(self, img_path, temp_files, max_width, max_height):
        """Process image for PDF"""
        try:
            with Image.open(img_path) as img:
                max_w_px, max_h_px = int(max_width*10), int(max_height*10)
                r = img.width / img.height
                if img.width/max_w_px > img.height/max_h_px:
                    new_w, new_h = max_w_px, int(max_w_px / r)
                else:
                    new_h, new_w = max_h_px, int(max_h_px * r)

                resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                if resized.mode != 'RGB':
                    resized = resized.convert('RGB')

                t = os.path.join(tempfile.gettempdir(), f"pdf_img_{uuid.uuid4().hex}.jpg")
                resized.save(t, 'JPEG', quality=92)
                temp_files.append(t)
                return t
        except:
            return None

    def _cleanup_temp_files(self, files):
        """Cleanup temporary files"""
        for f in files:
            try:
                if os.path.exists(f):
                    os.unlink(f)
            except:
                pass


def main():
    """Main entry point"""
    print("="*60)
    print("🚀 启动维修单工具 Modern Edition v2.0")
    print("="*60)
    print(f"系统: {platform.system()}")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}")
    print(f"拖拽: {'✓' if DRAG_DROP_AVAILABLE else '✗'}")
    print(f"Excel: {'✓' if EXCEL_AVAILABLE else '✗'}")
    print(f"PDF: {'✓' if PDF_AVAILABLE else '✗'}")
    print("="*60)

    # Check for CustomTkinter
    try:
        import customtkinter
        print("✓ CustomTkinter 已加载")
    except ImportError:
        print("✗ CustomTkinter 未安装")
        print("\n请安装 CustomTkinter:")
        print("  pip install customtkinter")
        return

    # Launch app
    try:
        app = ModernRepairTool()
        app.mainloop()
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
