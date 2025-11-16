import os
import sys
import threading
import requests
import pygame
from functools import partial
from dotenv import load_dotenv 
from openai import OpenAI
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QScrollArea, QSizePolicy
from config import BASE_URL, API_KEY, MODEL

# 设置Qt插件路径
load_dotenv()
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'./.venv/Lib/site-packages/PyQt5/Qt5/plugins'

# 设置OpenAI环境变量
os.environ['OPENAI_API_BASE'] = BASE_URL
os.environ['OPENAI_API_SECRET'] = API_KEY

# 获取当前 .py 所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# .md 所在的目录
md_path = os.path.join(current_dir, '蜡笔小新设定.md')
# 读取 .md 文件
with open(md_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

##########桌面宠物+系统托盘模块##########

class Qt_pet(QtWidgets.QWidget):
    def __init__(self):
        super(Qt_pet, self).__init__()
        self.dis_file = "img1"
        self.windowinit()
        self.icon_quit()

        self.pos_first = self.pos()
        self.timer = QTimer()
        self.timer.timeout.connect(self.img_update)
        self.timer.start(100)

        # 用于存储 ChatApp 实例
        self.chat_app = None

        # 自动移动功能相关
        self.dragging = False
        self.mouse_pos = QPoint()
        self.last_mouse_pos = QPoint()
        self.is_auto_move_enabled = False  # 默认禁用自动移动功能
        self.animation_running = False    # 是否正在播放动画

        # 设置鼠标事件过滤器
        self.installEventFilter(self)

    def img_update(self):
        if self.img_num < len(self.dir2img[self.current_dir])-1:
            self.img_num += 1
        else:
            self.img_num = 0
        self.qpixmap = QtGui.QPixmap(os.path.join(self.current_dir, self.dir2img[self.current_dir][self.img_num]))
        self.lab.setMaximumSize(self.pet_width, self.pet_height)
        self.lab.setScaledContents(True)
        # 重新设置lab的大小与图片保持一致
        self.lab.setGeometry(0, 0, self.qpixmap.width(), self.qpixmap.height())
        self.lab.setPixmap(self.qpixmap)

    # 获取放图片的路径，图片文件放在同一个项目下的pet_conf文件夹中，文件夹中放具体的图片，图片的格式为N.png(比如1.png，2.png等)
    def get_conf_dir(self):
        conf_dirs = ["桌宠素材/"]
        for conf_dir in conf_dirs:
            if os.path.exists(conf_dir) and os.path.isdir(conf_dir):
                self.conf_dir = conf_dir
                for root, dirs, files in os.walk(self.conf_dir):
                    if root in conf_dirs:
                        for dir in dirs:
                            for r, _, f in os.walk(os.path.join(root, dir)):
                                if r == os.path.join(root, dir) and len(f)>0:
                                    try:
                                        f.sort(key=lambda x: int(x.split(sep='.', maxsplit=1)[0]))
                                    except ValueError:
                                        f.sort(key=lambda x: x.split(sep='.', maxsplit=1)[0])
                                    self.dir2img.update({r: f})
                        return True
        QtWidgets.QMessageBox.warning(None, "警告", "没有找到配置文件哦~", QtWidgets.QMessageBox.StandardButton.Ok)
        return False

    def windowinit(self):
        screen_rect = QApplication.desktop().availableGeometry()
        self.pet_width = 200
        self.pet_height = 200
        self.x = screen_rect.width() - self.pet_width
        self.y = screen_rect.height() - self.pet_height
        self.setGeometry(self.x, self.y, self.pet_width, self.pet_height)
        self.setWindowTitle('蜡笔小新')
        self.img_num = 0
        # 找到配置文件，失败则退出
        self.dir2img = {}
        if not self.get_conf_dir():
            self.quit()
        
        self.lab = QtWidgets.QLabel(self)
        self.current_dir = list(self.dir2img.keys())[0]
        self.qpixmap = QtGui.QPixmap(os.path.join(self.current_dir, self.dir2img[self.current_dir][self.img_num]))
        self.lab.setPixmap(self.qpixmap)
        
        # 设置窗口为 无边框 | 保持顶部显示 | 不显示任务栏图标
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.Tool)
        # 设置窗口透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

    # 音乐控制方法
    def toggle_music(self, checked):
        global music_paused
        with music_lock:
            music_paused = not checked

    def adjust_volume(self, value):
        global current_volume
        with music_lock:
            current_volume = value / 100.0

    # 设置系统托盘
    def icon_quit(self):
        mini_icon = QtWidgets.QSystemTrayIcon(self)
        mini_icon.setIcon(QtGui.QIcon(os.path.join(self.current_dir, self.dir2img[self.current_dir][0])))
        mini_icon.setToolTip("蜡笔小新")
        quit_menu = QtWidgets.QAction('退出', self, triggered=self.quit)
        tpMenu = QtWidgets.QMenu(self)
        
        changeSubMenu = QtWidgets.QMenu(self)
        changeSubMenu.setTitle("切换")
        for dir in self.dir2img.keys():
            act = QtWidgets.QAction(os.path.basename(dir), self, triggered=partial(self.changeImg, dir))
            changeSubMenu.addAction(act)
        tpMenu.addMenu(changeSubMenu)

        # 添加自动移动功能开关
        self.enable_auto_move_action = QtWidgets.QAction("移动开关", self)
        self.enable_auto_move_action.setCheckable(True)
        self.enable_auto_move_action.setChecked(False)  # 默认未勾选
        self.enable_auto_move_action.triggered.connect(self.toggle_auto_move)
        tpMenu.addAction(self.enable_auto_move_action)

        # 添加启动 ChatApp 的菜单项
        chat_app_action = QtWidgets.QAction('聊天', self, triggered=self.start_chat_app)
        tpMenu.addAction(chat_app_action)
        tpMenu.addAction(quit_menu)
        mini_icon.setContextMenu(tpMenu)
        mini_icon.show()

        # 添加音乐控制菜单
        self.music_toggle = QtWidgets.QAction('音乐开关', self, checkable=True)
        self.music_toggle.setChecked(True)
        self.music_toggle.triggered.connect(self.toggle_music)
        tpMenu.addAction(self.music_toggle)

        # 添加音量滑块
        volume_slider = QtWidgets.QSlider(Qt.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(int(current_volume * 100))
        volume_slider.valueChanged.connect(self.adjust_volume)
        
        volume_action = QtWidgets.QWidgetAction(self)
        volume_action.setDefaultWidget(volume_slider)
        tpMenu.addAction(volume_action)

    def toggle_auto_move(self, checked):
        # 切换自动移动功能
        self.is_auto_move_enabled = checked

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = True
            self.mouse_pos = QMouseEvent.globalPos()
            QMouseEvent.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))

    def mouseMoveEvent(self, QMouseEvent):
        if self.dragging:
            delta = QMouseEvent.globalPos() - self.mouse_pos
            new_pos = self.pos() + delta
            self.last_mouse_pos = self.pos()  # 记录上一次位置
            self.move(new_pos)
            self.check_edge(new_pos)  # 检测窗口是否靠近屏幕边缘
            self.mouse_pos = QMouseEvent.globalPos()

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

    def check_edge(self, new_pos):
        # 检查窗口是否靠近屏幕边缘
        if self.is_auto_move_enabled and not self.animation_running:
            screen_rect = QApplication.desktop().availableGeometry(self)
            window_rect = self.geometry()

            # 获取窗口和屏幕的位置信息
            window_top = new_pos.y()
            window_bottom = new_pos.y() + window_rect.height()
            window_left = new_pos.x()
            window_right = new_pos.x() + window_rect.width()

            # 屏幕的高度和宽度
            screen_height = screen_rect.height()
            screen_width = screen_rect.width()

            # 设置边缘阈值
            edge_threshold = min(100, 0.1 * max(screen_height, screen_width))  # 边缘阈值为100像素或屏幕的10%

            # 动画速度（单位：毫秒）
            animation_speed = 10000  # 可以调整这个值来控制移动速度

            # 检查顶部
            if window_top < edge_threshold and self.last_mouse_pos.y() > edge_threshold:
                target_y = screen_height - window_rect.height() - edge_threshold
                self.start_animation(new_pos.x(), target_y, animation_speed)
            # 检查底部
            elif window_bottom > screen_height - edge_threshold and self.last_mouse_pos.y() + window_rect.height() < screen_height - edge_threshold:
                target_y = edge_threshold
                self.start_animation(new_pos.x(), target_y, animation_speed)
            # 检查左边
            elif window_left < edge_threshold and self.last_mouse_pos.x() > edge_threshold:
                target_x = screen_width - window_rect.width() - edge_threshold
                self.start_animation(target_x, new_pos.y(), animation_speed)
            # 检查右边
            elif window_right > screen_width - edge_threshold and self.last_mouse_pos.x() + window_rect.width() < screen_width - edge_threshold:
                target_x = edge_threshold
                self.start_animation(target_x, new_pos.y(), animation_speed)

    def start_animation(self, target_x, target_y, duration):
        # 启动平滑移动动画
        if self.animation_running:
            return

        self.animation = QtCore.QPropertyAnimation(self, b"pos")
        self.animation.setDuration(duration)  # 设置动画持续时间
        self.animation.setStartValue(self.pos())  # 设置动画起始位置
        self.animation.setEndValue(QtCore.QPoint(target_x, target_y))  # 设置动画目标位置
        self.animation.finished.connect(self.animation_finished)  # 动画完成后回调
        self.animation.start()
        self.animation_running = True

    def animation_finished(self):
        # 动画完成后的处理
        self.animation_running = False

    def quit(self):
        self.close()
        sys.exit()

    def changeImg(self, dir):
        self.current_dir = dir

    def start_chat_app(self):
        if not self.chat_app:
            self.chat_app = ChatApp()
            self.chat_app.show()

