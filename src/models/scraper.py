from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import urllib.parse
import datetime

class GoogleMapsLeadScraper:
    def __init__(self):
        """
        Inicializa o scraper do Google Maps.
        """
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def buscar_leads(self, nicho, local, quantidade):
        busca = f"{nicho} em {local}"
        self.driver.get("https://www.google.com/maps")
        
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.send_keys(busca)
        search_box.send_keys(Keys.ENTER)
        
        time.sleep(5)
        
        leads = []
        tentativas = 0
        max_tentativas = 50  # Limite máximo de tentativas
        
        while len(leads) < quantidade and tentativas < max_tentativas:
            try:
                items = self.wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a.hfpxzc")))
                
                if not items:
                    tentativas += 1
                    continue
                    
                for i in range(len(items)):
                    if len(leads) >= quantidade:
                        break
                        
                    try:
                        items = self.wait.until(EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "a.hfpxzc")))
                        
                        self.driver.execute_script("arguments[0].click();", items[i])
                        time.sleep(3)
                        
                        nome = self.wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "h1.DUwDvf, div.fontHeadlineLarge"))).text
                        
                        try:
                            telefone_element = self.wait.until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "button[data-tooltip='Copiar número de telefone']")))
                            telefone = telefone_element.get_attribute("aria-label")
                            if telefone:
                                # Remove o prefixo "Copiar número de telefone" e espaços extras
                                telefone = telefone.replace("Copiar número de telefone", "").strip()
                                if telefone.startswith(":"):
                                    telefone = telefone[1:].strip()
                                # Formata e valida o número
                                telefone = self.formatar_numero_whatsapp(telefone, nome)
                        except Exception:
                            try:
                                # Tenta um seletor alternativo
                                telefone_element = self.wait.until(EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "button[data-item-id*='phone']")))
                                telefone = telefone_element.get_attribute("aria-label")
                                if telefone:
                                    telefone = telefone.split(":")[-1].strip()
                            except Exception:
                                telefone = "Não disponível"
                        except:
                            telefone = "Não disponível"
                            
                        try:
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
                        
                        voltar = self.wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button.hYBOP")))
                        self.driver.execute_script("arguments[0].click();", voltar)
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"Erro ao coletar informações: {e}")
                        try:
                            self.driver.execute_script(
                                "document.querySelector('button.hYBOP').click();")
                            time.sleep(2)
                        except:
                            self.driver.get(self.driver.current_url)
                            time.sleep(3)
                        continue
                
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(2)
                tentativas += 1
                
            except Exception as e:
                print(f"Erro ao processar página: {e}")
                self.driver.get(self.driver.current_url)
                time.sleep(3)
                tentativas += 1
        
        if len(leads) < quantidade:
            print(f"Atenção: Foram encontrados apenas {len(leads)} leads dos {quantidade} solicitados.")
        
        return leads

    def buscar_leads_generator(self, nicho, local, quantidade):
        busca = f"{nicho} em {local}"
        self.driver.get("https://www.google.com/maps")
        
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.send_keys(busca)
        search_box.send_keys(Keys.ENTER)
        
        time.sleep(5)
        
        leads_encontrados = 0
        tentativas = 0
        max_tentativas = 50
        
        while leads_encontrados < quantidade and tentativas < max_tentativas:
            try:
                items = self.wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a.hfpxzc")))
                
                if not items:   
                    tentativas += 1
                    continue
                    
                for i in range(len(items)):
                    if leads_encontrados >= quantidade:
                        break
                        
                    try:
                        items = self.wait.until(EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "a.hfpxzc")))
                        self.driver.execute_script("arguments[0].click();", items[i])
                        time.sleep(3)
                        
                        nome = self.wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "h1.DUwDvf, div.fontHeadlineLarge"))).text
                        
                        try:
                            # Tenta diferentes seletores para o telefone
                            try:
                                telefone_element = self.wait.until(EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "button[data-tooltip='Copiar número de telefone']")))
                                telefone = telefone_element.get_attribute("aria-label")
                                if telefone:
                                    # Remove o prefixo "Copiar número de telefone" e espaços extras
                                    telefone = telefone.replace("Copiar número de telefone", "").strip()
                                    if telefone.startswith(":"):
                                        telefone = telefone[1:].strip()
                                    # Formata e valida o número
                                    telefone = self.formatar_numero_whatsapp(telefone, nome)
                            except Exception:
                                # Tenta outro seletor alternativo
                                try:
                                    telefone_element = self.wait.until(EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, "button[data-item-id*='phone']")))
                                    telefone = telefone_element.get_attribute("aria-label")
                                    if telefone:
                                        telefone = telefone.split(":")[-1].strip()
                                except Exception:
                                    telefone = "Não disponível"
                        except:
                            telefone = "Não disponível"
                            
                        try:
                            endereco_element = self.wait.until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "button[data-item-id='address']")))
                            endereco = endereco_element.get_attribute("aria-label").replace("Copiar endereço: ", "")
                        except:
                            endereco = "Não disponível"
                        
                        lead = {
                            "Nome": nome,
                            "Telefone": telefone,
                            "Endereço": endereco
                        }
                        
                        leads_encontrados += 1
                        yield lead
                        
                        voltar = self.wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button.hYBOP")))
                        self.driver.execute_script("arguments[0].click();", voltar)
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"Erro ao coletar informações: {e}")
                        try:
                            self.driver.execute_script(
                                "document.querySelector('button.hYBOP').click();")
                            time.sleep(2)
                        except:
                            self.driver.get(self.driver.current_url)
                            time.sleep(3)
                        continue
                
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(2)
                tentativas += 1
                
            except Exception as e:
                print(f"Erro ao processar página: {e}")
                self.driver.get(self.driver.current_url)
                time.sleep(3)
                tentativas += 1

    def salvar_excel(self, leads, nome_arquivo):
        df = pd.DataFrame(leads)
        df.to_excel(f"{nome_arquivo}.xlsx", index=False)

    def fechar(self):
        self.driver.quit()

    def formatar_numero_whatsapp(self, telefone, nome_empresa):
        if not telefone or telefone == "Não disponível":
            return "Não disponível"
        
        # Remove todos os caracteres não numéricos
        numero = ''.join(filter(str.isdigit, telefone))
        
        if not numero:
            return "Não disponível"
        
        # Validações do número
        if len(numero) < 10 or len(numero) > 15:
            return "Não disponível"
        
        if len(numero) in [10, 11]:
            if not numero.startswith('55'):
                numero = f"55{numero}"
        
        if len(numero) < 12:
            return "Não disponível"
        
        if numero[4] not in '6789':
            return "Não disponível"
        
        # Determina a saudação
        hora_atual = datetime.datetime.now().hour
        if 5 <= hora_atual < 12:
            saudacao = "Bom dia"
        elif 12 <= hora_atual < 18:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"
        
        # Formata a mensagem sem codificação inicial
        mensagem = (
            f"{saudacao}! Acabei de ver a {nome_empresa} no Maps e fiquei pensando... será que já usam IA para: \n\n"
            "→ Automatizar processos repetitivos? (quase 65% dos processos se encaixam aqui) \n"
            "→ Converter mais clientes sem aumentar a equipe? \n"
            "→ Reduzir custos bases do processo dos serviços?\n\n"
            "Se tiver 1 minutinho, mostro como outras empresas parecidas estão fazendo. Me diz o que acha!"
        )
        
        # Usa urllib.parse.quote para codificar corretamente a URL
        mensagem_codificada = urllib.parse.quote(mensagem)
        
        return f"https://wa.me/{numero}?text={mensagem_codificada}"

    def formatar_mensagem_whatsapp(self, nome_empresa):
        hora_atual = datetime.now().hour
        
        if 5 <= hora_atual < 12:
            saudacao = "Bom dia"
        elif 12 <= hora_atual < 18:
            saudacao = "Boa tarde"
        elif 18 <= hora_atual <= 23 or 0 <= hora_atual < 5:
            saudacao = "Boa noite"
        
        # Formata a mensagem com a saudação dinâmica e quebras de linha corretas
        mensagem = (
            f"Boa tarde! Acabei de ver a {nome_empresa} no Maps e fiquei pensando... será que já usam IA para:\n\n"
            "→ Automatizar processos repetitivos? (quase 65% dos processos se encaixam aqui) \n\n"
            "→ Converter mais clientes sem aumentar a equipe? \n\n"
            "→ Reduzir custos bases do processo dos serviços? \n\n"
            "Se tiver 1 minutinho, mostro como outras empresas parecidas estão fazendo. Me diz o que acha!"
        )

        # Codifica a mensagem para URL
        mensagem_codificada = urllib.parse.quote(mensagem)
        
        return f"https://wa.me/{numero}?text={mensagem_codificada}" 