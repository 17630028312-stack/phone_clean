"""
手机相册整理App - 划一下
iOS 风格设计：简洁、圆角、毛玻璃效果
"""

import os
import random
import sqlite3
from datetime import datetime
from functools import partial

from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.core.image import Image as CoreImage

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton, MDRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.textinput import TextInput
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, OneLineAvatarIconListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.fitimage import FitImage
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.gridlayout import MDGridLayout

# ============== 中文字体配置 ==============
from kivy.core.text import LabelBase

def get_chinese_font():
    """获取可用的中文字体路径"""
    windows_fonts = [
        'C:/Windows/Fonts/msyh.ttc',      # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',    # 黑体
        'C:/Windows/Fonts/simsun.ttc',    # 宋体
    ]
    
    for font in windows_fonts:
        if os.path.exists(font):
            return font
    return None

chinese_font = get_chinese_font()
if chinese_font:
    LabelBase.register(name='Chinese', fn_regular=chinese_font)
    LabelBase.register(name='Roboto', fn_regular=chinese_font)

# ============== iOS 颜色配置 ==============
IOS_COLORS = {
    'background': (0.97, 0.97, 0.98, 1),      # 浅灰背景
    'card': (1, 1, 1, 1),                      # 白色卡片
    'primary': (0.0, 0.48, 1.0, 1),           # iOS 蓝
    'secondary': (0.56, 0.56, 0.58, 1),       # 灰色
    'success': (0.2, 0.8, 0.4, 1),            # 绿色
    'danger': (1.0, 0.23, 0.19, 1),           # 红色
    'warning': (1.0, 0.58, 0.0, 1),           # 橙色
    'text': (0, 0, 0, 1),                     # 黑色文字
    'text_secondary': (0.55, 0.55, 0.55, 1),  # 灰色文字
}

