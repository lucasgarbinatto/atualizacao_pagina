import requests
import schedule
import time
import hashlib
import json
from bs4 import BeautifulSoup

# Configuração da página a ser monitorada
page_url = "https://presencial.moodle.ufsc.br/mod/attendance/view.php?id=654493"

# Arquivo para armazenar os cookies (você vai criar este arquivo)
cookies_file = "moodle_cookies.json"

previous_hash = None

def load_cookies():
    try:
        with open(cookies_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo de cookies '{cookies_file}' não encontrado.")
        print("Por favor, siga as instruções abaixo para criar este arquivo:")
        print("1. Faça login manualmente no Moodle usando seu navegador")
        print("2. Instale a extensão 'EditThisCookie' ou similar")
        print("3. Vá até a página do Moodle e exporte os cookies para JSON")
        print("4. Salve o arquivo como 'moodle_cookies.json' na mesma pasta deste script")
        return None

def check_page_modification():
    global previous_hash
    cookies = load_cookies()
    
    if not cookies:
        print("Não foi possível continuar sem os cookies.")
        return
    
    # Criar uma sessão e adicionar os cookies do navegador
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    
    try:
        response = session.get(page_url, timeout=15)
        response.raise_for_status()
        
        if "login/index.php" in response.url:
            print("Erro: Você foi redirecionado para a página de login.")
            print("Os cookies podem ter expirado. Faça login manualmente novamente.")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content_area = soup.find('div', role='main')
        if not content_area:
            content_area = soup.find('table', class_='generaltable')
        content_text = content_area.get_text(separator=' ', strip=True) if content_area else response.text
        current_hash = hashlib.md5(content_text.encode('utf-8')).hexdigest()
        
        if previous_hash is None:
            previous_hash = current_hash
            print(f"Primeira verificação da página {page_url}. Conteúdo armazenado.")
        elif current_hash != previous_hash:
            for _ in range(5):
                print(f"!!! ALTERAÇÃO DETECTADA NA PÁGINA {page_url} !!!")
            print("Verifique a página para ver as mudanças.")
            previous_hash = current_hash
        else:
            print(f"Nenhuma alteração detectada na página {page_url}.")
    except Exception as e:
        print(f"Erro durante a verificação da página: {str(e)}")

# --- Início da Execução ---
print("Iniciando monitoramento usando cookies do navegador...")
check_page_modification()  # Primeira verificação
schedule.every(1).minutes.do(check_page_modification)
print("Script iniciado. Verificando a página a cada minuto...")

while True:
    schedule.run_pending()
    time.sleep(1)