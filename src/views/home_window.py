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
            #config-button {
                background: transparent;
                border: 2px solid #3b82f6;
                color: #3b82f6;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            #config-button:hover {
                background: rgba(59, 130, 246, 0.1);
                border-color: #60a5fa;
                color: #60a5fa;
            }
            #back-button {
                background: transparent;
                border: none;
                color: #3b82f6;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                margin: 10px;
            }
            #back-button:hover {
                color: #60a5fa;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 6px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(0)
        
        # Header com título e botão de configurações
        header_layout = QHBoxLayout()
        
        # Container para título e subtítulo
        title_container = QVBoxLayout()
        title = QLabel("LEAD AI")
        title.setObjectName("title")
        subtitle = QLabel("Sua plataforma inteligente de prospecção de leads")
        subtitle.setObjectName("subtitle")
        
        title_container.addWidget(title, alignment=Qt.AlignLeft)
        title_container.addWidget(subtitle, alignment=Qt.AlignLeft)
        header_layout.addLayout(title_container)
        
        # Botão de configurações
        config_button = QPushButton("⚙️ Configurações")
        
        config_button.setObjectName("config-button")
        config_button.setCursor(Qt.PointingHandCursor)
        config_button.clicked.connect(self.abrir_configuracoes)
        header_layout.addWidget(config_button, alignment=Qt.AlignRight | Qt.AlignTop)
        
        layout.addLayout(header_layout)
        
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
        
        self.current_window = None  # Armazena a janela atual
        
    def abrir_scraper(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = MainWindow()
        self.setCentralWidget(self.current_window)

    def abrir_whatsapp(self):
        if self.current_window:
            self.current_window.close()
        from src.views.whatsapp_window import WhatsAppWindow
        self.current_window = WhatsAppWindow()
        self.setCentralWidget(self.current_window)

    def abrir_configuracoes(self):
        from src.views.config_window import ConfigWindow
        config_window = ConfigWindow(self)
        config_window.exec_() 