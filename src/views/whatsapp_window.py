from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QFileDialog, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import urllib.parse
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

# Carrega os XPaths do .env
SEND_BUTTON_XPATH = os.getenv('WHATSAPP_SEND_BUTTON_XPATH')
CHAT_LOADED_XPATH = os.getenv('WHATSAPP_CHAT_LOADED_XPATH')
COMPOSE_BOX_XPATH = os.getenv('WHATSAPP_COMPOSE_BOX_XPATH')

class EnviadorWhatsAppThread(QThread):
    progresso_signal = pyqtSignal(str)
    erro_signal = pyqtSignal(str)
    
    def __init__(self, leads):
        super().__init__()
        self.leads = leads
        self.parar_envio = False
        
    def run(self):
        try:
            # Configuração do navegador
            opcoes = Options()
            opcoes.add_argument('--start-maximized')
            opcoes.add_argument('--disable-blink-features=AutomationControlled')
            opcoes.add_argument('--disable-dev-shm-usage')
            opcoes.add_argument('--no-sandbox')
            opcoes.add_argument('--disable-gpu')
            opcoes.add_argument('--remote-debugging-port=9222')
            opcoes.add_argument('--disable-web-security')
            opcoes.add_argument('--allow-running-insecure-content')
            opcoes.add_argument('--disable-extensions')
            opcoes.add_argument('--disable-notifications')
            opcoes.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            opcoes.add_experimental_option('useAutomationExtension', False)
            
            # Adiciona o diretório do perfil do Chrome em um local fixo
            home_dir = os.path.expanduser('~')
            perfil_dir = os.path.join(home_dir, '.chrome_whatsapp_profile')
            
            if not os.path.exists(perfil_dir):
                os.makedirs(perfil_dir)
            
            opcoes.add_argument(f'user-data-dir={perfil_dir}')
            opcoes.add_argument('--profile-directory=Default')
            
            # Usa o webdriver_manager sem especificar o chrome_type
            servico = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=servico, options=opcoes)
            self.wait = WebDriverWait(self.driver, 60)
            
            # Abre WhatsApp Web
            self.driver.get('https://web.whatsapp.com')
            self.progresso_signal.emit("Verificando login no WhatsApp Web...")
            
            for lead in self.leads:
                if self.parar_envio:
                    break
                    
                telefone = lead['Telefone']
                if not telefone.startswith('https://wa.me/'):
                    continue
                    
                try:
                    numero = telefone.split('wa.me/')[1].split('?')[0]
                    mensagem = telefone.split('?text=')[1] if '?text=' in telefone else ''
                    
                    url_completa = f'https://web.whatsapp.com/send?phone={numero}&text={mensagem}'
                    self.driver.get(url_completa)
                    
                    # Espera o campo de mensagem aparecer (indica que o chat carregou)
                    campo_mensagem = self.wait.until(
                        EC.presence_of_element_located((
                            By.XPATH, CHAT_LOADED_XPATH
                        ))
                    )
                    
                    time.sleep(2)  # Pequena pausa para garantir que tudo carregou
                    
                    # Clica no botão de enviar usando o xpath do .env
                    botao_enviar = self.wait.until(
                        EC.element_to_be_clickable((
                            By.XPATH, SEND_BUTTON_XPATH
                        ))
                    )
                    botao_enviar.click()
                    
                    time.sleep(3)
                    self.progresso_signal.emit(f"Mensagem enviada para {lead['Nome']}")
                    time.sleep(5)
                    
                except Exception as e:
                    self.erro_signal.emit(f"Erro ao enviar mensagem para {lead['Nome']}: {str(e)}")
                    continue
                
            self.driver.quit()
            
        except Exception as e:
            self.erro_signal.emit(f"Erro geral: {str(e)}")

    def verificar_botao_enviar(self):
        try:
            # Imprime todos os botões na página
            botoes = self.driver.find_elements(By.TAG_NAME, "button")
            print("Botões encontrados:")
            for botao in botoes:
                print(f"Text: {botao.text}")
                print(f"HTML: {botao.get_attribute('outerHTML')}")
                print(f"Data-testid: {botao.get_attribute('data-testid')}")
                print("---")
            return True
        except Exception as e:
            print(f"Erro ao verificar botões: {str(e)}")
            return False

class WhatsAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.inicializar_ui()
        
    def inicializar_ui(self):
        self.setWindowTitle("Enviador de WhatsApp")
        self.setMinimumSize(900, 600)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout = QVBoxLayout(widget_central)
        
        # Título
        titulo = QLabel("Enviador de Mensagens WhatsApp")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Nome", "WhatsApp", "Endereço"])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabela)
        
        # Barra de progresso
        self.barra_progresso = QProgressBar()
        layout.addWidget(self.barra_progresso)
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        self.botao_carregar = QPushButton("Carregar Excel")
        self.botao_carregar.clicked.connect(self.carregar_excel)
        
        self.botao_enviar = QPushButton("Iniciar Envio")
        self.botao_enviar.clicked.connect(self.iniciar_envio)
        self.botao_enviar.setEnabled(False)
        
        layout_botoes.addWidget(self.botao_carregar)
        layout_botoes.addWidget(self.botao_enviar)
        layout.addLayout(layout_botoes)
        
    def carregar_excel(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if arquivo:
            try:
                df = pd.read_excel(arquivo)
                self.tabela.setRowCount(0)
                
                for idx, linha in df.iterrows():
                    self.tabela.insertRow(idx)
                    self.tabela.setItem(idx, 0, QTableWidgetItem(str(linha['Nome'])))
                    
                    item_telefone = QTableWidgetItem(str(linha['Telefone']))
                    if str(linha['Telefone']).startswith('https://wa.me/'):
                        item_telefone.setForeground(QColor("#00b894"))
                    self.tabela.setItem(idx, 1, item_telefone)
                    
                    self.tabela.setItem(idx, 2, QTableWidgetItem(str(linha['Endereço'])))
                
                self.botao_enviar.setEnabled(True)
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar arquivo: {str(e)}")
    
    def iniciar_envio(self):
        leads_validos = []
        for linha in range(self.tabela.rowCount()):
            telefone = self.tabela.item(linha, 1).text()
            if telefone.startswith('https://wa.me/'):
                leads_validos.append({
                    'Nome': self.tabela.item(linha, 0).text(),
                    'Telefone': telefone,
                    'Endereço': self.tabela.item(linha, 2).text()
                })
        
        if not leads_validos:
            QMessageBox.warning(self, "Aviso", "Nenhum número válido encontrado!")
            return
            
        resposta = QMessageBox.question(
            self,
            'Confirmar Envio',
            'Certifique-se de ter copiado a mensagem.\nDeseja iniciar o envio?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            self.thread_envio = EnviadorWhatsAppThread(leads_validos)
            self.thread_envio.progresso_signal.connect(self.atualizar_status)
            self.thread_envio.erro_signal.connect(self.mostrar_erro)
            self.thread_envio.start()
            self.botao_enviar.setEnabled(False)
            
    def atualizar_status(self, mensagem):
        self.statusBar().showMessage(mensagem)
        
    def mostrar_erro(self, mensagem):
        QMessageBox.warning(self, "Erro", mensagem)
        
    def closeEvent(self, event):
        if hasattr(self, 'thread_envio') and self.thread_envio.isRunning():
            self.thread_envio.parar_envio = True
            self.thread_envio.quit()
            self.thread_envio.wait()
        event.accept()

    def enviar_mensagem(self, chat_input, mensagem):
        try:
            # Digita a mensagem
            chat_input.send_keys(mensagem)
            
            # Clica no botão de enviar usando o seletor correto
            botao_enviar = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']")
            botao_enviar.click()
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar mensagem: {str(e)}")
            return False 