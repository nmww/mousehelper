import pygame
import sys
import pyautogui
import threading
import time
from pynput import keyboard

class MouseClickHelper:
    def __init__(self):
        # 获取屏幕分辨率
        self.screen_width, self.screen_height = pyautogui.size()
        
        # 自动点击控制变量
        self.is_clicking = False
        self.click_thread = None
        self.click_count = 0
        self.target_clicks = 0
        self.click_interval = 1000  # 默认1秒
        self.click_button = "left"  # 默认左键
        self.target_x = self.screen_width // 2
        self.target_y = self.screen_height // 2
        self.hotkey = "f2"
        
        # 输入框状态
        self.active_input = None
        self.input_texts = {
            'clicks': str(self.target_clicks),
            'interval': str(self.click_interval),
            'target_x': str(self.target_x),
            'target_y': str(self.target_y)
        }
        
        # 下拉框选项
        self.hotkey_options = [f"f{i}" for i in range(1, 13)]
        self.button_options = ["left", "right"]
        self.hotkey_dropdown_open = False
        self.button_dropdown_open = False
        
        # 初始化Pygame
        pygame.init()
        self.window_width = 900
        self.window_height = 700
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("鼠标点击助手")
        
        # 设置窗口置顶（Windows系统）- 改进版本
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info()['window']
            # 使用HWND_TOPMOST参数确保窗口始终置顶
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001)
        except:
            pass  # 如果设置置顶失败，继续运行
        
        # 字体
        self.font = pygame.font.SysFont('simhei', 24)
        self.small_font = pygame.font.SysFont('simhei', 18)
        
        # 颜色
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.GREEN = (0, 200, 0)
        self.RED = (200, 0, 0)
        self.BLUE = (0, 120, 255)
        self.LIGHT_BLUE = (173, 216, 230)
        
        # 设置热键监听
        self.hotkey_listener = None
        self.setup_hotkey_listener()
        
    def setup_hotkey_listener(self):
        """设置热键监听器"""
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    key_str = key.char
                else:
                    key_str = str(key).replace("Key.", "").lower()
                
                if key_str == self.hotkey:
                    self.toggle_clicking()
            except AttributeError:
                pass
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
    
    def toggle_clicking(self):
        """切换点击状态"""
        self.is_clicking = not self.is_clicking
        if self.is_clicking:
            self.start_clicking()
        else:
            self.stop_clicking()
    
    def start_clicking(self):
        """开始自动点击"""
        if self.click_thread is None or not self.click_thread.is_alive():
            self.click_thread = threading.Thread(target=self.auto_click)
            self.click_thread.daemon = True
            self.click_thread.start()
    
    def stop_clicking(self):
        """停止自动点击"""
        self.is_clicking = False
    
    def auto_click(self):
        """自动点击线程"""
        self.click_count = 0
        while self.is_clicking and (self.target_clicks == 0 or self.click_count < self.target_clicks):
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            
            # 如果当前坐标不等于目标坐标，先移动鼠标
            if current_x != self.target_x or current_y != self.target_y:
                pyautogui.moveTo(self.target_x, self.target_y)
                # 等待一小段时间确保鼠标移动完成
                time.sleep(0.05)
            
            # 执行点击
            if self.click_button == "left":
                pyautogui.click()
            else:
                pyautogui.rightClick()
            
            self.click_count += 1
            time.sleep(self.click_interval / 1000.0)
            
            # 检查是否达到目标点击次数
            if self.target_clicks > 0 and self.click_count >= self.target_clicks:
                self.is_clicking = False
                break
    
    def draw_button(self, surface, text, rect, color, hover=False):
        """绘制按钮"""
        button_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255)) if hover else color
        pygame.draw.rect(surface, button_color, rect, border_radius=5)
        pygame.draw.rect(surface, self.BLACK, rect, 2, border_radius=5)
        
        text_surf = self.font.render(text, True, self.BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)
    
    def draw_input_box(self, surface, text, rect, active=False):
        """绘制输入框"""
        color = self.BLUE if active else self.GRAY
        pygame.draw.rect(surface, self.WHITE, rect)
        pygame.draw.rect(surface, color, rect, 2, border_radius=3)
        
        text_surf = self.small_font.render(text, True, self.BLACK)
        surface.blit(text_surf, (rect.x + 5, rect.y + (rect.height - text_surf.get_height()) // 2))
        
        # 如果输入框激活，绘制光标
        if active:
            cursor_x = rect.x + 5 + text_surf.get_width()
            cursor_y = rect.y + 5
            cursor_height = rect.height - 10
            pygame.draw.line(surface, self.BLACK, (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + cursor_height), 2)
    
    def apply_settings(self):
        """应用设置"""
        try:
            # 验证并应用设置
            self.target_clicks = max(0, int(self.input_texts['clicks']))
            self.click_interval = max(100, int(self.input_texts['interval']))  # 最小间隔100ms
            self.target_x = max(0, min(int(self.input_texts['target_x']), self.screen_width))
            self.target_y = max(0, min(int(self.input_texts['target_y']), self.screen_height))
            
            # 重新设置热键监听器
            if self.hotkey_listener:
                self.hotkey_listener.stop()
            self.setup_hotkey_listener()
            
        except ValueError:
            # 如果输入无效，恢复默认值
            self.input_texts['clicks'] = str(self.target_clicks)
            self.input_texts['interval'] = str(self.click_interval)
            self.input_texts['target_x'] = str(self.target_x)
            self.input_texts['target_y'] = str(self.target_y)
    
    def handle_input_event(self, event):
        """处理输入事件"""
        if self.active_input:
            if event.key == pygame.K_RETURN:
                self.apply_settings()
                self.active_input = None
            elif event.key == pygame.K_BACKSPACE:
                self.input_texts[self.active_input] = self.input_texts[self.active_input][:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active_input = None
            elif event.unicode.isdigit() or (event.unicode == '0' and self.active_input in ['clicks', 'interval', 'target_x', 'target_y']):
                self.input_texts[self.active_input] += event.unicode
    
    def draw_dropdown(self, surface, rect, options, current_value, is_open, label):
        """绘制下拉框"""
        # 绘制下拉框主体
        pygame.draw.rect(surface, self.WHITE, rect)
        pygame.draw.rect(surface, self.BLUE, rect, 2, border_radius=3)
        
        # 绘制当前值
        value_text = current_value.upper() if label == "热键:" else ("左键" if current_value == "left" else "右键")
        value_surf = self.small_font.render(value_text, True, self.BLACK)
        surface.blit(value_surf, (rect.x + 5, rect.y + (rect.height - value_surf.get_height()) // 2))
        
        # 绘制下拉箭头
        arrow_points = [(rect.right - 15, rect.centery - 3), (rect.right - 10, rect.centery + 3), (rect.right - 5, rect.centery - 3)]
        pygame.draw.polygon(surface, self.BLACK, arrow_points)
        
        # 绘制标签 - 移动到下拉框右侧
        label_surf = self.small_font.render(label, True, self.BLACK)
        surface.blit(label_surf, (rect.x + rect.width + 10, rect.y))
        
        # 如果下拉框打开，绘制选项
        if is_open:
            dropdown_rect = pygame.Rect(rect.x, rect.bottom, rect.width, len(options) * 30)
            pygame.draw.rect(surface, self.WHITE, dropdown_rect)
            pygame.draw.rect(surface, self.BLACK, dropdown_rect, 1)
            
            for i, option in enumerate(options):
                option_rect = pygame.Rect(rect.x, rect.bottom + i * 30, rect.width, 30)
                if option_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(surface, self.LIGHT_BLUE, option_rect)
                
                option_text = option.upper() if label == "热键:" else ("左键" if option == "left" else "右键")
                option_surf = self.small_font.render(option_text, True, self.BLACK)
                surface.blit(option_surf, (option_rect.x + 5, option_rect.y + (option_rect.height - option_surf.get_height()) // 2))
    
    def run(self):
        """运行主循环"""
        clock = pygame.time.Clock()
        running = True
        
        # 重新定义布局区域，避免重叠
        # 状态信息区域：左侧顶部
        # 参数设置区域：右侧顶部
        # 操作说明区域：左侧底部
        # 当前设置区域：右侧底部
        
        # 参数设置区域 - 重新调整位置
        input_rects = {
            'clicks': pygame.Rect(500, 120, 150, 30),
            'interval': pygame.Rect(500, 170, 150, 30),
            'target_x': pygame.Rect(500, 270, 150, 30),
            'target_y': pygame.Rect(500, 320, 150, 30)
        }
        
        hotkey_dropdown_rect = pygame.Rect(500, 220, 150, 30)
        button_dropdown_rect = pygame.Rect(500, 370, 150, 30)
        
        apply_button = pygame.Rect(500, 420, 120, 40)
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_input_event(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    option_handled = False
                    
                    # 优先处理下拉框选项选择（当下拉框打开时）
                    if self.hotkey_dropdown_open:
                        for i, option in enumerate(self.hotkey_options):
                            option_rect = pygame.Rect(hotkey_dropdown_rect.x, 
                                                    hotkey_dropdown_rect.bottom + i * 30, 
                                                    hotkey_dropdown_rect.width, 30)
                            if option_rect.collidepoint(event.pos):
                                self.hotkey = option
                                self.hotkey_dropdown_open = False
                                self.apply_settings()
                                option_handled = True
                                break
                    
                    if not option_handled and self.button_dropdown_open:
                        for i, option in enumerate(self.button_options):
                            option_rect = pygame.Rect(button_dropdown_rect.x, 
                                                    button_dropdown_rect.bottom + i * 30, 
                                                    button_dropdown_rect.width, 30)
                            if option_rect.collidepoint(event.pos):
                                self.click_button = option
                                self.button_dropdown_open = False
                                self.apply_settings()
                                option_handled = True
                                break
                    
                    # 如果已经处理了下拉框选项，就不处理其他控件
                    if option_handled:
                        continue
                    
                    # 处理热键下拉框
                    if hotkey_dropdown_rect.collidepoint(event.pos):
                        self.hotkey_dropdown_open = not self.hotkey_dropdown_open
                        self.button_dropdown_open = False
                        self.active_input = None
                        continue
                    
                    # 处理按钮下拉框
                    if button_dropdown_rect.collidepoint(event.pos):
                        self.button_dropdown_open = not self.button_dropdown_open
                        self.hotkey_dropdown_open = False
                        self.active_input = None
                        continue
                    
                    # 处理输入框点击
                    for input_name, rect in input_rects.items():
                        if rect.collidepoint(event.pos):
                            self.active_input = input_name
                            self.hotkey_dropdown_open = False
                            self.button_dropdown_open = False
                            break
                    
                    # 处理应用按钮
                    if apply_button.collidepoint(event.pos):
                        self.apply_settings()
            
            # 清屏
            self.screen.fill(self.WHITE)
            
            # 绘制背景分区
            pygame.draw.rect(self.screen, (245, 245, 245), (20, 20, 850, 650), border_radius=10)
            pygame.draw.rect(self.screen, self.BLACK, (20, 20, 850, 650), 2, border_radius=10)
            
            # 显示标题
            title = self.font.render("鼠标点击助手", True, self.BLUE)
            self.screen.blit(title, (self.window_width // 2 - title.get_width() // 2, 35))
            
            # 左侧顶部：状态信息区域 (80-250)
            pygame.draw.rect(self.screen, (240, 248, 255), (40, 80, 400, 165), border_radius=8)
            pygame.draw.rect(self.screen, self.BLUE, (40, 80, 400, 165), 2, border_radius=8)
            
            status_title = self.font.render("状态信息", True, self.BLUE)
            self.screen.blit(status_title, (50, 95))
            
            # 显示屏幕分辨率
            resolution_text = f"屏幕分辨率: {self.screen_width} x {self.screen_height}"
            resolution_surf = self.small_font.render(resolution_text, True, self.BLACK)
            self.screen.blit(resolution_surf, (60, 130))
            
            # 显示鼠标坐标
            actual_mouse_x, actual_mouse_y = pyautogui.position()
            mouse_text = f"鼠标坐标: X={actual_mouse_x}, Y={actual_mouse_y}"
            mouse_surf = self.small_font.render(mouse_text, True, self.BLACK)
            self.screen.blit(mouse_surf, (60, 160))
            
            # 显示当前状态
            status_color = self.RED if self.is_clicking else self.GREEN
            status_text = "运行中" if self.is_clicking else "已停止"
            status_surf = self.small_font.render(f"状态: {status_text}", True, status_color)
            self.screen.blit(status_surf, (60, 190))
            
            # 显示点击统计
            clicks_text = f"已点击: {self.click_count}"
            if self.target_clicks > 0:
                clicks_text += f" / {self.target_clicks}"
            clicks_surf = self.small_font.render(clicks_text, True, self.BLACK)
            self.screen.blit(clicks_surf, (60, 220))
            
            # 右侧顶部：参数设置区域 (80-470)
            pygame.draw.rect(self.screen, (255, 250, 240), (480, 80, 370, 390), border_radius=8)
            pygame.draw.rect(self.screen, self.BLUE, (480, 80, 370, 390), 2, border_radius=8)
            
            settings_title = self.font.render("参数设置", True, self.BLUE)
            self.screen.blit(settings_title, (490, 95))
            
            # 绘制输入框 - 调整标签位置到右侧
            labels = {
                'clicks': "点击次数 (0=无限):",
                'interval': "点击间隔 (ms):", 
                'target_x': "目标坐标 X:",
                'target_y': "目标坐标 Y:"
            }
            
            for input_name, rect in input_rects.items():
                # 绘制标签 - 移动到输入框右侧
                label_surf = self.small_font.render(labels[input_name], True, self.BLACK)
                self.screen.blit(label_surf, (rect.x + rect.width + 10, rect.y))
                
                # 绘制输入框
                active = self.active_input == input_name
                self.draw_input_box(self.screen, self.input_texts[input_name], rect, active)
            
            # 绘制下拉框 - 调整标签位置
            self.draw_dropdown(self.screen, hotkey_dropdown_rect, self.hotkey_options, 
                              self.hotkey, self.hotkey_dropdown_open, "热键:")
            
            self.draw_dropdown(self.screen, button_dropdown_rect, self.button_options, 
                              self.click_button, self.button_dropdown_open, "点击按钮:")
            
            # 绘制应用按钮
            self.draw_button(self.screen, "应用设置", apply_button, self.GREEN, 
                           apply_button.collidepoint(mouse_pos))
            
            # 左侧底部：操作说明区域 (260-450)
            pygame.draw.rect(self.screen, (240, 255, 240), (40, 260, 400, 180), border_radius=8)
            pygame.draw.rect(self.screen, self.GREEN, (40, 260, 400, 180), 2, border_radius=8)
            
            instructions_title = self.font.render("操作说明", True, self.GREEN)
            self.screen.blit(instructions_title, (50, 275))
            
            instructions = [
                "• 在右侧设置区域输入参数",
                "• 按Enter或点击'应用设置'保存",
                "• 按选定的热键(F1-F12)开始/停止",
                "• 自动点击前会先移动鼠标",
                "• 窗口已置顶，方便查看状态"
            ]
            
            for i, instruction in enumerate(instructions):
                inst_surf = self.small_font.render(instruction, True, self.BLACK)
                self.screen.blit(inst_surf, (60, 310 + i * 25))
            
            # 右侧底部：当前设置区域 (480-650)
            pygame.draw.rect(self.screen, (255, 245, 240), (480, 480, 370, 170), border_radius=8)
            pygame.draw.rect(self.screen, self.RED, (480, 480, 370, 170), 2, border_radius=8)
            
            current_title = self.font.render("当前设置", True, self.RED)
            self.screen.blit(current_title, (490, 495))
            
            current_settings = [
                f"热键: {self.hotkey.upper()}",
                f"按钮: {'左键' if self.click_button == 'left' else '右键'}",
                f"间隔: {self.click_interval}ms",
                f"目标坐标: ({self.target_x}, {self.target_y})",
                f"目标次数: {self.target_clicks if self.target_clicks > 0 else '无限'}"
            ]
            
            for i, setting in enumerate(current_settings):
                setting_surf = self.small_font.render(setting, True, self.BLACK)
                self.screen.blit(setting_surf, (500, 525 + i * 25))
            
            pygame.display.flip()
            clock.tick(60)
        
        # 清理资源
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = MouseClickHelper()
    app.run()