# ============== 数据库管理 ==============
class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'app_data.db')
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 照片状态表 - 添加收藏状态
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photo_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_path TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'pending',
                is_favorite INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 历史记录表 - 添加收藏统计
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                photos_count INTEGER DEFAULT 0,
                kept_count INTEGER DEFAULT 0,
                deleted_count INTEGER DEFAULT 0,
                skipped_count INTEGER DEFAULT 0,
                favorite_count INTEGER DEFAULT 0,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, username, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def login_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id FROM users WHERE username = ? AND password = ?',
            (username, password)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_pending_photos(self, limit=10):
        """获取待处理的照片（不包括已收藏和已处理的）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT photo_path FROM photo_status WHERE status = ? AND is_favorite = 0 LIMIT ?',
            ('pending', limit)
        )
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
    
    def update_photo_status(self, photo_path, status):
        """更新照片状态: kept(保留), deleted(删除), skipped(跳过), favorite(收藏)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE photo_status SET status = ? WHERE photo_path = ?',
            (status, photo_path)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                'INSERT INTO photo_status (photo_path, status) VALUES (?, ?)',
                (photo_path, status)
            )
        conn.commit()
        conn.close()
    
    def mark_as_favorite(self, photo_path):
        """标记照片为收藏"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE photo_status SET is_favorite = 1, status = ? WHERE photo_path = ?',
            ('favorite', photo_path)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                'INSERT INTO photo_status (photo_path, status, is_favorite) VALUES (?, ?, 1)',
                (photo_path, 'favorite')
            )
        conn.commit()
        conn.close()
    
    def get_favorite_count(self):
        """获取收藏照片数量"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM photo_status WHERE is_favorite = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def sync_photos_from_album(self, photo_paths):
        """同步相册照片到数据库 - 保留收藏状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        for path in photo_paths:
            # 检查是否已存在且已收藏
            cursor.execute('SELECT is_favorite FROM photo_status WHERE photo_path = ?', (path,))
            result = cursor.fetchone()
            
            if result:
                # 已存在，保留收藏状态
                is_fav = result[0]
                if is_fav:
                    continue  # 已收藏，不重置状态
                # 未收藏，更新状态为 pending
                cursor.execute(
                    'UPDATE photo_status SET status = ? WHERE photo_path = ?',
                    ('pending', path)
                )
            else:
                # 新照片
                cursor.execute(
                    'INSERT INTO photo_status (photo_path, status, is_favorite) VALUES (?, ?, 0)',
                    (path, 'pending')
                )
        conn.commit()
        conn.close()
    
    def get_pending_count(self):
        """获取待处理照片数量（不包括已收藏的）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM photo_status WHERE status = ? AND is_favorite = 0', ('pending',))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_total_count(self):
        """获取所有照片总数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM photo_status')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def add_history(self, user_id, photos_count, kept_count, deleted_count, skipped_count, favorite_count=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO history (user_id, photos_count, kept_count, deleted_count, skipped_count, favorite_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, photos_count, kept_count, deleted_count, skipped_count, favorite_count))
        conn.commit()
        conn.close()
    
    def get_history(self, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if user_id:
            cursor.execute('''
                SELECT * FROM history WHERE user_id = ? 
                ORDER BY completed_at DESC
            ''', (user_id,))
        else:
            cursor.execute('SELECT * FROM history ORDER BY completed_at DESC')
        results = cursor.fetchall()
        conn.close()
        return results


# ============== 相册管理器 ==============
class AlbumManager:
    def __init__(self):
        self.photos = []
        self.db = DatabaseManager()
    
    def scan_album(self):
        """扫描相册获取照片"""
        photo_paths = []
        
        try:
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path
            IS_ANDROID = True
        except ImportError:
            IS_ANDROID = False
        
        if IS_ANDROID:
            storage_path = primary_external_storage_path()
            dcim_path = os.path.join(storage_path, 'DCIM')
            pictures_path = os.path.join(storage_path, 'Pictures')
            
            for path in [dcim_path, pictures_path]:
                if os.path.exists(path):
                    photo_paths.extend(self._scan_directory(path))
        else:
            import tempfile
            test_dirs = [
                os.path.expanduser("~/Pictures"),
                os.path.expanduser("~/Desktop"),
                tempfile.gettempdir(),
            ]
            for d in test_dirs:
                if os.path.exists(d):
                    photo_paths.extend(self._scan_directory(d))
        
        photo_paths = list(set(photo_paths))
        self.db.sync_photos_from_album(photo_paths)
        self.photos = photo_paths
        return photo_paths
    
    def _scan_directory(self, path, extensions=('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
        photos = []
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(extensions):
                        photos.append(os.path.join(root, file))
        except Exception as e:
            print(f"扫描目录错误: {e}")
        return photos
    
    def get_random_batch(self, batch_size=10):
        pending = self.db.get_pending_photos(limit=100)
        if not pending:
            return []
        batch = random.sample(pending, min(batch_size, len(pending)))
        return batch


# ============== iOS 风格组件 ==============
class IOSCard(MDCard):
    """iOS 风格卡片"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = IOS_COLORS['card']
        self.radius = [dp(16), dp(16), dp(16), dp(16)]
        self.elevation = 2
        self.shadow_softness = 0.5


class IOSButton(MDFlatButton):
    """iOS 风格按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = IOS_COLORS['primary']
        self.text_color = (1, 1, 1, 1)
        self.radius = [dp(10), dp(10), dp(10), dp(10)]
        self.font_size = dp(16)


class IOSLabel(MDLabel):
    """iOS 风格标签"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_style = 'Body1'
        self.theme_text_color = 'Custom'
        self.text_color = IOS_COLORS['text']


