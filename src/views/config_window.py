from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                           QPushButton, QSpinBox, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt
from dotenv import load_dotenv, set_key
import os

class ConfigWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(600)
        self.setup_ui()
        self.carregar_configuracoes()
        self.setStyleSheet("""
            QDialog {
                background: #0f172a;
            }
            QLabel {
                color: #94a3b8;
                font-size: 14px;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                background: #1e293b;
                border: 1px solid #3b82f6;
                border-radius: 4px;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            #save-button {
                background: #3b82f6;
                color: white;
            }
            #save-button:hover {
                background: #2563eb;
            }
            #cancel-button {
                background: transparent;
                border: 1px solid #ef4444;
                color: #ef4444;
            }
            #cancel-button:hover {
                background: rgba(239, 68, 68, 0.1);
            }
        """)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Cria os campos
        self.send_button = QLineEdit()
        self.chat_loaded = QLineEdit()
        self.compose_box = QLineEdit()
        self.delay_load = QSpinBox()
        self.delay_send = QSpinBox()
        self.delay_between = QSpinBox()
        
        # Adiciona campos ao layout
        form_layout.addRow("Botão Enviar (XPath):", self.send_button)
        form_layout.addRow("Chat Carregado (XPath):", self.chat_loaded)
        form_layout.addRow("Caixa de Mensagem (XPath):", self.compose_box)
        form_layout.addRow("Delay após carregar (s):", self.delay_load)
        form_layout.addRow("Delay após enviar (s):", self.delay_send)
        form_layout.addRow("Delay entre mensagens (s):", self.delay_between)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        save_button = QPushButton("Salvar")
        save_button.setObjectName("save-button")
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("cancel-button")
        
        save_button.clicked.connect(self.save_config)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def carregar_configuracoes(self):
        # Recarrega o arquivo .env
        load_dotenv(override=True)
        
        # Atualiza os valores dos campos
        self.send_button.setText(os.getenv('WHATSAPP_SEND_BUTTON_XPATH', ''))
        self.chat_loaded.setText(os.getenv('WHATSAPP_CHAT_LOADED_XPATH', ''))
        self.compose_box.setText(os.getenv('WHATSAPP_COMPOSE_BOX_XPATH', ''))
        self.delay_load.setValue(int(os.getenv('DELAY_AFTER_LOAD', '2')))
        self.delay_send.setValue(int(os.getenv('DELAY_AFTER_SEND', '3')))
        self.delay_between.setValue(int(os.getenv('DELAY_BETWEEN_MESSAGES', '5')))

    def save_config(self):
        env_path = '.env'
        
        set_key(env_path, 'WHATSAPP_SEND_BUTTON_XPATH', self.send_button.text())
        set_key(env_path, 'WHATSAPP_CHAT_LOADED_XPATH', self.chat_loaded.text())
        set_key(env_path, 'WHATSAPP_COMPOSE_BOX_XPATH', self.compose_box.text())
        set_key(env_path, 'DELAY_AFTER_LOAD', str(self.delay_load.value()))
        set_key(env_path, 'DELAY_AFTER_SEND', str(self.delay_send.value()))
        set_key(env_path, 'DELAY_BETWEEN_MESSAGES', str(self.delay_between.value()))
        
        self.accept() 