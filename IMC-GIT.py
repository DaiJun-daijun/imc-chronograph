from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from math import *
import sys
import calendar
import datetime
import ctypes  # 新增：用于调用Windows API阻止休眠

# 定义Windows API常量
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


class IMCChrnongreph(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMC Chrnongreph")
        self.showFullScreen()

        # 阻止系统休眠和屏幕关闭（Windows）
        self.prevent_sleep()

        # 设置背景颜色（外部区域）为深蓝色 (10,25,45)
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(10, 25, 45))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # 设置字体（保持原样）
        self.font_main = QFont("Arial", 3)  # 主表盘数字
        self.font_sub = QFont("Arial", 13)  # 子表盘数字
        self.font_brand = QFont("New", 7)  # IMC品牌
        self.font_brand.setStretch(130)
        self.font_city = QFont("Arial", 3)  # SCHEEEHAUSEN
        self.font_swiss_made = QFont("Arial", 2)  # SWISS_MADE
        self.font_chr = QFont("Arial", 4.5)  # CHRNONGREPH AUTOMATIC

        # 计时器设置
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

        # 计时功能变量
        self.chrono_running = False
        self.chrono_start_time = 0
        self.chrono_elapsed = 0
        self.chrono_paused_time = 0

        # 指针形状定义（完全不变）
        self.hour_hand_path = QPainterPath()
        self.hour_hand_path.moveTo(0, -88)
        self.hour_hand_path.cubicTo(4, -40, 4, -40, 0, 0)
        self.hour_hand_path.lineTo(-0, 0)
        self.hour_hand_path.cubicTo(-4, -40, -4, -40, 0, -88)

        self.minute_hand_path = QPainterPath()
        self.minute_hand_path.moveTo(0, -131)
        self.minute_hand_path.cubicTo(3.5, -60, 3.5, -60, 0, 0)
        self.minute_hand_path.lineTo(-0, 0)
        self.minute_hand_path.cubicTo(-3.5, -60, -3.5, -60, 0, -131)

        self.second_hand = [QPoint(3.5, 30), QPoint(-3.5, 30), QPoint(0, -149)]
        self.chrono_min_hand = [QPoint(3.5, 30), QPoint(-3.5, 30), QPoint(0, -149)]
        self.chrono_sec_hand = [QPoint(1, 28), QPoint(-1, 28), QPoint(0, -135)]

        # ========== 颜色修改 ==========
        # 主表盘内容颜色（刻度、数字、指针）改为深蓝色 (10,25,45)
        self.main_mark_color = QColor(10, 25, 45)
        self.main_hand_color = QColor(10, 25, 45)
        # 指针的银色轮廓保持不变（仍用 silver_outline）
        self.silver_outline = QColor(192, 192, 192)  # 银色
        self.outline_width = 0.5

        # 子表盘内容颜色保持白色+银色
        self.sub_mark_color = QColor(255, 255, 255)
        self.sub_hand_color = QColor(255, 255, 255)
        self.sub_outline = QColor(192, 192, 192)

        # 品牌文字颜色改为黑色
        self.brand_text_color = QColor(0, 0, 0)

        # 主表盘背景色（新增）为近白色
        self.main_dial_bg = QColor(255, 250, 238)

        # 子表盘背景色（6点和12点小盘）改为深蓝色
        self.sub_dial_bg = QColor(10, 25, 45)

        # 以下保持原样（但颜色变量后续会调整使用）
        # 原代码中的 self.hand_color, self.mark_color, self.text_color 不再使用，
        # 我们将它们重新指向新的颜色，以避免修改过多代码结构
        self.hand_color = self.main_hand_color      # 主表盘指针颜色
        self.mark_color = self.main_mark_color      # 主表盘刻度颜色
        self.text_color = self.brand_text_color     # 品牌文字颜色（黑色）

        # 秒针中心圆点参数（子表盘，保持原样）
        self.second_hand1_dot_radius = 10
        self.second_hand1_dot_color = QColor(255, 255, 255)
        self.second_hand2_dot_radius = 5
        self.second_hand2_dot_color = QColor(0, 0, 0)
        self.second_hand3_dot_radius = 3
        self.second_hand3_dot_color = QColor(255, 255, 255)

        # 计时分针中心圆点参数（子表盘，保持原样）
        self.chrono_min_hand1_dot_radius = 10
        self.chrono_min_hand1_dot_color = QColor(255, 255, 255)
        self.chrono_min_hand2_dot_radius = 5
        self.chrono_min_hand2_dot_color = QColor(0, 0, 0)
        self.chrono_min_hand3_dot_radius = 3
        self.chrono_min_hand3_dot_color = QColor(255, 255, 255)

        # 刻度圆点(大) - 主表盘外围圆点，改为深蓝色
        self.scale_line_b_dot_radius = 1.9
        self.scale_line_b_dot_color = self.main_mark_color

        # 刻度圆点(小) - 主表盘外围圆点，改为深蓝色
        self.scale_line_s_dot_radius = 1
        self.scale_line_s_dot_color = self.main_mark_color

        # 针轴美化圆点（中心轴心）保持原样（黑白色）
        self.but1_dot_radius = 3.9
        self.but1_dot_color = QColor(255, 251, 240)
        self.but2_dot_radius = 3.5
        self.but2_dot_color = QColor(0, 0, 0)
        self.but3_dot_radius = 2.0
        self.but3_dot_color = QColor(255, 251, 240)
        self.but4_dot_radius = 1.5
        self.but4_dot_color = QColor(0, 0, 0)

    # ---------- 防息屏 ----------
    def prevent_sleep(self):
        try:
            self.hUser32 = ctypes.windll.kernel32
            self.hUser32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
        except Exception as e:
            print(f"无法阻止休眠: {e}")

    def restore_sleep(self):
        try:
            self.hUser32.SetThreadExecutionState(ES_CONTINUOUS)
        except:
            pass

    def closeEvent(self, event):
        self.restore_sleep()
        event.accept()

    # ---------- 键盘事件 ----------
    def keyPressEvent(self, event):
        current_time = QDateTime.currentMSecsSinceEpoch()
        if event.key() == Qt.Key_Space:
            if not self.chrono_running:
                self.chrono_running = True
                self.chrono_start_time = current_time - self.chrono_paused_time
            else:
                self.chrono_running = False
                self.chrono_paused_time = current_time - self.chrono_start_time
        elif event.key() == Qt.Key_Return:
            self.chrono_running = False
            self.chrono_start_time = 0
            self.chrono_elapsed = 0
            self.chrono_paused_time = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing |
            QPainter.SmoothPixmapTransform |
            QPainter.HighQualityAntialiasing
        )

        min_size = min(self.width(), self.height())
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(min_size / 300, min_size / 300)

        # 绘制主表盘背景（白色圆形）
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.main_dial_bg)
        painter.drawEllipse(QPointF(0, 0), 145, 145)
        painter.restore()

        # 绘制12点及6点位特殊字符（颜色改为深蓝色）
        # 3点矩形
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.main_mark_color)
        rect_width = 2.6
        rect_height = 14.1
        rect_x = -rect_height / 2
        rect_y = -125
        painter.drawRect(QRectF(rect_x, rect_y, rect_width, rect_height))
        painter.restore()

        # 9点椭圆
        painter.save()
        painter.setPen(QPen(self.main_mark_color, 2.6))
        painter.setBrush(Qt.NoBrush)
        ellipse_width = 14.5
        ellipse_height = 10
        ellipse_x = -ellipse_height / 2 - 2.8
        ellipse_y = 98 + ellipse_width
        painter.drawEllipse(QRectF(ellipse_x, ellipse_y, ellipse_width, ellipse_height))
        painter.restore()

        # 6点弧线
        painter.save()
        pen = QPen(self.main_mark_color, 2.5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        arc_rect = QRectF(-8.5, 110.8, 6, 10)
        start_angle = 130 * 16
        span_angle = 131 * 16
        painter.drawArc(arc_rect, start_angle, span_angle)
        painter.restore()

        # 12点弧线
        painter.save()
        pen = QPen(self.main_mark_color, 2.5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        arc_rect = QRectF(-1, -124, 11, 12)
        start_angle = 160 * 16
        span_angle = -230 * 16
        painter.drawArc(arc_rect, start_angle, span_angle)
        painter.restore()

        # 获取当前时间
        time = QTime.currentTime()
        current_time = QDateTime.currentMSecsSinceEpoch()
        if self.chrono_running:
            self.chrono_elapsed = current_time - self.chrono_start_time
        chrono_seconds = self.chrono_elapsed / 1000
        chrono_minutes = chrono_seconds / 60

        # 绘制主表盘刻度、数字（深蓝色）
        self.draw_main_dial(painter)

        # 绘制子表盘（6点位和12点位）背景和内容（深蓝色背景，白色内容）
        self.draw_small_second_dial(painter, time)
        self.draw_chrono_minute_dial(painter, chrono_minutes)

        # 绘制品牌文字（黑色）
        self.draw_brand_text(painter)

        # 绘制计时功能文字（黑色）
        self.draw_chrono_text(painter)

        # 绘制时针和分针（深蓝色主体，银色轮廓）
        self.draw_hour_minute_hands(painter, time)

        # ========== 调整轴心与秒针的层次 ==========
        # 1. 先绘制中心较大的三个圆点（底部白色大圆 + but1, but2, but3）—— 位于秒针下方
        painter.save()
        painter.setPen(Qt.NoPen)
        # 深蓝色底层圆（半径7）
        painter.setBrush(QColor(10, 25, 45))
        painter.drawEllipse(QPointF(0, 0), 7, 7)
        # 较大圆点 but1, but2, but3
        painter.setBrush(self.but1_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.but1_dot_radius, self.but1_dot_radius)
        painter.setBrush(self.but2_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.but2_dot_radius, self.but2_dot_radius)
        painter.setBrush(self.but3_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.but3_dot_radius, self.but3_dot_radius)
        painter.restore()

        # 2. 绘制中央计时秒针（位于较大圆点之上，但被最小圆点覆盖）
        self.draw_chrono_second_hand(painter, chrono_seconds)

        # 3. 绘制最小轴心圆点（but4）—— 位于秒针最上层，覆盖秒针根部
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.but4_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.but4_dot_radius, self.but4_dot_radius)
        # 高光效果（可选）
        highlight = QRadialGradient(0, 0, self.but4_dot_radius)
        highlight.setColorAt(0, QColor(255, 255, 255, 180))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight))
        painter.drawEllipse(QPointF(0, 0), self.but4_dot_radius, self.but4_dot_radius)
        painter.restore()

        # 4. 最后绘制外围刻度圆点（半径131处）—— 远离轴心，不影响层次
        for i in range(12):
            painter.setBrush(self.scale_line_b_dot_color)
            painter.drawEllipse(QPointF(0, 131), self.scale_line_b_dot_radius, self.scale_line_b_dot_radius)
            painter.rotate(30)
        for i in range(60):
            if (i % 5 != 0):
                painter.setBrush(self.scale_line_s_dot_color)
                painter.drawEllipse(QPointF(0, 131), self.scale_line_s_dot_radius, self.scale_line_s_dot_radius)
            painter.rotate(6)

    def draw_main_dial(self, painter):
        # 绘制外圈刻度（颜色已改为深蓝色）
        painter.save()
        painter.setPen(self.mark_color)  # 现在是深蓝色

        # 小时刻度
        for i in range(12):
            painter.drawLine(0, -136, 0, -139)
            painter.rotate(30)

        # 分钟刻度
        for i in range(60):
            if i % 5 != 0:
                painter.drawLine(0, -136, 0, -142)
            painter.rotate(6)

        # 剩余刻度
        for i in range(300):
            painter.drawLine(0, -136, 0, -138)
            painter.rotate(1.2)

        painter.restore()

        # 绘制小时数字 (2.3.4.5.7.8.9)
        painter.save()
        painter.setPen(self.text_color)
        painter.setFont(QFont("Arial", 14.5))  # 使用更大的字体显示小时数字

        hour_numbers = ["12", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
        radius = 112  # 数字距离中心的半径

        for i in range(12):
            if (i == 0):
                continue
            if (i == 1):
                continue
            if (i == 6):
                continue
            if (i == 10):
                continue
            if (i == 11):
                continue
            else:
                angle = 30 * i  # 每个数字间隔30度
                x = radius * sin(radians(angle))
                y = -radius * cos(radians(angle))

                # 保存当前状态
                painter.save()
                # 移动到数字位置
                painter.translate(x, y)
                # 旋转文本使其保持直立
                painter.rotate(angle)
                # 绘制文本（居中）
                painter.rotate(-30 * i)  # 为了保持字体始终朝上
                painter.drawText(QRectF(-15, -15, 30, 30), Qt.AlignCenter, hour_numbers[i])
                # 恢复状态
                painter.restore()

        # 绘制小时数字 (1.11.12)
        painter.save()
        painter.setPen(self.text_color)
        painter.setFont(QFont("Gill Sans MT", 14.5))  # 使用更大的字体显示小时数字

        hour_numbers = ["12", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
        radius = 115  # 数字距离中心的半径

        for i in range(12):
            if (i == 0):
                continue
            if (i == 2):
                continue
            if (i == 3):
                continue
            if (i == 4):
                continue
            if (i == 5):
                continue
            if (i == 6):
                continue
            if (i == 6):
                continue
            if (i == 7):
                continue
            if (i == 8):
                continue
            if (i == 9):
                continue
            else:
                angle = 30 * i  # 每个数字间隔30度
                x = radius * sin(radians(angle))
                y = -radius * cos(radians(angle))

                # 保存当前状态
                painter.save()
                # 移动到数字位置
                painter.translate(x, y)
                # 旋转文本使其保持直立
                painter.rotate(angle)
                # 绘制文本（居中）
                painter.rotate(-30 * i)  # 为了保持字体始终朝上
                painter.drawText(QRectF(-15, -15, 30, 30), Qt.AlignCenter, hour_numbers[i])
                # 恢复状态
                painter.restore()

        painter.restore()

        # 绘制分钟数字（深蓝色）
        painter.save()
        painter.setPen(self.main_mark_color)
        painter.setFont(self.font_main)
        numbers = ["60", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]
        for i in range(12):
            painter.drawText(QRectF(-15, -157, 30, 30), Qt.AlignCenter, numbers[i])
            painter.rotate(30)
        painter.restore()

    def draw_small_second_dial(self, painter, time):
        painter.save()
        painter.translate(0, 63)
        painter.scale(0.3, 0.3)

        # 填充子表盘背景（深蓝色）
        painter.setBrush(self.sub_dial_bg)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(0, 0), 150, 150)

        # 绘制小秒盘外圈（白色）
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self.sub_mark_color)
        painter.drawEllipse(QPointF(0, 0), 150, 150)

        # 绘制刻度（白色）
        for i in range(12):
            painter.drawLine(0, -134, 0, -150)
            painter.rotate(30)

        # 绘制数字（白色）
        painter.setFont(self.font_sub)
        numbers = ["60", "15", "30", "45"]
        for i in range(4):
            painter.drawText(QRectF(-15, -135, 30, 30), Qt.AlignCenter, numbers[i])
            painter.rotate(90)

        # 绘制秒针 - 白银色轮廓 + 白色主体
        painter.setPen(QPen(self.sub_outline, self.outline_width))
        painter.setBrush(Qt.NoBrush)
        painter.rotate(6 * time.second() + 0.006 * time.msec())
        painter.drawConvexPolygon(QPolygonF(self.second_hand))

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.sub_hand_color)
        painter.drawConvexPolygon(QPolygonF(self.second_hand))

        # 指针轴心美化（保持原样）
        painter.setBrush(self.second_hand1_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.second_hand1_dot_radius, self.second_hand1_dot_radius)
        painter.setBrush(self.second_hand2_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.second_hand2_dot_radius, self.second_hand2_dot_radius)
        painter.setBrush(self.second_hand3_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.second_hand3_dot_radius, self.second_hand3_dot_radius)

        painter.restore()

    def draw_chrono_minute_dial(self, painter, chrono_minutes):
        painter.save()
        painter.translate(0, -63)
        painter.scale(0.3, 0.3)

        # 填充子表盘背景（深蓝色）
        painter.setBrush(self.sub_dial_bg)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(0, 0), 150, 150)

        # 绘制计时分针盘外圈（白色）
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self.sub_mark_color)
        painter.drawEllipse(QPointF(0, 0), 150, 150)

        # 绘制刻度（白色）
        for i in range(30):
            if i % 5 == 0:
                painter.drawLine(0, -134, 0, -150)
            else:
                painter.drawLine(0, -140, 0, -150)
            painter.rotate(12)

        # 绘制数字（白色）
        painter.setFont(self.font_sub)
        numbers = ["30", "5", "10", "15", "20", "25"]
        for i in range(6):
            painter.drawText(QRectF(-15, -135, 30, 30), Qt.AlignCenter, numbers[i])
            painter.rotate(60)

        # 绘制计时分针 - 白银色轮廓 + 白色主体
        painter.setPen(QPen(self.sub_outline, self.outline_width))
        painter.setBrush(Qt.NoBrush)
        painter.rotate(12 * floor(chrono_minutes % 30))
        painter.drawConvexPolygon(QPolygonF(self.chrono_min_hand))

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.sub_hand_color)
        painter.drawConvexPolygon(QPolygonF(self.chrono_min_hand))

        # 指针轴心美化（保持原样）
        painter.setBrush(self.chrono_min_hand1_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.chrono_min_hand1_dot_radius, self.chrono_min_hand1_dot_radius)
        painter.setBrush(self.chrono_min_hand2_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.chrono_min_hand2_dot_radius, self.chrono_min_hand2_dot_radius)
        painter.setBrush(self.chrono_min_hand3_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.chrono_min_hand3_dot_radius, self.chrono_min_hand3_dot_radius)

        painter.restore()

    def draw_chrono_second_hand(self, painter, chrono_seconds):
        painter.save()

        # 计时秒针使用主表盘指针颜色（深蓝色）和银色轮廓
        painter.setPen(QPen(self.silver_outline, self.outline_width))
        painter.setBrush(Qt.NoBrush)
        painter.rotate(6 * (chrono_seconds % 60))
        painter.drawConvexPolygon(QPolygonF(self.chrono_sec_hand))

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.main_hand_color)
        painter.drawConvexPolygon(QPolygonF(self.chrono_sec_hand))

        painter.restore()

    def draw_brand_text(self, painter):
        painter.save()
        painter.setPen(self.brand_text_color)  # 黑色

        painter.setFont(self.font_brand)
        painter.drawText(QRectF(12, -19, 100, 30), Qt.AlignCenter, "IMC")

        painter.setFont(self.font_city)
        painter.drawText(QRectF(12, -2.3, 100, 20), Qt.AlignCenter, "SCHEEEHAUSEN")

        painter.restore()

    def draw_chrono_text(self, painter):
        painter.save()
        painter.setPen(self.brand_text_color)  # 黑色
        painter.setFont(self.font_chr)

        painter.drawText(QRectF(-110, -15, 100, 20), Qt.AlignCenter, "CHRNONGREPH")
        painter.drawText(QRectF(-110, -6, 100, 20), Qt.AlignCenter, "A U T O M A T I C")

        painter.setFont(self.font_swiss_made)
        angle = 5
        painter.rotate(angle)
        painter.drawText(QRectF(-52, 118, 100, 20), Qt.AlignCenter, "SWISS")
        angle = -10
        painter.rotate(angle)
        painter.drawText(QRectF(-48, 118.1, 100, 20), Qt.AlignCenter, "MADE")
        angle = 5
        painter.rotate(angle)

        status = "RUNNING" if self.chrono_running else "PAUSED"
        if self.chrono_elapsed == 0:
            status = "READY"
        painter.setFont(QFont("Arial", 3))
        painter.setPen(QColor(255, 251, 240))  # 设置为白色
        painter.drawText(QRectF(110, 135, 150, 20), Qt.AlignCenter, f"SPACE: {status} | ENTER: RESET")
        # 如果后面不需要恢复颜色，可以不用设置回去

        painter.restore()

    def draw_hour_minute_hands(self, painter, time):
        painter.save()

        precise_minute = time.minute() + time.second() / 60.0 + time.msec() / 60000.0
        precise_hour = time.hour() % 12 + precise_minute / 60.0

        # 绘制时针（深蓝色主体，银色轮廓）
        painter.setPen(QPen(self.silver_outline, self.outline_width))
        painter.setBrush(Qt.NoBrush)
        hour_angle = 30 * precise_hour
        painter.rotate(hour_angle)
        painter.drawPath(self.hour_hand_path)
        painter.rotate(-hour_angle)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.main_hand_color)
        painter.rotate(hour_angle)
        painter.drawPath(self.hour_hand_path)
        painter.rotate(-hour_angle)

        # 绘制分针（深蓝色主体，银色轮廓）
        painter.setPen(QPen(self.silver_outline, self.outline_width))
        painter.setBrush(Qt.NoBrush)
        minute_angle = 6 * precise_minute
        painter.rotate(minute_angle)
        painter.drawPath(self.minute_hand_path)
        painter.rotate(-minute_angle)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.main_hand_color)
        painter.rotate(minute_angle)
        painter.drawPath(self.minute_hand_path)

        painter.restore()

    def draw_center(self, painter):
        # 完全保持原样（黑白色轴心圆点）
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.hand_color)  # 这里hand_color现在是深蓝色，但原中心底层是白色，改为白色保持美观
        # 为了不改变原始视觉效果，底层椭圆颜色最好用白色，独立设定
        painter.setBrush(QColor(10, 25, 45))
        painter.drawEllipse(QPointF(0, 0), 7, 7)

        painter.setBrush(self.but1_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.but1_dot_radius, self.but1_dot_radius)
        painter.setBrush(self.but2_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.but2_dot_radius, self.but2_dot_radius)
        painter.setBrush(self.but3_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.but3_dot_radius, self.but3_dot_radius)
        painter.setBrush(self.but4_dot_color)
        painter.drawEllipse(QPointF(0, 0), self.but4_dot_radius, self.but4_dot_radius)
        painter.restore()

        # 外围刻度圆点（深蓝色）
        for i in range(12):
            painter.setBrush(self.scale_line_b_dot_color)
            painter.drawEllipse(QPointF(0, 131), self.scale_line_b_dot_radius, self.scale_line_b_dot_radius)
            painter.rotate(30)
        for i in range(60):
            if (i % 5 != 0):
                painter.setBrush(self.scale_line_s_dot_color)
                painter.drawEllipse(QPointF(0, 131), self.scale_line_s_dot_radius, self.scale_line_s_dot_radius)
            painter.rotate(6)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IMCChrnongreph()
    window.show()
    app.aboutToQuit.connect(window.restore_sleep)
    app.exec_()