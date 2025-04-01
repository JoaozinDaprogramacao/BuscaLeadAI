from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import urllib.parse
import datetime
import os
from dotenv import load_dotenv
import re

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
                            print("\n=== Iniciando coleta de telefone ===")
                            
                            # Tenta encontrar o elemento do telefone usando XPath
                            try:
                                telefone_element = self.wait.until(
                                    EC.presence_of_element_located((
                                        By.XPATH, 
                                        '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[6]/button/div/div[2]/div[1]'
                                    ))
                                )
                                
                                # Tenta clicar no elemento pai
                                try:
                                    botao_pai = telefone_element.find_element(By.XPATH, ".//ancestor::button")
                                    self.driver.execute_script("arguments[0].click();", botao_pai)
                                    time.sleep(1)
                                except:
                                    pass
                                
                                # Obtém o texto do elemento
                                telefone = telefone_element.text
                                if not telefone:
                                    telefone = self.driver.execute_script(
                                        "return arguments[0].textContent;", 
                                        telefone_element
                                    )
                                
                                print(f"Telefone encontrado: {telefone}")
                                
                                # Limpa o número
                                if telefone:
                                    telefone = telefone.strip()
                                    print(f"Telefone após limpeza: {telefone}")
                                else:
                                    telefone = "Não disponível"
                            except Exception as e:
                                print(f"Erro ao encontrar telefone: {str(e)}")
                                telefone = "Não disponível"
                        except Exception as e:
                            print(f"Erro geral: {str(e)}")
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
                        
                        # Tenta obter o telefone com diferentes seletores
                        try:
                            # Primeiro tenta o seletor do botão de copiar telefone
                            telefone_element = self.wait.until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "button[data-item-id*='phone:tel']")))
                            telefone = telefone_element.get_attribute("aria-label") or telefone_element.text
                            
                            if not telefone:
                                # Tenta outro seletor comum
                                telefone_element = self.wait.until(EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "button[data-tooltip='Copiar número de telefone']")))
                                telefone = telefone_element.get_attribute("aria-label")
                            
                            if telefone:
                                if "Copiar número de telefone" in telefone:
                                    telefone = telefone.replace("Copiar número de telefone", "").strip()
                                    if telefone.startswith(":"):
                                        telefone = telefone[1:].strip()
                                elif ":" in telefone:
                                    telefone = telefone.split(":")[-1].strip()
                                
                                # Formata o número para URL do WhatsApp
                                if telefone != "Não disponível":
                                    telefone = self.formatar_numero_whatsapp(telefone, nome)
                        except Exception as e:
                            print(f"Erro ao coletar telefone: {e}")
                            telefone = "Não disponível"
                        
                        # Tenta obter o endereço
                        try:
                            endereco_element = self.wait.until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "button[data-item-id='address']")))
                            endereco = endereco_element.get_attribute("aria-label").replace("Copiar endereço: ", "")
                        except Exception:
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
        
        # Remove caracteres não numéricos
        numero = ''.join(filter(str.isdigit, telefone))
        
        if not numero or len(numero) < 10:
            return "Não disponível"
        
        # Adiciona código do país se necessário
        if len(numero) in [10, 11] and not numero.startswith('55'):
            numero = f"55{numero}"
        
        # Carrega o template e formata a mensagem
        load_dotenv()
        mensagem = (
            "Boa tarde! Acabei de ver a {nome_empresa} no Maps e fiquei pensando... será que já usam IA para:\n\n"
            "→ Automatizar processos repetitivos? (quase 65% dos processos se encaixam aqui)\n"
            "→ Converter mais clientes sem aumentar a equipe?\n"
            "→ Reduzir custos bases do processo dos serviços?\n\n"
            "Se tiver 1 minutinho, mostro como outras empresas parecidas estão fazendo. Me diz o que acha!"
        ).format(nome_empresa=nome_empresa)
        
        # Codifica a mensagem para URL
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