import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QMovie, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtCore import QPoint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Backend import state


# ================= PATH =================
def Graphics(file):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join( BASE_DIR, "Graphics", file)


# ================= TOP BAR =================
class TopBar(QWidget):
    def __init__(self, parent, stack):
        super().__init__(parent)

        self.parent = parent
        self.stack = stack

        self.setFixedHeight(50)
        self.setStyleSheet("background:#f5f5f5;")

       
        self._drag_active = False
        self._drag_pos = QPoint()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)

        # LEFT
        title = QLabel("Nova AI")
        title.setStyleSheet("color:black;font-size:15px;font-weight:500;")

        # CENTER
        center = QHBoxLayout()

        def nav_btn(text, icon, index):
            btn = QPushButton(f"  {text}")
            btn.setIcon(QIcon(Graphics(icon)))
            btn.setIconSize(QSize(16, 16))
            btn.setStyleSheet("""
                QPushButton {
                    background: #ffffff;
                    border:1px solid #ccc;
                    border-radius:5px;
                    padding:6px 12px;
                }
                QPushButton:hover {
                    background:#eaeaea;
                }
            """)
            btn.clicked.connect(lambda: self.switch(index))
            return btn

        center.addWidget(nav_btn("Home", "Home.png", 0))
        center.addSpacing(10)
        center.addWidget(nav_btn("Chat", "Chats.png", 1))

        # RIGHT
        right = QHBoxLayout()

        def win_btn(icon, func):
            btn = QPushButton()
            btn.setIcon(QIcon(Graphics(icon)))
            btn.setIconSize(QSize(14, 14))
            btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 5px;
            }
            QPushButton:hover {
                background: rgba(0,0,0,0.1);
                border-radius: 4px;
            }
            """)
            btn.clicked.connect(func)
            return btn

        right.addWidget(win_btn("Minimize2.png", self.parent.showMinimized))
        right.addWidget(win_btn("Maximize.png", self.toggle_max))
        right.addWidget(win_btn("Close.png", self.parent.close))

        # ALIGNMENT
        layout.addWidget(title)
        layout.addStretch()
        layout.addLayout(center)
        layout.addStretch()
        layout.addLayout(right)

    def switch(self, index):
        state.ui_mode = "home" if index == 0 else "chat"
        self.stack.setCurrentIndex(index)

    def toggle_max(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()


    def mouseMoveEvent(self, event):
        if self._drag_active:

            if self.window().isMaximized():
                self.window().showNormal()

            self.window().move(event.globalPos() - self._drag_pos)
            event.accept()


    def mouseReleaseEvent(self, event):
        self._drag_active = False



# ================= HOME SCREEN =================
class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()

        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        self.setStyleSheet("background:black;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # ORB
        self.orb = QLabel()
        movie = QMovie(Graphics("Nova.gif"))
       # max_gif_size_H = int(screen_width / 16 * 9)
        size = int(screen_width/3)
        movie.setScaledSize(QSize(size*3, int(size*1.5)))
        self.orb.setMovie(movie)
        movie.start()

        # MIC
        self.mic = QLabel()
        self.mic.setFixedSize(150, 150)
        self.mic.setAlignment(Qt.AlignCenter)
        self.mic.mousePressEvent = self.toggle_mic

        # STATUS
        self.status = QLabel("Available...")
        self.status.setStyleSheet("color:white;font-size:14px;")

        layout.addWidget(self.orb,alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.mic,alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self.status,alignment=Qt.AlignCenter)

        # UPDATE LOOP
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateUI)
        self.timer.start(200)

    def updateUI(self):
        self.status.setText(state.assistant_status)

        icon = "Mic_on.png" if state.mic_status else "Mic_off.png"
        pix = QPixmap(Graphics(icon)).scaled(100, 100, Qt.KeepAspectRatio)
        self.mic.setPixmap(pix)

    def toggle_mic(self, e=None):
        state.mic_status = not state.mic_status
    
    

# ================= CHAT SCREEN =================
class ChatScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background:black;")

        # ✅ MAIN LAYOUT (ONLY ONE)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ================= LEFT (CHAT) =================
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("""
            background:black;
            color:white;
            border:none;
            font-size:14px;
        """)

        # ================= RIGHT (ORB) =================
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border:none;")

        movie = QMovie(Graphics("Nova.gif"))
        movie.setScaledSize(QSize(250, 250))
        self.gif_label.setMovie(movie)
        movie.start()

        right_layout = QVBoxLayout()
        right_layout.addStretch()
        right_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)
        right_layout.addStretch()

        # ================= FINAL STRUCTURE =================
        main_layout.addWidget(self.chat, 3)
        main_layout.addLayout(right_layout, 1)

        # ================= STATE UPDATE =================
        self.last = ""

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateUI)
        self.timer.start(200)

    def updateUI(self):
        if state.latest_response != self.last:
            self.chat.append(state.latest_response)
            self.last = state.latest_response

# ================= MAIN WINDOW =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background:black;")

        container = QWidget()
        layout = QVBoxLayout(container)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # STACK
        self.stack = QStackedWidget()
        self.home = HomeScreen()
        self.chat = ChatScreen()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.chat)

        # TOP BAR
        self.topbar = TopBar(self, self.stack)

        layout.addWidget(self.topbar)
        layout.addWidget(self.stack)

        self.setCentralWidget(container)
        self.showMaximized()

        # AUTO UI SWITCH
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateUI)
        self.timer.start(200)

    def updateUI(self):
        if state.ui_mode == "chat":
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)


# ================= ENTRY =================
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()