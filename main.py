import pygame
import sys
import pyautogui
import threading
import time
import os
import subprocess
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
        self.click_interval = 30000  # 默认1秒
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
        
        # 双击检测
        self.last_click_time = 0
        self.double_click_threshold = 500  # 双击时间阈值（毫秒）
        
        # 坐标获取模式
        self.coord_get_mode = False
        self.coord_get_start_time = 0
        self.coord_get_timeout = 10  # 10秒超时
        
        # 坐标记录文件
        self.coord_file = "temp_coord.txt"
        
        # 窗口自适应 - 根据屏幕分辨率调整窗口大小
        self.window_scale = 0.125  # 窗口占屏幕的比例 (1/8)
        self.window_width = int(self.screen_width * self.window_scale)
        self.window_height = int(self.screen_height * self.window_scale)
        
        # 确保窗口大小在合理范围内
        self.window_width = max(800, min(self.window_width, 1200))
        self.window_height = max(600, min(self.window_height, 900))
        
        # 计算布局比例因子
        self.layout_scale_x = self.window_width / 900.0  # 基准宽度900
        self.layout_scale_y = self.window_height / 700.0  # 基准高度700
        
        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption("鼠标点击助手")
        
        # 设置窗口置顶（Windows系统）- 改进版本
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info()['window']
            # 使用HWND_TOPMOST参数确保窗口始终置顶
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001)
        except:
            pass  # 如果设置置顶失败，继续运行
        
        # 字体 - 根据窗口大小自适应
        self.base_font_size = int(24 * min(self.layout_scale_x, self.layout_scale_y))
        self.base_small_font_size = int(18 * min(self.layout_scale_x, self.layout_scale_y))
        self.font = pygame.font.SysFont('simhei', max(20, self.base_font_size))
        self.small_font = pygame.font.SysFont('simhei', max(16, self.base_small_font_size))
        
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
    
    def save_coordinates_to_file(self, x, y):
        """保存坐标到临时文件"""
        try:
            with open(self.coord_file, 'w') as f:
                f.write(f"{x},{y}")
        except:
            pass
    
    def read_coordinates_from_file(self):
        """从临时文件读取坐标"""
        try:
            if os.path.exists(self.coord_file):
                with open(self.coord_file, 'r') as f:
                    content = f.read().strip()
                    if ',' in content:
                        x, y = content.split(',')
                        return int(x), int(y)
        except:
            pass
        return None, None
    
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
            # 添加对数字键盘的支持
            elif event.key in [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, 
                             pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]:
                # 将数字键盘按键转换为对应数字
                num = event.key - pygame.K_KP0
                self.input_texts[self.active_input] += str(num)
            # 添加对数字键的直接支持（向日葵可能只发送key事件，不发送unicode）
            elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                             pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                # 将数字键转换为对应数字
                if event.key == pygame.K_0:
                    num = '0'
                else:
                    num = str(event.key - pygame.K_0)
                self.input_texts[self.active_input] += num
        # 处理空格键获取坐标
        elif event.key == pygame.K_SPACE and self.coord_get_mode:
            current_x, current_y = pyautogui.position()
            self.input_texts['target_x'] = str(current_x)
            self.input_texts['target_y'] = str(current_y)
            self.coord_get_mode = False
            print(f"已获取坐标: ({current_x}, {current_y})")
    
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
        
        # 自适应布局计算
        # 基准布局尺寸 (基于900x700窗口)
        base_width, base_height = 900, 700
        
        # 计算缩放后的布局位置和尺寸
        def scale_rect(x, y, width, height):
            return pygame.Rect(
                int(x * self.layout_scale_x),
                int(y * self.layout_scale_y),
                int(width * self.layout_scale_x),
                int(height * self.layout_scale_y)
            )
        
        # 参数设置区域 - 自适应调整位置和大小
        input_rects = {
            'clicks': scale_rect(500, 120, 150, 30),
            'interval': scale_rect(500, 170, 150, 30),
            'target_x': scale_rect(500, 270, 150, 30),
            'target_y': scale_rect(500, 320, 150, 30)
        }
        
        hotkey_dropdown_rect = scale_rect(500, 220, 150, 30)
        button_dropdown_rect = scale_rect(500, 370, 150, 30)
        
        apply_button = scale_rect(500, 420, 120, 40)
        get_coord_button = scale_rect(630, 420, 120, 40)  # 获取坐标按钮 - 与应用设置保持水平
        
        # 间隔时间调整按钮 - 向右移动，放在"间隔时间 (ms):"标签右侧
        interval_up_button = scale_rect(780, 170, 30, 15)  # 增加间隔时间按钮
        interval_down_button = scale_rect(780, 190, 30, 15)  # 减少间隔时间按钮
        
        # 开始/停止按钮 - 放在操作说明边框外下方，调整位置确保可见
        start_button = scale_rect(100, 570, 120, 40)  # 开始按钮
        stop_button = scale_rect(250, 570, 120, 40)   # 停止按钮
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
            
            # 检查坐标获取模式超时
            if self.coord_get_mode and time.time() - self.coord_get_start_time > self.coord_get_timeout:
                self.coord_get_mode = False
                print("坐标获取模式已超时")
            
            # 检查是否有新的坐标记录
            if self.coord_get_mode:
                x, y = self.read_coordinates_from_file()
                if x is not None and y is not None:
                    self.input_texts['target_x'] = str(x)
                    self.input_texts['target_y'] = str(y)
                    self.coord_get_mode = False
                    print(f"已获取坐标: ({x}, {y})")
                    # 删除临时文件
                    try:
                        os.remove(self.coord_file)
                    except:
                        pass
            
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
                    
                    # 处理获取坐标按钮
                    if get_coord_button.collidepoint(event.pos):
                        if not self.is_clicking:  # 仅在停止状态可用
                            # 使用简单的坐标获取方式
                            print("请将鼠标移动到目标位置，然后按空格键获取坐标...")
                            self.coord_get_mode = True
                            self.coord_get_start_time = time.time()
                    
                    # 处理间隔时间调整按钮
                    if interval_up_button.collidepoint(event.pos):
                        # 增加间隔时间1000毫秒
                        try:
                            current_interval = int(self.input_texts['interval'])
                            new_interval = current_interval + 1000
                            self.input_texts['interval'] = str(new_interval)
                            print(f"间隔时间增加到: {new_interval}ms")
                        except ValueError:
                            self.input_texts['interval'] = "1000"
                    
                    if interval_down_button.collidepoint(event.pos):
                        # 减少间隔时间1000毫秒（最小100毫秒）
                        try:
                            current_interval = int(self.input_texts['interval'])
                            new_interval = max(100, current_interval - 1000)
                            self.input_texts['interval'] = str(new_interval)
                            print(f"间隔时间减少到: {new_interval}ms")
                        except ValueError:
                            self.input_texts['interval'] = "1000"
                    
                    # 处理开始按钮
                    if start_button.collidepoint(event.pos):
                        if not self.is_clicking:
                            self.apply_settings()  # 先应用当前设置
                            self.toggle_clicking()
                            print("开始自动点击")
                    
                    # 处理停止按钮
                    if stop_button.collidepoint(event.pos):
                        if self.is_clicking:
                            self.toggle_clicking()
                            print("停止自动点击")
                    
                    # 处理双击设置坐标
                    if event.button == 1:  # 左键点击
                        current_time = time.time() * 1000  # 转换为毫秒
                        if current_time - self.last_click_time < self.double_click_threshold:
                            # 双击事件
                            if not self.is_clicking:  # 仅在停止状态可用
                                current_x, current_y = pyautogui.position()
                                self.input_texts['target_x'] = str(current_x)
                                self.input_texts['target_y'] = str(current_y)
                                print(f"双击设置坐标: ({current_x}, {current_y})")
                        self.last_click_time = current_time
            
            # 清屏
            self.screen.fill(self.WHITE)
            
            # 绘制背景分区
            pygame.draw.rect(self.screen, (245, 245, 245), (20, 20, 850, 650), border_radius=10)
            pygame.draw.rect(self.screen, self.BLACK, (20, 20, 850, 650), 2, border_radius=10)
            
            # 显示标题
            title = self.font.render("鼠标点击助手", True, self.BLUE)
            self.screen.blit(title, (self.window_width // 2 - title.get_width() // 2, 35))
            
            # 自适应布局区域计算
            # 左侧顶部：状态信息区域 - 高度增加20
            status_rect = scale_rect(40, 80, 400, 185)  # 高度从165增加到185
            pygame.draw.rect(self.screen, (240, 248, 255), status_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.BLUE, status_rect, 2, border_radius=8)
            
            status_title = self.font.render("状态信息", True, self.BLUE)
            self.screen.blit(status_title, (status_rect.x + 10, status_rect.y + 15))
            
            # 显示屏幕分辨率
            resolution_text = f"屏幕分辨率: {self.screen_width} x {self.screen_height}"
            resolution_surf = self.small_font.render(resolution_text, True, self.BLACK)
            self.screen.blit(resolution_surf, (status_rect.x + 20, status_rect.y + 50))
            
            # 显示鼠标坐标
            actual_mouse_x, actual_mouse_y = pyautogui.position()
            mouse_text = f"鼠标坐标: X={actual_mouse_x}, Y={actual_mouse_y}"
            mouse_surf = self.small_font.render(mouse_text, True, self.BLACK)
            self.screen.blit(mouse_surf, (status_rect.x + 20, status_rect.y + 80))
            
            # 显示当前状态
            status_color = self.RED if self.is_clicking else self.GREEN
            status_text = "运行中" if self.is_clicking else "已停止"
            status_surf = self.small_font.render(f"状态: {status_text}", True, status_color)
            self.screen.blit(status_surf, (status_rect.x + 20, status_rect.y + 110))
            
            # 显示点击统计
            clicks_text = f"已点击: {self.click_count}"
            if self.target_clicks > 0:
                clicks_text += f" / {self.target_clicks}"
            clicks_surf = self.small_font.render(clicks_text, True, self.BLACK)
            self.screen.blit(clicks_surf, (status_rect.x + 20, status_rect.y + 140))
            
            # 右侧顶部：参数设置区域
            settings_rect = scale_rect(480, 80, 370, 390)
            pygame.draw.rect(self.screen, (255, 250, 240), settings_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.BLUE, settings_rect, 2, border_radius=8)
            
            settings_title = self.font.render("参数设置", True, self.BLUE)
            self.screen.blit(settings_title, (settings_rect.x + 10, settings_rect.y + 15))
            
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
                label_x = rect.x + rect.width + int(10 * self.layout_scale_x)
                self.screen.blit(label_surf, (label_x, rect.y))
                
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
            
            # 绘制获取坐标按钮
            self.draw_button(self.screen, "获取坐标", get_coord_button, self.BLUE, 
                           get_coord_button.collidepoint(mouse_pos))
            
            # 绘制间隔时间调整按钮
            # 增加按钮（向上箭头）
            pygame.draw.rect(self.screen, self.LIGHT_BLUE if interval_up_button.collidepoint(mouse_pos) else self.GRAY, 
                           interval_up_button, border_radius=3)
            pygame.draw.rect(self.screen, self.BLACK, interval_up_button, 1, border_radius=3)
            # 绘制向上箭头
            arrow_up_points = [
                (interval_up_button.centerx, interval_up_button.top + 3),
                (interval_up_button.centerx - 5, interval_up_button.bottom - 3),
                (interval_up_button.centerx + 5, interval_up_button.bottom - 3)
            ]
            pygame.draw.polygon(self.screen, self.BLACK, arrow_up_points)
            
            # 减少按钮（向下箭头）
            pygame.draw.rect(self.screen, self.LIGHT_BLUE if interval_down_button.collidepoint(mouse_pos) else self.GRAY, 
                           interval_down_button, border_radius=3)
            pygame.draw.rect(self.screen, self.BLACK, interval_down_button, 1, border_radius=3)
            # 绘制向下箭头
            arrow_down_points = [
                (interval_down_button.centerx, interval_down_button.bottom - 3),
                (interval_down_button.centerx - 5, interval_down_button.top + 3),
                (interval_down_button.centerx + 5, interval_down_button.top + 3)
            ]
            pygame.draw.polygon(self.screen, self.BLACK, arrow_down_points)
            
            # 绘制开始/停止按钮
            # 开始按钮 - 绿色
            start_color = self.GREEN if not self.is_clicking else self.GRAY
            self.draw_button(self.screen, "开始", start_button, start_color, 
                           start_button.collidepoint(mouse_pos) and not self.is_clicking)
            
            # 停止按钮 - 红色
            stop_color = self.RED if self.is_clicking else self.GRAY
            self.draw_button(self.screen, "停止", stop_button, stop_color, 
                           stop_button.collidepoint(mouse_pos) and self.is_clicking)
            
            # 左侧底部：操作说明区域 - 距离状态信息下边框+30，Y坐标增加40
            instructions_rect = scale_rect(40, 295, 400, 260)  # Y从260增加到295 (80+185+30=295)
            pygame.draw.rect(self.screen, (240, 255, 240), instructions_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.GREEN, instructions_rect, 2, border_radius=8)
            
            instructions_title = self.font.render("操作说明", True, self.GREEN)
            self.screen.blit(instructions_title, (instructions_rect.x + 10, instructions_rect.y + 15))
            
            instructions = [
                "• 在右侧设置区域输入参数",
                "• 按Enter或点击'应用设置'保存",
                "• 按选定的热键(F1-F12)开始/停止",
                "• 点击'获取坐标'按钮自动获取坐标",
                "• 双击屏幕任意位置也可获取坐标",
                "• 自动点击前会先移动鼠标",
                "• 窗口已置顶，方便查看状态"
            ]
            
            for i, instruction in enumerate(instructions):
                inst_surf = self.small_font.render(instruction, True, self.BLACK)
                self.screen.blit(inst_surf, (instructions_rect.x + 20, instructions_rect.y + 50 + i * 25))
            
            # 右侧底部：当前设置区域 - Y坐标增加15
            current_rect = scale_rect(480, 495, 370, 200)  # Y从480增加到495
            pygame.draw.rect(self.screen, (255, 245, 240), current_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.RED, current_rect, 2, border_radius=8)
            
            current_title = self.font.render("当前设置", True, self.RED)
            self.screen.blit(current_title, (current_rect.x + 10, current_rect.y + 15))
            
            current_settings = [
                f"热键: {self.hotkey.upper()}",
                f"按钮: {'左键' if self.click_button == 'left' else '右键'}",
                f"间隔: {self.click_interval}ms",
                f"目标坐标: ({self.target_x}, {self.target_y})",
                f"目标次数: {self.target_clicks if self.target_clicks > 0 else '无限'}"
            ]
            
            for i, setting in enumerate(current_settings):
                setting_surf = self.small_font.render(setting, True, self.BLACK)
                self.screen.blit(setting_surf, (current_rect.x + 20, current_rect.y + 45 + i * 25))
            
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