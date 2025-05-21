import math

from PyQt5.QtCore import Qt, QTime, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QRadialGradient, QBrush
from PyQt5.QtWidgets import QWidget


class AnimatedBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation_progress = 0.0
        self.start_time = QTime.currentTime()
        self.init_animation()
        self.setAttribute(Qt.WA_TranslucentBackground)

    def init_animation(self):
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(16)

    def update_animation(self):
        elapsed = self.start_time.msecsTo(QTime.currentTime())
        self._animation_progress = (elapsed % 15000) / 15000.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # 创建圆角路径（修复关键行）
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 15, 15)  # 将QRect转换为QRectF

        painter.setClipPath(path)
        self.draw_animated_gradients(painter)
        painter.end()

    def draw_animated_gradients(self, painter):
        t = self._animation_progress
        size = max(self.width(), self.height())
        gradients = [
            {"color": QColor(235, 105, 78), "phase": 0.0, "sizes": [1.3, 1.0, 0.8, 0.9]},
            {"color": QColor(243, 11, 164), "phase": 0.25, "sizes": [0.8, 0.9, 1.1, 0.9]},
            {"color": QColor(254, 234, 131), "phase": 0.5, "sizes": [0.9, 1.0, 0.8, 1.0]},
            {"color": QColor(170, 142, 245), "phase": 0.75, "sizes": [1.1, 0.9, 0.6, 0.9]},
            {"color": QColor(248, 192, 147), "phase": 1.0, "sizes": [0.9, 0.6, 0.8, 0.7]}
        ]
        for grad in gradients:
            pos = self.calc_gradient_position(t + grad["phase"])
            grad_size = self.calc_gradient_size(t, grad["sizes"]) * size
            self.draw_gradient(painter, grad["color"], pos, grad_size)

    def calc_gradient_position(self, phase):
        angle = phase * 2 * math.pi
        x = math.cos(angle) * 0.4
        y = math.sin(angle) * 0.4
        return (self.width() / 2 + x * self.width(), self.height() / 2 + y * self.height())

    def calc_gradient_size(self, t, sizes):
        """ 动态计算渐变尺寸的插值方法 """
        phases = [0, 0.25, 0.5, 0.75, 1.0]

        # 处理前三个时间区间 (0-0.25, 0.25-0.5, 0.5-0.75)
        for i in range(len(phases) - 2):  # 遍历0,1,2三个索引
            if phases[i] <= t < phases[i + 1]:
                # 线性插值公式：当前尺寸 + 尺寸差 * 时间比例
                return sizes[i] + (sizes[i + 1] - sizes[i]) * (t - phases[i]) * 4

        # 处理最后一个时间区间 (0.75-1.0)，实现循环效果
        return sizes[-1] + (sizes[0] - sizes[-1]) * (t - phases[-2]) * 4  # phases[-2] = 0.75

    def draw_gradient(self, painter, color, center, size):
        gradient = QRadialGradient(center[0], center[1], size)
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, Qt.transparent)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(self.rect())