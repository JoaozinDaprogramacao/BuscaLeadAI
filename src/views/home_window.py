from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from .main_window import MainWindow

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LEAD AI")
        self.setMinimumSize(1200, 800)
        
        self.setStyleSheet("""
            QMainWindow {
                background: #0f172a;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                background: #3b82f6;
                border: none;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            #title {
                font-size: 84px;
                font-weight: bold;
                color: white;
                margin: 60px 0 20px 0;
            }
            #subtitle {
                font-size: 24px;
                color: #94a3b8;
                margin-bottom: 80px;
            }
            #feature-card {
                background: rgba(30, 41, 59, 0.5);
                border-radius: 16px;
                padding: 60px;
                margin: 20px;
                border: 1px solid rgba(148, 163, 184, 0.1);
                min-width: 400px;
            }
            #feature-card:hover {
                border: 1px solid #3b82f6;
                background: rgba(30, 41, 59, 0.8);
            }
            #card-title {
                font-size: 28px;
                font-weight: bold;
                color: #3b82f6;
                margin-bottom: 20px;
            }
            #card-description {
                font-size: 16px;
                color: #94a3b8;
                line-height: 1.6;
                margin-bottom: 30px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(0)
        
        # Header
        header = QVBoxLayout()
        title = QLabel("LEAD AI")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Sua plataforma inteligente de prospecção de leads")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)
        
        # Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        
        # Google Maps Card
        maps_card = QWidget()
        maps_card.setObjectName("feature-card")
        maps_layout = QVBoxLayout(maps_card)
        maps_layout.setContentsMargins(20, 20, 20, 20)
        maps_layout.setSpacing(30)
        
        maps_title = QLabel("Google Maps Scraper")
        maps_title.setObjectName("card-title")
        
        maps_desc = QLabel("Extraia leads automaticamente do Google Maps com informações de contato e localização")
        maps_desc.setObjectName("card-description")
        maps_desc.setWordWrap(True)
        
        maps_button = QPushButton("Acessar Scraper")
        maps_button.setCursor(Qt.PointingHandCursor)
        maps_button.clicked.connect(self.abrir_scraper)
        
        maps_layout.addWidget(maps_title)
        maps_layout.addWidget(maps_desc)
        maps_layout.addStretch()
        maps_layout.addWidget(maps_button, alignment=Qt.AlignLeft)
        cards_layout.addWidget(maps_card)
        
        # WhatsApp Card
        whatsapp_card = QWidget()
        whatsapp_card.setObjectName("feature-card")
        whatsapp_layout = QVBoxLayout(whatsapp_card)
        whatsapp_layout.setContentsMargins(20, 20, 20, 20)
        whatsapp_layout.setSpacing(30)
        
        whatsapp_title = QLabel("Enviar Mensagens")
        whatsapp_title.setObjectName("card-title")
        
        whatsapp_desc = QLabel("Envie mensagens personalizadas para seus leads através do WhatsApp Web de forma organizada")
        whatsapp_desc.setObjectName("card-description")
        whatsapp_desc.setWordWrap(True)
        
        whatsapp_button = QPushButton("Acessar WhatsApp Sender")
        whatsapp_button.setCursor(Qt.PointingHandCursor)
        whatsapp_button.clicked.connect(self.abrir_whatsapp)
        
        whatsapp_layout.addWidget(whatsapp_title)
        whatsapp_layout.addWidget(whatsapp_desc)
        whatsapp_layout.addStretch()
        whatsapp_layout.addWidget(whatsapp_button, alignment=Qt.AlignLeft)
        cards_layout.addWidget(whatsapp_card)
        
        layout.addLayout(cards_layout)
        
    def abrir_scraper(self):
        self.scraper_window = MainWindow()
        self.scraper_window.show()

    def abrir_whatsapp(self):
        from src.views.whatsapp_window import WhatsAppWindow
        self.whatsapp_window = WhatsAppWindow()
        self.whatsapp_window.show() 