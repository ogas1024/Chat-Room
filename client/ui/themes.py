"""
TUI界面主题和样式定义
提供多种主题选择和样式配置
"""

from rich.style import Style
from rich.theme import Theme
from textual.design import ColorSystem


class ChatRoomTheme:
    """聊天室主题类"""
    
    def __init__(self, name: str):
        self.name = name
        self.colors = {}
        self.styles = {}
        self.setup_theme()
    
    def setup_theme(self):
        """设置主题"""
        pass  # 由子类实现


class DefaultTheme(ChatRoomTheme):
    """默认主题"""
    
    def setup_theme(self):
        self.colors = {
            "primary": "#0066cc",
            "secondary": "#6c757d", 
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "info": "#17a2b8",
            "background": "#ffffff",
            "surface": "#f8f9fa",
            "text": "#212529",
            "text_muted": "#6c757d"
        }
        
        self.styles = {
            "chat.self": Style(color="green", bold=True),
            "chat.other": Style(color="blue", bold=True),
            "chat.system": Style(color="yellow", italic=True),
            "chat.error": Style(color="red", bold=True),
            "chat.ai": Style(color="cyan", bold=True),
            "chat.timestamp": Style(color="bright_black", dim=True),
            "status.online": Style(color="green"),
            "status.offline": Style(color="red"),
            "border.active": Style(color="blue"),
            "border.inactive": Style(color="bright_black")
        }


class DarkTheme(ChatRoomTheme):
    """深色主题"""
    
    def setup_theme(self):
        self.colors = {
            "primary": "#4dabf7",
            "secondary": "#868e96",
            "success": "#51cf66", 
            "warning": "#ffd43b",
            "error": "#ff6b6b",
            "info": "#74c0fc",
            "background": "#1a1a1a",
            "surface": "#2d2d2d",
            "text": "#ffffff",
            "text_muted": "#adb5bd"
        }
        
        self.styles = {
            "chat.self": Style(color="bright_green", bold=True),
            "chat.other": Style(color="bright_blue", bold=True),
            "chat.system": Style(color="bright_yellow", italic=True),
            "chat.error": Style(color="bright_red", bold=True),
            "chat.ai": Style(color="bright_cyan", bold=True),
            "chat.timestamp": Style(color="bright_black", dim=True),
            "status.online": Style(color="bright_green"),
            "status.offline": Style(color="bright_red"),
            "border.active": Style(color="bright_blue"),
            "border.inactive": Style(color="bright_black")
        }


class TerminalTheme(ChatRoomTheme):
    """终端主题（高对比度）"""
    
    def setup_theme(self):
        self.colors = {
            "primary": "#00ff00",
            "secondary": "#808080",
            "success": "#00ff00",
            "warning": "#ffff00", 
            "error": "#ff0000",
            "info": "#00ffff",
            "background": "#000000",
            "surface": "#1a1a1a",
            "text": "#00ff00",
            "text_muted": "#808080"
        }
        
        self.styles = {
            "chat.self": Style(color="bright_green", bold=True),
            "chat.other": Style(color="bright_white", bold=True),
            "chat.system": Style(color="bright_yellow", italic=True),
            "chat.error": Style(color="bright_red", bold=True),
            "chat.ai": Style(color="bright_cyan", bold=True),
            "chat.timestamp": Style(color="white", dim=True),
            "status.online": Style(color="bright_green"),
            "status.offline": Style(color="bright_red"),
            "border.active": Style(color="bright_green"),
            "border.inactive": Style(color="white")
        }


class ThemeManager:
    """主题管理器"""
    
    def __init__(self):
        self.themes = {
            "default": DefaultTheme("默认"),
            "dark": DarkTheme("深色"),
            "terminal": TerminalTheme("终端")
        }
        self.current_theme = "default"
    
    def get_theme(self, name: str = None) -> ChatRoomTheme:
        """获取主题"""
        theme_name = name or self.current_theme
        return self.themes.get(theme_name, self.themes["default"])
    
    def set_theme(self, name: str) -> bool:
        """设置当前主题"""
        if name in self.themes:
            self.current_theme = name
            return True
        return False
    
    def get_available_themes(self) -> list:
        """获取可用主题列表"""
        return [(name, theme.name) for name, theme in self.themes.items()]
    
    def create_rich_theme(self, theme_name: str = None) -> Theme:
        """创建Rich主题对象"""
        theme = self.get_theme(theme_name)
        return Theme(theme.styles)


# 全局主题管理器实例
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """获取主题管理器实例"""
    return theme_manager


def get_current_theme() -> ChatRoomTheme:
    """获取当前主题"""
    return theme_manager.get_theme()


def apply_theme_to_console(console, theme_name: str = None):
    """将主题应用到Rich控制台"""
    rich_theme = theme_manager.create_rich_theme(theme_name)
    console.push_theme(rich_theme)


# 预定义的样式常量
CHAT_STYLES = {
    "self_message": "chat.self",
    "other_message": "chat.other", 
    "system_message": "chat.system",
    "error_message": "chat.error",
    "ai_message": "chat.ai",
    "timestamp": "chat.timestamp"
}

STATUS_STYLES = {
    "online": "status.online",
    "offline": "status.offline"
}

BORDER_STYLES = {
    "active": "border.active",
    "inactive": "border.inactive"
}


def get_message_style(message_type: str, is_self: bool = False) -> str:
    """获取消息样式"""
    if message_type == "chat":
        return CHAT_STYLES["self_message"] if is_self else CHAT_STYLES["other_message"]
    elif message_type == "system":
        return CHAT_STYLES["system_message"]
    elif message_type == "error":
        return CHAT_STYLES["error_message"]
    elif message_type == "ai":
        return CHAT_STYLES["ai_message"]
    else:
        return CHAT_STYLES["other_message"]


def get_status_style(is_online: bool) -> str:
    """获取状态样式"""
    return STATUS_STYLES["online"] if is_online else STATUS_STYLES["offline"]