class GestureHint(MDBoxLayout):
    """手势提示组件（小图标 + 文字）"""
    def __init__(self, icon_source, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'  # 水平排列
        self.size_hint = (1, None)
        self.height = dp(36)  # 整体高度
        self.spacing = dp(8)
        
        # 小图标
        self.icon = FitImage(
            source=icon_source,
            size_hint=(None, None),
            size=(dp(28), dp(28)),  # 小尺寸图标
            radius=[dp(6), dp(6), dp(6), dp(6)],
            pos_hint={'center_y': 0.5}
        )
        self.add_widget(self.icon)
        
        # 文字
        self.label = IOSLabel(
            text=text,
            halign='left',
            font_size=dp(13),
            text_color=IOS_COLORS['text_secondary'],
            pos_hint={'center_y': 0.5}
        )
        self.add_widget(self.label)


class PhotoCard(MDRelativeLayout):
    """iOS 风格照片卡片"""
    photo_path = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.85, None)
        self.height = dp(450)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        # iOS 风格圆角阴影卡片
        self.card = MDCard(
            radius=[dp(20), dp(20), dp(20), dp(20)],
            elevation=8,
            shadow_softness=0.8,
            shadow_offset=(0, dp(4)),
            size_hint=(1, 1)
        )
        
        # 图片
        self.image = FitImage(
            source=self.photo_path if self.photo_path else '',
            radius=[dp(20), dp(20), dp(20), dp(20)],
            size_hint=(1, 1)
        )
        self.card.add_widget(self.image)
        self.add_widget(self.card)
        
        self._touch_start_x = 0
        self._touch_start_y = 0
        self._is_dragging = False
    
    def on_photo_path(self, instance, value):
        if hasattr(self, 'image'):
            self.image.source = value
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start_x = touch.x
            self._touch_start_y = touch.y
            self._is_dragging = True
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self._is_dragging:
            dx = touch.x - self._touch_start_x
            dy = touch.y - self._touch_start_y
            
            # iOS 弹性跟随效果
            self.x = self.parent.x + self.parent.width * 0.075 + dx * 0.8
            self.y = self.parent.y + self.parent.height * 0.5 - self.height * 0.5 + dy * 0.8
            
            # 根据滑动方向旋转（iOS 卡片效果）
            rotation = dx * 0.03
            self.rotation = max(-15, min(15, rotation))
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self._is_dragging:
            self._is_dragging = False
            dx = touch.x - self._touch_start_x
            dy = touch.y - self._touch_start_y
            
            threshold = dp(100)
            vertical_threshold = dp(80)
            
            if abs(dx) > threshold:
                # 水平滑动 - 左滑删除，右滑保留
                direction = 'left' if dx < 0 else 'right'
                self._animate_swipe(direction)
            elif dy > vertical_threshold:
                # 上滑 - 暂不处理
                self._animate_swipe('up')
            elif dy < -vertical_threshold:
                # 下滑 - 收藏
                self._animate_swipe('down')
            else:
                self._animate_reset()
            
            return True
        return super().on_touch_up(touch)
    
    def _animate_swipe(self, direction):
        app = MDApp.get_running_app()
        
        if direction == 'left':
            anim = Animation(x=-Window.width, rotation=-20, duration=0.25, transition='out_quad')
            anim.bind(on_complete=lambda *args: app.on_photo_action(self.photo_path, 'deleted'))
        elif direction == 'right':
            anim = Animation(x=Window.width, rotation=20, duration=0.25, transition='out_quad')
            anim.bind(on_complete=lambda *args: app.on_photo_action(self.photo_path, 'kept'))
        elif direction == 'up':
            anim = Animation(y=Window.height, rotation=0, duration=0.25, transition='out_quad')
            anim.bind(on_complete=lambda *args: app.on_photo_action(self.photo_path, 'skipped'))
        else:  # down - 收藏
            anim = Animation(y=-Window.height, rotation=0, duration=0.25, transition='out_quad')
            anim.bind(on_complete=lambda *args: app.on_photo_action(self.photo_path, 'favorite'))
        
        anim.start(self)
    
    def _animate_reset(self):
        """iOS 弹性回弹效果"""
        anim = Animation(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            rotation=0,
            duration=0.3,
            transition='out_elastic'
        )
        anim.start(self)


