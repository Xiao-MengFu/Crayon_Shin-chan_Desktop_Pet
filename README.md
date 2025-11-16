# 蜡笔小新 AI 桌宠 
# Crayon Shin-chan Desktop Pet whit AI Chat
<p style="text-align: center;"><img src="./项目文件/xiao_xin.ico" alt="设置菜单" width="50"></p>

## 介绍
这是本人的第一个项目，是我大一时的作品，开始于 2024 年 11 月至 12 月，结束于 2025 年 2 月至 3 月。运行程序，会在电脑桌面的右下角出现一个可爱的蜡笔小新，设置菜单隐藏在系统的最小化托盘中，选择 **切换** 可以切换不同的动画效果，也可以在 `/桌宠素材` 文件夹中自定义动画效果；其中名称前面有 ★ 的是搭配 **移动开关** 可以获得更棒的动画互动效果，如：选择“★ 火箭飞天”，将蜡笔小新用鼠标拖拽至屏幕下方，松开之后会自动上升；**音乐开关** 可以开启和关闭 BGM 音乐（默认开启），第一段音乐播放的是 `蜡笔小新INTRO.wav` ，只播放一次，第二段开始循环播放 `蜡笔小新BGM.wav`，同样也可以在 `/音频素材` 文件夹自定义音频文件，左右拖动下方滑块，还可以调节音量大小；点击 **聊天** 可以在一个小窗口和扮演蜡笔小新的 AI 大模型进行聊天，用户需要设置自己的大模型服务提供商的 URL 地址、 API_Key 以及模型（建议不要选择推理模型，响应时间更快）。

本项目代码桌面宠物部分改编自B站up主 [@走神的阿圆](https://space.bilibili.com/24657764?spm_id_from=333.1391.0.0 "走神的阿圆 个人主页") 的视频 [《Python代码实现桌面宠物，真IKUN才能养》](https://www.bilibili.com/video/BV1Sg411B7gF) 。本项目采用 MIT 协议，乱选的，因为当时 DeepSeek-R1 开源就选择了 MIT 协议，并且好记。本项目多媒体素材来自网络。

## 使用
1. 克隆项目到本地
```bash
git clone https://github.com/Xiao-MengFu/Crayon_Shin-chan_Desktop_Pet.git
```
2. 进入 `./项目文件` 目录
```bash
cd ./项目文件
```
3. 创建并激活虚拟环境
```bash
# 创建一个名为 .venv 的虚拟环境
python -m venv .venv

# 激活 .venv 虚拟环境
.\.venv\Scripts\activate
```
4. 安装项目依赖
```bash
pip install -r requirements.txt
```
5. 运行程序
```bash
python "诶嘿嘿~大姐姐，请点击我把~.py"
```

<p style="text-align: center;"><img src="./说明图片/设置菜单.png" alt="设置菜单" width="300"></p>
<center>▲ 设置菜单</center>


<p style="text-align: center;"><img src="./说明图片/聊天截图.png" alt="聊天效果截图" width="300"></p>
<center>▲ 聊天效果截图</center>