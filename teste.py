from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os


class GoogleMapsLeadScraper:
    def __init__(self):
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def buscar_leads(self, nicho, local, quantidade):
        # Formata a busca
        busca = f"{nicho} em {local}"

        # Acessa o Google Maps
        self.driver.get("https://www.google.com/maps")

        # Localiza e preenche o campo de busca
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.send_keys(busca)
        search_box.send_keys(Keys.ENTER)

        time.sleep(5)  # Aguarda o carregamento dos resultados

        leads = []
        while len(leads) < quantidade:
            try:
                # Seletor atualizado para os resultados da lista
                items = self.wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a.hfpxzc")))  # Alterado para o link direto

                for i in range(len(items)):
                    if len(leads) >= quantidade:
                        break

                    try:
                        # Busca os itens novamente para evitar referência obsoleta
                        items = self.wait.until(EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "a.hfpxzc")))

                        # Usa JavaScript para clicar no elemento, evitando interceptação
                        self.driver.execute_script("arguments[0].click();", items[i])
                        time.sleep(3)

                        # Coleta o nome da empresa
                        nome = self.wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "h1.DUwDvf, div.fontHeadlineLarge"))).text

                        # Verifica se a empresa já existe em alguma planilha
                        if self.verificar_duplicata(nome):
                            print(f"Empresa '{nome}' já existe em uma planilha. Pulando...")
                            # Volta para a lista de resultados
                            voltar = self.wait.until(EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, "button.hYBOP")))
                            self.driver.execute_script("arguments[0].click();", voltar)
                            time.sleep(2)
                            continue

                        # Continua com a coleta dos dados se não for duplicata
                        try:
                            telefone_element = self.driver.find_element(By.CSS_SELECTOR,
                                                                    "button[data-item-id='phone:tel']")
                            telefone = telefone_element.get_attribute("aria-label") or telefone_element.text
                            if "Copiar número de telefone" in telefone:
                                telefone = telefone.replace("Copiar número de telefone: ", "")
                        except:
                            telefone = "Não disponível"

                        try:
                            # Seletor atualizado para endereço
                            endereco_element = self.driver.find_element(By.CSS_SELECTOR,
                                                                        "button[data-item-id='address']")
                            endereco = endereco_element.get_attribute("aria-label") or endereco_element.text
                            if "Copiar endereço" in endereco:
                                endereco = endereco.replace("Copiar endereço: ", "")
                        except:
                            endereco = "Não disponível"

                        leads.append({
                            "Nome": nome,
                            "Telefone": telefone,
                            "Endereço": endereco
                        })

                        # Volta para a lista de resultados usando JavaScript
                        voltar = self.wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button.hYBOP")))
                        self.driver.execute_script("arguments[0].click();", voltar)
                        time.sleep(2)

                    except Exception as e:
                        print(f"Erro ao coletar informações: {e}")
                        # Tenta voltar à lista de resultados se houver erro
                        try:
                            # Tenta fechar qualquer modal ou voltar à lista
                            self.driver.execute_script(
                                "document.querySelector('button.hYBOP').click();")
                            time.sleep(2)
                        except:
                            # Se falhar, tenta recarregar a página
                            self.driver.get(self.driver.current_url)
                            time.sleep(3)
                        continue

                # Método alternativo para rolar a lista de resultados
                self.driver.execute_script(
                    "window.scrollBy(0, 500);")
                time.sleep(2)

            except Exception as e:
                print(f"Erro ao processar página: {e}")
                # Tenta recarregar a página em caso de erro
                self.driver.get(self.driver.current_url)
                time.sleep(3)

        return leads

    def salvar_excel(self, leads, nome_arquivo):
        df = pd.DataFrame(leads)
        df.to_excel(f"{nome_arquivo}.xlsx", index=False)

    def fechar(self):
        self.driver.quit()

    def verificar_duplicata(self, nome_empresa, pasta_leads="leads"):
        """
        Verifica se uma empresa já existe em alguma planilha na pasta de leads
        """
        try:
            # Verifica se a pasta existe
            if not os.path.exists(pasta_leads):
                return False
            
            # Lista todos os arquivos Excel na pasta
            arquivos_excel = [f for f in os.listdir(pasta_leads) if f.endswith(('.xlsx', '.xls'))]
            
            for arquivo in arquivos_excel:
                caminho_completo = os.path.join(pasta_leads, arquivo)
                try:
                    df = pd.read_excel(caminho_completo)
                    if 'Nome' in df.columns:
                        # Verifica se o nome da empresa existe (ignorando maiúsculas/minúsculas)
                        if df['Nome'].str.lower().str.contains(nome_empresa.lower()).any():
                            return True
                except Exception as e:
                    print(f"Erro ao ler arquivo {arquivo}: {str(e)}")
                    continue
                
            return False
        
        except Exception as e:
            print(f"Erro ao verificar duplicatas: {str(e)}")
            return False


# Exemplo de uso
if __name__ == "__main__":
    scraper = GoogleMapsLeadScraper()

    nicho = input("Digite o nicho (exemplo: restaurantes): ")
    local = input("Digite o local (exemplo: São Paulo): ")
    quantidade = int(input("Digite a quantidade de leads desejada: "))

    print("\nBuscando leads... Por favor, aguarde...")
    leads = scraper.buscar_leads(nicho, local, quantidade)

    nome_arquivo = f"leads_{nicho}_{local}".replace(" ", "_")
    scraper.salvar_excel(leads, nome_arquivo)

    print(f"\nForam encontrados {len(leads)} leads!")
    print(f"Os dados foram salvos no arquivo: {nome_arquivo}.xlsx")

    scraper.fechar()