# ============== 屏幕定义 ==============
class SwipeScreen(MDScreen):
    """划一下主屏幕 - iOS 风格"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'swipe'
        self.current_batch = []
        self.current_index = 0
        self.batch_stats = {'kept': 0, 'deleted': 0, 'skipped': 0}
        self.db = DatabaseManager()
        self.album = AlbumManager()
        
        self.md_bg_color = IOS_COLORS['background']
        
        # 主布局
        self.layout = MDBoxLayout(orientation='vertical')
        
        # === iOS 风格顶部状态栏（居中） ===
        self.header_container = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(120),
            padding=[dp(16), dp(10)]
        )
        
        self.header = MDBoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=dp(360),  # 固定宽度居中
            pos_hint={'center_x': 0.5}
        )
        
        # 标题
        self.title_label = IOSLabel(
            text="划一下",
            font_size=dp(28),
            bold=True,
            halign='left',
            size_hint=(1, None),
            height=dp(40)
        )
        self.header.add_widget(self.title_label)
        
        # 相册统计信息 - iOS 风格卡片（添加收藏统计）
        self.stats_card = IOSCard(
            size_hint=(1, None),
            height=dp(70),
            padding=[dp(12), dp(10)],
            radius=[dp(12), dp(12), dp(12), dp(12)]
        )
        
        stats_layout = MDGridLayout(cols=3, spacing=dp(10))
        
        # 总照片数
        self.total_label = IOSLabel(
            text="相册\n0",
            font_size=dp(13),
            text_color=IOS_COLORS['text_secondary'],
            halign='center'
        )
        stats_layout.add_widget(self.total_label)
        
        # 待整理数
        self.pending_label = IOSLabel(
            text="待整理\n0",
            font_size=dp(13),
            text_color=IOS_COLORS['primary'],
            halign='center'
        )
        stats_layout.add_widget(self.pending_label)
        
        # 收藏数（新增）
        self.favorite_label = IOSLabel(
            text="收藏\n0",
            font_size=dp(13),
            text_color=IOS_COLORS['warning'],
            halign='center'
        )
        stats_layout.add_widget(self.favorite_label)
        
        self.stats_card.add_widget(stats_layout)
        self.header.add_widget(self.stats_card)
        
        # 组装层次结构：header -> header_container -> layout
        self.header_container.add_widget(self.header)
        self.layout.add_widget(self.header_container)
        
        # === 照片卡片区域 ===
        self.card_container = MDFloatLayout(
            size_hint=(1, 0.65)
        )
        self.layout.add_widget(self.card_container)
        
        # === iOS 风格手势提示区 - 2x2 网格（小图标+文字） ===
        self.gesture_container = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(90),
            padding=[dp(20), dp(10)]
        )
        
        # 居中包装器
        self.gesture_wrapper = MDBoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            width=dp(300),  # 固定宽度居中
            pos_hint={'center_x': 0.5}
        )
        
        self.gesture_layout = MDGridLayout(
            cols=2,
            size_hint=(1, 1),
            spacing=[dp(30), dp(8)]  # 列间距和行间距
        )
        
        # 获取图标路径
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        
        # 左滑删除
        self.delete_hint = GestureHint(
            os.path.join(assets_dir, 'icon_delete.png'),
            "左滑删除"
        )
        self.gesture_layout.add_widget(self.delete_hint)
        
        # 右滑保留
        self.keep_hint = GestureHint(
            os.path.join(assets_dir, 'icon_keep.png'),
            "右滑保留"
        )
        self.gesture_layout.add_widget(self.keep_hint)
        
        # 上滑跳过
        self.skip_hint = GestureHint(
            os.path.join(assets_dir, 'icon_skip.png'),
            "上滑跳过"
        )
        self.gesture_layout.add_widget(self.skip_hint)
        
        # 下滑收藏（新增）
        self.favorite_hint = GestureHint(
            os.path.join(assets_dir, 'icon_favorite.png'),
            "下滑收藏"
        )
        self.gesture_layout.add_widget(self.favorite_hint)
        
        # 组装层次结构：gesture_layout -> wrapper -> container -> layout
        self.gesture_wrapper.add_widget(self.gesture_layout)
        self.gesture_container.add_widget(self.gesture_wrapper)
        self.layout.add_widget(self.gesture_container)
        
        # === 底部按钮区（居中） ===
        self.button_container = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(80),
            padding=[dp(20), dp(15)]
        )
        
        self.button_wrapper = MDBoxLayout(
            size_hint=(None, 1),
            width=dp(320),  # 固定宽度居中
            pos_hint={'center_x': 0.5}
        )
        
        # iOS 风格大按钮
        self.start_btn = MDRaisedButton(
            text="开始整理",
            size_hint=(1, 1),
            md_bg_color=IOS_COLORS['primary'],
            text_color=(1, 1, 1, 1),
            font_size=dp(17),
            on_release=self.start_new_batch
        )
        self.button_wrapper.add_widget(self.start_btn)
        self.button_container.add_widget(self.button_wrapper)
        self.layout.add_widget(self.button_container)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_stats()
    
    def load_stats(self):
        """加载相册统计"""
        total = self.db.get_total_count()
        pending = self.db.get_pending_count()
        favorite = self.db.get_favorite_count()
        
        self.total_label.text = f"相册\n{total}"
        self.pending_label.text = f"待整理\n{pending}"
        self.favorite_label.text = f"收藏\n{favorite}"
        
        if pending == 0:
            self.start_btn.text = "暂无待整理照片"
            self.start_btn.disabled = True
            self.start_btn.md_bg_color = IOS_COLORS['secondary']
        else:
            self.start_btn.text = "开始整理"
            self.start_btn.disabled = False
            self.start_btn.md_bg_color = IOS_COLORS['primary']
    
    def start_new_batch(self, *args):
        """开始新的一批"""
        self.current_batch = self.album.get_random_batch(10)
        self.current_index = 0
        self.batch_stats = {'kept': 0, 'deleted': 0, 'skipped': 0, 'favorite': 0}
        
        if not self.current_batch:
            return
        
        # 隐藏按钮，显示卡片
        self.start_btn.parent.opacity = 0
        self.show_next_photo()
    
    def show_next_photo(self):
        """显示下一张照片"""
        self.card_container.clear_widgets()
        
        if self.current_index >= len(self.current_batch):
            self._complete_batch()
            return
        
        photo_path = self.current_batch[self.current_index]
        
        # 进度指示器
        progress_text = f"{self.current_index + 1} / {len(self.current_batch)}"
        self.title_label.text = f"划一下  ·  {progress_text}"
        
        # 创建照片卡片
        card = PhotoCard(photo_path=photo_path)
        self.card_container.add_widget(card)
    
    def on_photo_action(self, photo_path, action):
        """处理照片操作"""
        if action == 'favorite':
            # 收藏操作 - 标记为收藏但不改变 pending 状态
            self.db.mark_as_favorite(photo_path)
            # 同时尝试标记系统相册收藏
            self._mark_system_favorite(photo_path)
        else:
            self.db.update_photo_status(photo_path, action)
        
        self.batch_stats[action] += 1
        self.current_index += 1
        
        # 更新统计
        self.load_stats()
        self.show_next_photo()
    
    def _mark_system_favorite(self, photo_path):
        """标记系统相册收藏（Android）"""
        try:
            if 'android' in str(os.sys.platform).lower():
                # Android 平台 - 使用 MediaStore
                from jnius import autoclass
                MediaStore = autoclass('android.provider.MediaStore')
                ContentValues = autoclass('android.content.ContentValues')
                context = autoclass('org.kivy.android.PythonActivity').mActivity
                content_resolver = context.getContentResolver()
                
                # 构建更新值 - 设置 IS_FAVORITE = 1
                values = ContentValues()
                values.put('is_favorite', 1)
                
                # 更新媒体库
                uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
                selection = '_data = ?'
                selection_args = [photo_path]
                
                content_resolver.update(uri, values, selection, selection_args)
                print(f"已标记系统收藏: {photo_path}")
        except Exception as e:
            print(f"标记系统收藏失败: {e}")
    
    def _complete_batch(self):
        """完成一批"""
        app = MDApp.get_running_app()
        user_id = getattr(app, 'current_user_id', None)
        
        self.db.add_history(
            user_id,
            len(self.current_batch),
            self.batch_stats['kept'],
            self.batch_stats['deleted'],
            self.batch_stats['skipped'],
            self.batch_stats['favorite']
        )
        
        # 显示完成提示
        self._show_completion_dialog()
        
        # 重置界面
        self.start_btn.parent.opacity = 1
        self.start_btn.text = "再来一组"
        self.title_label.text = "划一下"
    
    def _show_completion_dialog(self):
        """iOS 风格完成提示"""
        total = sum(self.batch_stats.values())
        kept = self.batch_stats['kept']
        deleted = self.batch_stats['deleted']
        favorite = self.batch_stats['favorite']
        
        encouragements = [
            "太棒了！🎉",
            "整理大师！✨",
            "空间更清爽了！🌟",
            "继续加油！💪",
            "完成！🎊"
        ]
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=dp(200)
        )
        
        content.add_widget(IOSLabel(
            text=random.choice(encouragements),
            font_size=dp(22),
            bold=True,
            halign='center'
        ))
        
        content.add_widget(IOSLabel(
            text=f"本次整理了 {total} 张照片",
            font_size=dp(16),
            halign='center',
            text_color=IOS_COLORS['text_secondary']
        ))
        
        stats_text = f"保留 {kept}  ·  删除 {deleted}  ·  跳过 {self.batch_stats['skipped']}  ·  收藏 {favorite}"
        content.add_widget(IOSLabel(
            text=stats_text,
            font_size=dp(13),
            halign='center',
            text_color=IOS_COLORS['secondary']
        ))
        
        dialog = MDDialog(
            title="",
            type='custom',
            content_cls=content,
            buttons=[
                MDRoundFlatButton(
                    text="继续",
                    text_color=IOS_COLORS['primary'],
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()


class HistoryScreen(MDScreen):
    """历史记录屏幕 - iOS 风格"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'history'
        self.db = DatabaseManager()
        self.md_bg_color = IOS_COLORS['background']
        
        self.layout = MDBoxLayout(orientation='vertical')
        
        # iOS 风格标题栏
        self.header = MDBoxLayout(
            size_hint=(1, None),
            height=dp(70),
            padding=[dp(20), dp(20), dp(20), dp(10)]
        )
        
        self.title = IOSLabel(
            text="历史记录",
            font_size=dp(28),
            bold=True,
            halign='left'
        )
        self.header.add_widget(self.title)
        self.layout.add_widget(self.header)
        
        # 列表容器
        self.scroll = MDScrollView()
        self.list_view = MDList()
        self.scroll.add_widget(self.list_view)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.refresh_history()
    
    def refresh_history(self):
        self.list_view.clear_widgets()
        
        app = MDApp.get_running_app()
        user_id = getattr(app, 'current_user_id', None)
        
        history = self.db.get_history(user_id)
        
        if not history:
            empty_label = IOSLabel(
                text="暂无整理记录",
                halign='center',
                text_color=IOS_COLORS['text_secondary'],
                pos_hint={'center_y': 0.5}
            )
            self.list_view.add_widget(empty_label)
            return
        
        for record in history:
            # 兼容旧数据和新数据结构
            if len(record) == 7:
                record_id, uid, photos_count, kept, deleted, skipped, completed_at = record
                favorite = 0
            else:
                record_id, uid, photos_count, kept, deleted, skipped, favorite, completed_at = record
            
            try:
                dt = datetime.fromisoformat(completed_at)
                time_str = dt.strftime("%Y年%m月%d日 %H:%M")
            except:
                time_str = str(completed_at)
            
            # iOS 风格列表项
            item = IOSCard(
                size_hint=(1, None),
                height=dp(80),
                padding=[dp(16), dp(12)],
                margin=[dp(16), dp(8), dp(16), dp(8)]
            )
            
            item_layout = MDBoxLayout(orientation='vertical')
            
            title = IOSLabel(
                text=time_str,
                font_size=dp(16),
                bold=True
            )
            item_layout.add_widget(title)
            
            subtitle = IOSLabel(
                text=f"{photos_count} 张  ·  保留 {kept}  ·  删除 {deleted}  ·  跳过 {skipped}  ·  收藏 {favorite}",
                font_size=dp(13),
                text_color=IOS_COLORS['text_secondary']
            )
            item_layout.add_widget(subtitle)
            
            item.add_widget(item_layout)
            self.list_view.add_widget(item)