##########聊天模块##########

# 检查网络连接的函数
def check_internet_connection():
    try:
        # 尝试连接到深度求索（DeepSeek AI）的公共DNS服务器
        requests.get("https://www.deepseek.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

api_key = API_KEY
llm_name = MODEL
base_url = BASE_URL
client = OpenAI(api_key=api_key, base_url=base_url)

system_prompt = '''
你是一个由霄孟芾设置的智能体，你很擅长模仿蜡笔小新(野原新之助)这个动漫角色的说话风格和用户进行交互聊天。
'''

text = md_content

def gen_prompt(context_text, user_input):
    return f"""
    根据如下《蜡笔小新》的设定和背景信息：
    {context_text}    
    请用蜡笔小新的语气和风格回答用户的这个问题
    {user_input}
    """

def call_llm(user_input):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": gen_prompt(text, user_input)}
    ]
    
    response = client.chat.completions.create(
        model=llm_name,
        messages=messages,
        temperature=1
    )
    return response.choices[0].message.content

# 初始化聊天历史（保持原有结构）
history = [
    {"role": "system", "content": system_prompt}
]

# 修改后的聊天函数
def chat(user_input, history):
    history.append({"role": "user", "content": user_input})
    response = call_llm(user_input)
    history.append({"role": "assistant", "content": response})
    return response

