# 图书馆管理系统 🎓

[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![PyQt5](https://img.shields.io/badge/PyQt-5-green?logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![QFluentWidgets](https://img.shields.io/badge/QFluentWidgets-latest-purple)](https://qfluentwidgets.com/)

> 毕设来的，到了反哺开源社区的时候了 :-) 希望能对您有所启发

# 效果展示

## V2：

![V2](readme_img\Snipaste_V2.png)

## V3:

![V3_1](readme_img\Snipaste_V3_1.png)
![V3_2](readme_img\Snipaste_V3_2.png)

> V3 版本的背景会流动渐变

## 🚀 快速开始

### 环境要求

- Python 3.11+
- MySQL
- 虚拟环境（推荐使用项目自带的 `venv`）

### 数据库配置

1. 导入数据库：使用 Navicat 导入 `librarydatabase.sql` 文件
2. 配置数据库连接：
   在 `connector_pymysql.py`（或 `connector.py`）中修改以下配置：
   ```python
   db_config = {
       "host": "localhost",
       "database": "librarydatabase",
       "user": "root",
       "password": "你的数据库密码"  # 改成你自己的密码！
   }
   ```

### 运行项目

- 带 GUI 界面：运行 `UI_main.py`
- 命令行版本：运行 `main.py`

## 🌟 版本说明

项目包含三个版本（v1、v2、v3），默认展示 v2 版本。

> 至于为什么优先展示 V2 版本，因为 V2 到 V3 的改变仅在于重写了部分 PyQt 的绘画事件以优化画面，但是绘画事件的重写并不是一件容易的事，（至少对于当时的作者来说），所以使用了 ai 生成，但请放心，其余部分均为古法纯人工手写，尽管作者及其中意 qfluentwidgets 的简约风格，但显然我的指导老师并不这么认为 😅

![不美观，不炫酷](readme_img\Snipaste_WeChat.png)

## 💡 技术小贴士

- 关于数据库连接：项目提供了两个连接器实现（`connector.py` 和 `connector_pymysql.py`）
- 实际使用 `connector_pymysql.py`：因为 `mysql.connector` 可能会和 PyQt 的底层 C 实现起冲突

## 📂 项目结构

你可以：

1. 直接在对应版本文件夹中运行
2. 或者把需要的版本文件复制到根目录（记得删除根目录已有的 .py 文件）

## 📝 开源协议

因为使用了 [qfluentwidgets](https://qfluentwidgets.com/)（超棒的 UI 库 🥵），项目需遵循 GPL 协议。

- 源码：[PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
- 要求：修改后的代码也需要使用 GPL 协议并禁止商用

## 🤝 贡献

欢迎提出建议和改进！如果这个项目对你有帮助，别忘了给个 star ⭐
