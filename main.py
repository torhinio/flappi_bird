import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMessageBox, QVBoxLayout
from PyQt5.QtGui import QPainter, QPixmap, QFont, QPen
from PyQt5.QtCore import Qt, QTimer


class FlappyBird(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flappy Bird - PyQt5 Edition")
        self.setFixedSize(400, 600)

        # Bird
        self.bird_x = 100
        self.bird_y = 250
        self.velocity = 0
        self.gravity = 1
        self.lift = -10

        # Pipes
        self.pipe_x = 400
        self.pipe_width = 52
        self.pipe_gap = 150
        self.pipe_speed = 4
        self.pipe_top_height = random.randint(100, 300)

        # Score
        self.score = 0
        self.high_score = 0
        self.passed_pipe = False

        # Game state
        self.game_running = False
        self.in_start_menu = True

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)

        self.flap_timer = QTimer()
        self.flap_timer.timeout.connect(self.toggle_flap)
        self.flap_timer.start(150)

        # Bird animation
        self.flap_index = 0
        self.bird_frames = [
            QPixmap("assets/yellowbird-upflap.png"),
            QPixmap("assets/yellowbird-midflap.png"),
            QPixmap("assets/yellowbird-downflap.png")
        ]

        # Images
        self.bg = QPixmap("assets/background-day.png")
        self.pipe_img = QPixmap("assets/pipe-green.png")
        self.base_img = QPixmap("assets/base.png")

        # Pause button
        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setGeometry(300, 20, 80, 30)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.hide()

        # Pause menu
        self.pause_overlay = QWidget(self)
        self.pause_overlay.setGeometry(0, 0, self.width(), self.height())
        self.pause_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 180);")
        self.pause_overlay.hide()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.pause_label = QLabel("PAUSED")
        self.pause_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")
        layout.addWidget(self.pause_label)

        button_style = """
            QPushButton {
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #5555FF;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #3333CC;
            }
        """

        resume_btn = QPushButton("Resume")
        resume_btn.setStyleSheet(button_style)
        resume_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(resume_btn)

        restart_btn = QPushButton("Restart")
        restart_btn.setStyleSheet(button_style)
        restart_btn.clicked.connect(self.restart_game)
        layout.addWidget(restart_btn)

        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet(button_style.replace('#5555FF', '#FF4444').replace('#3333CC', '#CC2222'))
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        self.pause_overlay.setLayout(layout)

        # Start menu
        self.start_overlay = QWidget(self)
        self.start_overlay.setGeometry(0, 0, self.width(), self.height())
        self.start_overlay.setStyleSheet("background-image: url('assets/background-day.png');")

        start_layout = QVBoxLayout()
        start_layout.setAlignment(Qt.AlignCenter)
        start_layout.setContentsMargins(50, 200, 50, 200)

        start_label = QLabel("FLAPPY BIRD")
        start_label.setStyleSheet("""
            color: white;
            font-size: 48px;
            font-weight: bold;
        """)
        start_label.setAlignment(Qt.AlignCenter)
        start_layout.addWidget(start_label)

        start_btn = QPushButton("Start Game")
        start_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: #FFA500;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
        """)
        start_btn.clicked.connect(self.start_game)
        start_layout.addWidget(start_btn)

        self.start_overlay.setLayout(start_layout)

    def toggle_flap(self):
        self.flap_index = (self.flap_index + 1) % len(self.bird_frames)
        self.update()

    def start_game(self):
        self.in_start_menu = False
        self.start_overlay.hide()
        self.pause_button.show()
        self.reset_game()
        self.timer.start(20)
        self.game_running = True

    def toggle_pause(self):
        if self.game_running:
            self.timer.stop()
            self.pause_overlay.show()
        else:
            self.pause_overlay.hide()
            self.timer.start(20)
        self.game_running = not self.game_running

    def reset_game(self):
        self.bird_y = 250
        self.velocity = 0
        self.pipe_x = 400
        self.pipe_top_height = random.randint(100, 300)
        self.score = 0
        self.passed_pipe = False
        self.game_running = True
        self.pause_overlay.hide()

    def restart_game(self):
        self.reset_game()
        self.timer.start(20)

    def game_loop(self):
        self.velocity += self.gravity
        self.bird_y += self.velocity
        self.pipe_x -= self.pipe_speed

        if self.pipe_x + self.pipe_width < 0:
            self.pipe_x = self.width()
            self.pipe_top_height = random.randint(100, 300)
            self.passed_pipe = False

        if self.pipe_x + self.pipe_width < self.bird_x and not self.passed_pipe:
            self.score += 1
            self.passed_pipe = True
            self.high_score = max(self.high_score, self.score)

        if (self.bird_y + 24 > 500 or self.bird_y < 0 or
            (self.pipe_x < self.bird_x + 34 < self.pipe_x + self.pipe_width and
             (self.bird_y < self.pipe_top_height or self.bird_y + 24 > self.pipe_top_height + self.pipe_gap))):
            self.timer.stop()
            reply = QMessageBox.question(
                self, "Game Over",
                f"Your Score: {self.score}\nHigh Score: {self.high_score}\nPlay again?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.restart_game()
            else:
                self.close()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.velocity = self.lift
        elif event.key() == Qt.Key_Escape:
            self.toggle_pause()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Background
        painter.drawPixmap(0, 0, self.width(), self.height(), self.bg)

        # Pipes
        painter.drawPixmap(self.pipe_x, 0, self.pipe_width, self.pipe_top_height, self.pipe_img)
        painter.drawPixmap(
            self.pipe_x, self.pipe_top_height + self.pipe_gap,
            self.pipe_width, self.height() - (self.pipe_top_height + self.pipe_gap),
            self.pipe_img
        )

        # Ground/Base
        painter.drawPixmap(0, 500, self.width(), 100, self.base_img)

        # Bird
        painter.drawPixmap(self.bird_x, self.bird_y, 34, 24, self.bird_frames[self.flap_index])

        # Score
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        painter.setPen(QPen(Qt.white))
        painter.drawText(20, 40, f"Score: {self.score}")
        painter.drawText(20, 70, f"Best: {self.high_score}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlappyBird()
    window.show()
    sys.exit(app.exec_())