# 设置文本气泡样式
class ChatBubble(QLabel):
    def __init__(self, text, is_sender=True, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.is_sender = is_sender
        self.setWordWrap(True)
        self.setFont(QFont("微软雅黑", 10))  # 设置字体为微软雅黑，字号为10
        self.initUI()

    def initUI(self):
        # 设置气泡样式
        if self.is_sender:
            self.setStyleSheet("""
                QLabel {
                    background-color: #DCF8C6;
                    border-radius: 15px;
                    padding: 10px;
                    margin: 5px;
                    alignment: right;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border-radius: 15px;
                    padding: 10px;
                    margin: 5px;
                    alignment: left;
                    border: 1px solid #DDDDDD;
                }
            """)
        # 确保高度根据内容自动调整
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(40)  # 设置最小高度，避免过小

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        # 设置窗口
        self.setLayout(main_layout)
        self.setWindowTitle('蜡笔小新')
        self.setGeometry(300, 300, 480, 800)
        # 加载并设置左上角窗口图标
        icon = QIcon('xiao_xin.ico')
        self.setWindowIcon(icon)        

        # 消息显示区域
        self.message_area = QWidget()
        self.message_area.setStyleSheet("background-color: #FFC0CB;")  # 设置消息显示区域的颜色为粉色#FFC0CB
        message_layout = QVBoxLayout(self.message_area)
        
        # 使用 QScrollArea 来支持消息区域的滚动
        scroll = QScrollArea()
        scroll.setWidget(self.message_area)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # 设置滚动条样式为粉色
        scroll.setStyleSheet("""
            QScrollBar:vertical {
                background: #FFC0CB;
                width: 10px;
            }
        """)
        main_layout.addWidget(scroll)

        # 创建输入框和发送按钮的布局
        input_layout = QHBoxLayout()

        # 创建输入框
        self.input_box = QLineEdit(self)
        self.input_box.setStyleSheet("background-color: #FFC0CB;")  # 设置输入框背景颜色
        input_layout.addWidget(self.input_box)

        # 创建发送按钮
        send_button = QPushButton('发送', self)
        send_button.clicked.connect(self.send_message)
        send_button.setStyleSheet("background-color: #FFC0CB;")  # 设置按钮背景颜色
        input_layout.addWidget(send_button)

        # 将输入框和发送按钮的布局添加到主布局
        main_layout.addLayout(input_layout)

        # 自动发送欢迎消息
        self.send_welcome_message()

    def send_welcome_message(self):
        # 自动发送欢迎消息
        welcome_message = chat("你好！", history)
        self.add_message("小新", welcome_message, is_sender=False)

    def send_message(self):
        # 获取用户输入的消息
        message = self.input_box.text()
        if message:
            # 在聊天记录中显示用户消息
            self.add_message("你", message, is_sender=True)
            # 清空输入框
            self.input_box.clear()

            # 检查网络连接
            if not check_internet_connection():
                # 如果没有网络连接，显示提示信息
                QMessageBox.warning(self, "网络错误哦~", "妈妈，为什么小新不能和大姐姐聊天了？\n\n可我检查了我们家里的网络没有问题呀，是不是大姐姐家的网络坏掉了？")
                return

            # 调用chat函数获取回复
            response = chat(message, history)

            # 在聊天记录中显示蜡笔小新智能体的回复
            self.add_message("小新", response, is_sender=False)

    def add_message(self, sender, message, is_sender):
        # 创建新的气泡并添加到消息区域
        new_message = ChatBubble(f"{sender}: {message}", is_sender=is_sender)
        self.message_area.layout().addWidget(new_message)
        # 滚动到最底部
        self.message_area.layout().update()
        scroll = self.findChild(QScrollArea)
        scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())

