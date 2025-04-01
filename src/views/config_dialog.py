from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt
import os
from dotenv import load_dotenv, set_key

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Carrega as configurações atuais
        load_dotenv()
        
        # XPath inputs
        self.send_button = QLineEdit(os.getenv('WHATSAPP_SEND_BUTTON_XPATH', ''))
        self.chat_loaded = QLineEdit(os.getenv('WHATSAPP_CHAT_LOADED_XPATH', ''))
        self.compose_box = QLineEdit(os.getenv('WHATSAPP_COMPOSE_BOX_XPATH', ''))
        
        # Delay inputs
        self.delay_load = QSpinBox()
        self.delay_load.setValue(int(os.getenv('DELAY_AFTER_LOAD', '2')))
        self.delay_send = QSpinBox()
        self.delay_send.setValue(int(os.getenv('DELAY_AFTER_SEND', '3')))
        self.delay_between = QSpinBox()
        self.delay_between.setValue(int(os.getenv('DELAY_BETWEEN_MESSAGES', '5')))
        
        # Adiciona campos ao layout
        form_layout.addRow("Botão Enviar (XPath):", self.send_button)
        form_layout.addRow("Chat Carregado (XPath):", self.chat_loaded)
        form_layout.addRow("Caixa de Mensagem (XPath):", self.compose_box)
        form_layout.addRow("Delay após carregar (s):", self.delay_load)
        form_layout.addRow("Delay após enviar (s):", self.delay_send)
        form_layout.addRow("Delay entre mensagens (s):", self.delay_between)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Salvar")
        cancel_button = QPushButton("Cancelar")
        
        save_button.clicked.connect(self.save_config)
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

    def save_config(self):
        # Atualiza o arquivo .env
        env_path = '.env'
        
        set_key(env_path, 'WHATSAPP_SEND_BUTTON_XPATH', self.send_button.text())
        set_key(env_path, 'WHATSAPP_CHAT_LOADED_XPATH', self.chat_loaded.text())
        set_key(env_path, 'WHATSAPP_COMPOSE_BOX_XPATH', self.compose_box.text())
        set_key(env_path, 'DELAY_AFTER_LOAD', str(self.delay_load.value()))
        set_key(env_path, 'DELAY_AFTER_SEND', str(self.delay_send.value()))
        set_key(env_path, 'DELAY_BETWEEN_MESSAGES', str(self.delay_between.value()))
        
        self.accept() 