from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QSpinBox, QPushButton, QProgressBar,
                           QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from src.controllers.scraper_controller import ScraperController
import pandas as pd
import os
from datetime import datetime

class ScraperThread(QThread):
    finished_signal = pyqtSignal(list)
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    lead_found_signal = pyqtSignal(dict)  # Novo sinal para cada lead encontrado
    progress_signal = pyqtSignal(int)     # Novo sinal para progresso
    
    def __init__(self, nicho, local, quantidade):
        super().__init__()
        self.nicho = nicho
        self.local = local
        self.quantidade = quantidade
        # Importante: criar o controller dentro da thread
        self.controller = None
        
    def run(self):
        try:
            self.controller = ScraperController()
            self.controller.status_updated.connect(self.status_signal.emit)
            self.controller.error_occurred.connect(self.error_signal.emit)
            self.controller.lead_found.connect(self.lead_found_signal.emit)
            self.controller.progress_updated.connect(self.progress_signal.emit)
            self.controller.finished.connect(self.finished_signal.emit)
            
            self.status_signal.emit("Iniciando busca...")
            self.controller.buscar_leads(self.nicho, self.local, self.quantidade)
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if self.controller:
                self.controller.fechar()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Maps Lead Scraper")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #74b9ff;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton#start {
                background-color: #00b894;
            }
            QPushButton#start:hover {
                background-color: #00a885;
            }
            QPushButton#stop {
                background-color: #e17055;
            }
            QPushButton#stop:hover {
                background-color: #d15745;
            }
            QPushButton#save {
                background-color: #0984e3;
            }
            QPushButton#save:hover {
                background-color: #0874d3;
            }
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #dcdde1;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #2c3e50;
            }
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #dcdde1;
                height: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00b894;
                border-radius: 5px;
            }
        """)
        
        # Widget central com margem
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel("Google Maps Lead Scraper")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Container para os inputs
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setSpacing(15)
        
        # Campos de entrada estilizados
        for label_text, placeholder, widget_type in [
            ("Nicho:", "Digite o nicho (ex: restaurantes)", QLineEdit),
            ("Local:", "Digite o local (ex: São Paulo)", QLineEdit),
            ("Quantidade:", "", QSpinBox)
        ]:
            field_layout = QVBoxLayout()
            label = QLabel(label_text)
            
            if widget_type == QLineEdit:
                widget = widget_type()
                widget.setPlaceholderText(placeholder)
            else:
                widget = widget_type()
                widget.setRange(1, 100)
                widget.setValue(10)
            
            field_layout.addWidget(label)
            field_layout.addWidget(widget)
            input_layout.addLayout(field_layout)
            
            if label_text == "Nicho:":
                self.nicho_input = widget
            elif label_text == "Local:":
                self.local_input = widget
            else:
                self.qtd_input = widget
        
        main_layout.addWidget(input_container)
        
        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nome", "Telefone", "Endereço"])
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Pronto para iniciar")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Botões
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar Busca")
        self.stop_button = QPushButton("Parar Busca")
        self.save_button = QPushButton("Salvar Excel")
        
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.save_button)
        main_layout.addLayout(button_layout)
        
        # Botões com IDs
        self.start_button.setObjectName("start")
        self.stop_button.setObjectName("stop")
        self.save_button.setObjectName("save")
        
        # Controller
        self.setup_connections()
        
    def setup_connections(self):
        self.start_button.clicked.connect(self.iniciar_busca)
        self.stop_button.clicked.connect(self.parar_busca)
        self.save_button.clicked.connect(self.salvar_arquivo)
    
    def adicionar_lead(self, lead):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(lead["Nome"]))
        
        # Cria um item de tabela para o telefone/WhatsApp
        telefone_item = QTableWidgetItem(lead["Telefone"])
        if lead["Telefone"].startswith("https://wa.me/"):
            telefone_item.setForeground(QColor("#00b894"))  # Verde para links válidos
        self.table.setItem(row, 1, telefone_item)
        
        self.table.setItem(row, 2, QTableWidgetItem(lead["Endereço"]))
        
    def iniciar_busca(self):
        # Limpa qualquer thread anterior se existir
        if hasattr(self, 'scraper_thread') and self.scraper_thread is not None:
            self.scraper_thread.quit()
            self.scraper_thread.wait()
            self.scraper_thread = None
        
        nicho = self.nicho_input.text().strip()
        local = self.local_input.text().strip()
        quantidade = self.qtd_input.value()
        
        if not nicho or not local:
            self.mostrar_erro("Preencha todos os campos!")
            return
        
        self.table.setRowCount(0)  # Limpa a tabela
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.leads = []  # Limpa a lista de leads
        self.is_scraping = True
        
        # Criar e configurar a thread
        self.scraper_thread = ScraperThread(nicho, local, quantidade)
        self.scraper_thread.finished_signal.connect(self.busca_finalizada)
        self.scraper_thread.status_signal.connect(self.status_label.setText)
        self.scraper_thread.error_signal.connect(self.mostrar_erro)
        self.scraper_thread.lead_found_signal.connect(self.novo_lead_encontrado)
        self.scraper_thread.progress_signal.connect(self.progress_bar.setValue)
        
        # Iniciar a thread
        self.scraper_thread.start()
    
    def busca_finalizada(self, leads):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.is_scraping = False
        
        if hasattr(self, 'scraper_thread'):
            if self.scraper_thread and self.scraper_thread.isRunning():
                self.scraper_thread.quit()
                self.scraper_thread.wait()
            self.scraper_thread = None
        
        self.status_label.setText("Busca interrompida!")

    def salvar_arquivo(self):
        if not self.leads:
            self.mostrar_erro("Não há leads para salvar!")
            return
        
        try:
            # Criar pasta 'leads' se não existir
            if not os.path.exists('leads'):
                os.makedirs('leads')
            
            # Formatar nome do arquivo
            nicho = self.nicho_input.text().strip().lower().replace(" ", "_")
            local = self.local_input.text().strip().lower().replace(" ", "_")
            data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            qtd_leads = len(self.leads)
            
            nome_arquivo = f"leads_{nicho}_{local}_{qtd_leads}_leads_{data_hora}"
            caminho_completo = os.path.join('leads', nome_arquivo)
            
            # Salvar arquivo
            df = pd.DataFrame(self.leads)
            df.to_excel(f"{caminho_completo}.xlsx", index=False)
            
            self.status_label.setText(f"Arquivo salvo com sucesso em: leads/{nome_arquivo}.xlsx")
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar arquivo: {str(e)}")

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, "Erro", mensagem)
        self.start_button.setEnabled(True)

    def novo_lead_encontrado(self, lead):
        self.leads.append(lead)
        self.adicionar_lead(lead)

    def closeEvent(self, event):
        if hasattr(self, 'controller'):
            self.controller.fechar()
        event.accept()

    def parar_busca(self):
        if hasattr(self, 'scraper_thread') and self.scraper_thread.isRunning():
            self.is_scraping = False
            
            if hasattr(self.scraper_thread, 'controller') and self.scraper_thread.controller:
                self.scraper_thread.controller.stop_scraping = True
                self.scraper_thread.controller.fechar()
                
            self.status_label.setText("Parando busca...")
            self.stop_button.setEnabled(False)
            self.save_button.setEnabled(True)
            self.start_button.setEnabled(True)
            
            # Aguarda a thread terminar
            self.scraper_thread.quit()
            self.scraper_thread.wait()
            self.scraper_thread = None 