from PyQt5.QtCore import QObject, pyqtSignal
from src.models.scraper import GoogleMapsLeadScraper

class ScraperController(QObject):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    lead_found = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.scraper = GoogleMapsLeadScraper()
        self.leads = []
        self.stop_scraping = False

    def buscar_leads(self, nicho, local, quantidade):
        try:
            self.status_updated.emit("Iniciando busca...")
            self.leads = []
            self.stop_scraping = False
            
            for lead in self.scraper.buscar_leads_generator(nicho, local, quantidade):
                if self.stop_scraping:
                    break
                self.leads.append(lead)
                self.lead_found.emit(lead)
                self.progress_updated.emit(int((len(self.leads) / quantidade) * 100))
            
            if self.stop_scraping:
                self.status_updated.emit("Busca interrompida!")
            else:
                self.status_updated.emit("Busca finalizada!")
            self.finished.emit(self.leads)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def salvar_arquivo(self, leads, nome_arquivo):
        try:
            self.scraper.salvar_excel(leads, nome_arquivo)
            self.status_updated.emit(f"Arquivo salvo com sucesso: {nome_arquivo}.xlsx")
        except Exception as e:
            self.error_occurred.emit(f"Erro ao salvar arquivo: {str(e)}")

    def fechar(self):
        self.scraper.fechar()