class ProfileScreen(MDScreen):
    """我的屏幕 - iOS 风格"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'profile'
        self.db = DatabaseManager()
        self.md_bg_color = IOS_COLORS['background']
        
        self.layout = MDBoxLayout(orientation='vertical')
        
        # iOS 风格标题栏
        self.header = MDBoxLayout(
            size_hint=(1, None),
            height=dp(70),
            padding=[dp(20), dp(20), dp(20), dp(10)]
        )
        
        self.title = IOSLabel(
            text="我的",
            font_size=dp(28),
            bold=True,
            halign='left'
        )
        self.header.add_widget(self.title)
        self.layout.add_widget(self.header)
        
        # 内容区域
        self.content = MDScrollView()
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(500),
            padding=[dp(20), dp(10)],
            spacing=dp(20)
        )
        
        # 用户信息卡片
        self.user_card = IOSCard(
            size_hint=(1, None),
            height=dp(80),
            padding=dp(16)
        )
        
        self.user_layout = MDBoxLayout(orientation='horizontal')
        
        # 头像占位
        self.avatar = MDCard(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            radius=[dp(24), dp(24), dp(24), dp(24)],
            md_bg_color=IOS_COLORS['primary']
        )
        self.user_layout.add_widget(self.avatar)
        
        self.user_layout.add_widget(MDLabel(size_hint_x=0.05))
        
        self.username_label = IOSLabel(
            text="未登录",
            font_size=dp(18),
            bold=True
        )
        self.user_layout.add_widget(self.username_label)
        
        self.user_card.add_widget(self.user_layout)
        self.content_layout.add_widget(self.user_card)
        
        # 登录表单卡片
        self.form_card = IOSCard(
            size_hint=(1, None),
            height=dp(200),
            padding=[dp(20), dp(16)]
        )
        
        self.form_layout = MDBoxLayout(orientation='vertical', spacing=dp(12))
        
        # iOS 风格输入框
        self.username_input = TextInput(
            hint_text="用户名",
            size_hint=(1, None),
            height=dp(44),
            background_color=(0.97, 0.97, 0.98, 1),
            foreground_color=IOS_COLORS['text'],
            cursor_color=IOS_COLORS['primary'],
            padding=[dp(12), dp(12)],
            font_size=dp(16),
            multiline=False
        )
        self.form_layout.add_widget(self.username_input)
        
        self.password_input = TextInput(
            hint_text="密码",
            password=True,
            size_hint=(1, None),
            height=dp(44),
            background_color=(0.97, 0.97, 0.98, 1),
            foreground_color=IOS_COLORS['text'],
            cursor_color=IOS_COLORS['primary'],
            padding=[dp(12), dp(12)],
            font_size=dp(16),
            multiline=False
        )
        self.form_layout.add_widget(self.password_input)
        
        self.form_card.add_widget(self.form_layout)
        self.content_layout.add_widget(self.form_card)
        
        # 按钮区域
        self.button_card = IOSCard(
            size_hint=(1, None),
            height=dp(120),
            padding=dp(16)
        )
        
        self.button_layout = MDBoxLayout(orientation='vertical', spacing=dp(12))
        
        # iOS 风格主按钮
        self.login_btn = MDRaisedButton(
            text="登录",
            size_hint=(1, None),
            height=dp(48),
            md_bg_color=IOS_COLORS['primary'],
            text_color=(1, 1, 1, 1),
            font_size=dp(17),
            on_release=self.do_login
        )
        self.button_layout.add_widget(self.login_btn)
        
        # iOS 风格次要按钮
        self.register_btn = MDFlatButton(
            text="注册新账号",
            size_hint=(1, None),
            height=dp(44),
            text_color=IOS_COLORS['primary'],
            font_size=dp(16),
            on_release=self.do_register
        )
        self.button_layout.add_widget(self.register_btn)
        
        self.logout_btn = MDFlatButton(
            text="退出登录",
            size_hint=(1, None),
            height=dp(44),
            text_color=IOS_COLORS['danger'],
            font_size=dp(16),
            on_release=self.do_logout,
            opacity=0
        )
        self.button_layout.add_widget(self.logout_btn)
        
        self.button_card.add_widget(self.button_layout)
        self.content_layout.add_widget(self.button_card)
        
        self.content.add_widget(self.content_layout)
        self.layout.add_widget(self.content)
        
        self.add_widget(self.layout)
        self._update_ui()
    
    def _update_ui(self):
        app = MDApp.get_running_app()
        is_logged_in = getattr(app, 'current_user_id', None) is not None
        
        if is_logged_in:
            self.username_label.text = getattr(app, 'current_username', '用户')
            self.form_card.opacity = 0
            self.form_card.height = 0
            self.login_btn.opacity = 0
            self.login_btn.disabled = True
            self.register_btn.opacity = 0
            self.register_btn.disabled = True
            self.logout_btn.opacity = 1
            self.logout_btn.disabled = False
        else:
            self.username_label.text = "未登录"
            self.form_card.opacity = 1
            self.form_card.height = dp(200)
            self.login_btn.opacity = 1
            self.login_btn.disabled = False
            self.register_btn.opacity = 1
            self.register_btn.disabled = False
            self.logout_btn.opacity = 0
            self.logout_btn.disabled = True
    
    def on_enter(self):
        self._update_ui()
    
    def do_login(self, *args):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self._show_snackbar("请输入用户名和密码")
            return
        
        user_id = self.db.login_user(username, password)
        if user_id:
            app = MDApp.get_running_app()
            app.current_user_id = user_id
            app.current_username = username
            self._show_snackbar(f"欢迎回来，{username}")
            self._update_ui()
        else:
            self._show_snackbar("用户名或密码错误")
    
    def do_register(self, *args):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self._show_snackbar("请输入用户名和密码")
            return
        
        if len(password) < 6:
            self._show_snackbar("密码至少需要6位")
            return
        
        if self.db.register_user(username, password):
            self._show_snackbar("注册成功，请登录")
        else:
            self._show_snackbar("用户名已存在")
    
    def do_logout(self, *args):
        app = MDApp.get_running_app()
        app.current_user_id = None
        app.current_username = None
        self.username_input.text = ""
        self.password_input.text = ""
        self._show_snackbar("已退出登录")
        self._update_ui()
    
    def _show_snackbar(self, message):
        MDSnackbar(
            MDLabel(text=message),
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5},
            duration=2,
            md_bg_color=IOS_COLORS['text']
        ).open()


# ============== 主应用 ==============
class PhotoCleanerApp(MDApp):
    """照片整理App - iOS 风格"""
    
    current_user_id = None
    current_username = None
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        # 设置全局中文字体
        if chinese_font:
            self.theme_cls.font_styles.update({
                'H1': [chinese_font, 96, False, -1.5],
                'H2': [chinese_font, 60, False, -0.5],
                'H3': [chinese_font, 48, False, 0],
                'H4': [chinese_font, 34, False, 0.25],
                'H5': [chinese_font, 24, False, 0],
                'H6': [chinese_font, 20, False, 0.15],
                'Subtitle1': [chinese_font, 16, False, 0.15],
                'Subtitle2': [chinese_font, 14, False, 0.1],
                'Body1': [chinese_font, 16, False, 0.5],
                'Body2': [chinese_font, 14, False, 0.25],
                'Button': [chinese_font, 14, True, 1.25],
                'Caption': [chinese_font, 12, False, 0.4],
                'Overline': [chinese_font, 10, True, 1.5],
            })
        
        # iOS 风格底部导航
        self.bottom_nav = MDBottomNavigation()
        
        # 划一下标签
        self.swipe_tab = MDBottomNavigationItem(
            name='swipe',
            text='划一下',
            icon='gesture-swipe'
        )
        self.swipe_screen = SwipeScreen()
        self.swipe_tab.add_widget(self.swipe_screen)
        self.bottom_nav.add_widget(self.swipe_tab)
        
        # 历史记录标签
        self.history_tab = MDBottomNavigationItem(
            name='history',
            text='历史记录',
            icon='history'
        )
        self.history_screen = HistoryScreen()
        self.history_tab.add_widget(self.history_screen)
        self.bottom_nav.add_widget(self.history_tab)
        
        # 我的标签
        self.profile_tab = MDBottomNavigationItem(
            name='profile',
            text='我的',
            icon='account'
        )
        self.profile_screen = ProfileScreen()
        self.profile_tab.add_widget(self.profile_screen)
        self.bottom_nav.add_widget(self.profile_tab)
        
        # 设置颜色（必须在添加子项后）
        self.bottom_nav.selected_color_background = IOS_COLORS['primary']
        self.bottom_nav.text_color_active = IOS_COLORS['primary']
        self.bottom_nav.text_color_normal = IOS_COLORS['text_secondary']
        self.bottom_nav.panel_color = IOS_COLORS['card']
        
        # 扫描相册
        Clock.schedule_once(self._init_album, 0.5)
        
        return self.bottom_nav
    
    def _init_album(self, dt):
        album = AlbumManager()
        album.scan_album()
        # 刷新划一下页面的统计
        self.swipe_screen.load_stats()
    
    def on_photo_action(self, photo_path, action):
        self.swipe_screen.on_photo_action(photo_path, action)


if __name__ == '__main__':
    PhotoCleanerApp().run()