##########音乐播放模块##########

# 在全局添加音乐控制变量
music_lock = threading.Lock()
music_paused = False
current_volume = 0.3  # 默认音量30%
playing_second = False  # 标志变量，表示是否正在播放第二首音频

def play_music():
    global music_paused, current_volume, playing_second  # 显式声明全局变量
    # 初始化pygame
    pygame.init()

    # 加载音乐文件
    music1 = './音频文件/蜡笔小新INTRO.wav'
    music2 = './音频文件/蜡笔小新BGM.wav'

    # 初始化当前播放的音乐索引、是否单曲循环的标志和音量
    current_track = 0

    # 加载并播放第一首音乐
    pygame.mixer.music.load(music1)
    pygame.mixer.music.play()


    # 主循环
    running = True
    while running:
        with music_lock:
            # 更新播放状态和音量
            if music_paused:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            pygame.mixer.music.set_volume(current_volume)

        # 检查是否是第一次播放第一首音乐
        if not playing_second:
            if not pygame.mixer.music.get_busy():
                # 第一首音乐播放完毕，加载第二首音乐并循环播放
                pygame.mixer.music.load(music2)
                pygame.mixer.music.play(-1)  # -1 表示循环播放
                playing_second = True

        pygame.time.wait(100)

    pygame.quit()

# 在 PyQt5 的退出逻辑中，确保 pygame 停止播放
def stop_music():
    global music_paused, playing_second
    with music_lock:
        music_paused = True
        playing_second = False
        pygame.mixer.music.stop()
        pygame.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = Qt_pet()
    # sys.exit(app.exec_())

    # 创建并启动音乐播放线程
    music_thread = threading.Thread(target=play_music)
    music_thread.daemon = True  # 设置为守护线程，这样主线程结束时音乐播放线程也会结束
    music_thread.start()
    # 连接退出信号
    app.aboutToQuit.connect(stop_music)
    sys.exit(app.exec_())