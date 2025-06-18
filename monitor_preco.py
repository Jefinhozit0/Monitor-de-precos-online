import requests
from bs4 import BeautifulSoup
import time
import csv # Importe a biblioteca csv
from datetime import datetime # Importe datetime para pegar a data e hora atual
import schedule

# --- Configurações Iniciais ---
# !!! IMPORTANTE: SUBSTITUA ESTA URL PELA URL DO SEU PRODUTO REAL DA AMAZON !!!
URL_PRODUTO = "https://www.amazon.com.br/Echo-Dot-5%C2%AA-gera%C3%A7%C3%A3o-Cor-Preta/dp/B09B8VGCR8/?_encoding=UTF8&pd_rd_w=Uyk7p&content-id=amzn1.sym.8fbb3d34-c3f1-46af-9d99-fd6986f6ec8f&pf_rd_p=8fbb3d34-c3f1-46af-9d99-fd6986f6ec8f&pf_rd_r=NK3QTBYVED3VWK53GP53&pd_rd_wg=SWg1j&pd_rd_r=91effca1-6985-472a-9ac0-93ee557014a4&ref_=pd_hp_d_btf_crs_zg_bs_16209062011&th=1"

# Headers para simular uma requisição de navegador mais completa.
# Se o bloqueio persistir, você pode tentar encontrar o User-Agent do SEU navegador.
HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
            })

def get_product_page(url):
    """
    Faz uma requisição HTTP GET para a URL do produto com headers de navegador
    e retorna o conteúdo HTML.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None

def extract_product_info(html_content):
    """
    Extrai o nome e o preço do produto do conteúdo HTML usando BeautifulSoup.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    nome_produto = "Nome não encontrado"
    preco = None

    # --- Extrair o Título do Produto ---
    # IDs comuns para título na Amazon: "productTitle"
    titulo_element = soup.find(id="productTitle")
    if titulo_element:
        nome_produto = titulo_element.get_text(strip=True)
    else:
        print("Aviso: Elemento do título (ID 'productTitle') não encontrado.")

    # --- Extrair o Preço do Produto ---
    # IDs/Classes comuns para preço na Amazon:
    # "priceblock_ourprice", "priceblock_dealprice" (IDs)
    # "a-price-whole", "a-price-fraction" (Classes para partes do preço)

    # Tentativa 1: Encontrar um elemento com preço completo (pode ser um ID)
    # Ex: preco_element = soup.find(id="priceblock_ourprice")
    # Ex: preco_element = soup.find(id="priceblock_dealprice")
    
    # Tentativa 2: Encontrar o span que contém a parte inteira do preço (muito comum)
    preco_inteiro_element = soup.find(class_="a-price-whole")
    preco_fracao_element = soup.find(class_="a-price-fraction")

    if preco_inteiro_element and preco_fracao_element:
        # Se o preço for dividido em parte inteira e fração
        preco_str = preco_inteiro_element.get_text(strip=True) + preco_fracao_element.get_text(strip=True)
        # Os prints de DEBUG são úteis, mas você pode removê-los na versão final para um output mais limpo
        # print(f"DEBUG: Preço string bruto (inteiro + fracao): '{preco_str}'")
    elif soup.find(id="priceblock_ourprice"):
        preco_element = soup.find(id="priceblock_ourprice")
        preco_str = preco_element.get_text(strip=True)
        # print(f"DEBUG: Preço string bruto (ID priceblock_ourprice): '{preco_str}'")
    elif soup.find(id="priceblock_dealprice"):
        preco_element = soup.find(id="priceblock_dealprice")
        preco_str = preco_element.get_text(strip=True)
        # print(f"DEBUG: Preço string bruto (ID priceblock_dealprice): '{preco_str}'")
    else:
        preco_str = None
        print("Aviso: Elemento de preço não encontrado com os seletores comuns. Verifique o HTML da página.")

    if preco_str:
        # Limpa e converte a string do preço para float
        # Remove R$, espaços, pontos de milhar, e substitui vírgula decimal por ponto
        preco_str = preco_str.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
        # print(f"DEBUG: Preço string limpo: '{preco_str}'")
        try:
            preco = float(preco_str)
        except ValueError:
            print(f"Erro: Não foi possível converter o preço '{preco_str}' para número.")
            preco = None

    return nome_produto, preco

# --- Função para Salvar os Dados no CSV ---
def save_to_csv(data, filename='historico_precos.csv'):
    """
    Salva os dados (data, nome_produto, preco) em um arquivo CSV.
    Cria o arquivo com cabeçalho se ele não existir.
    """
    # Verifica se o arquivo já existe para decidir se adiciona o cabeçalho
    file_exists = False
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            file_exists = True
            # Verifica se o arquivo está vazio, mesmo que exista
            if not f.read(1): # Tenta ler um caractere. Se não ler, está vazio.
                file_exists = False
    except FileNotFoundError:
        pass # O arquivo não existe, então file_exists continua False

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Data/Hora', 'Nome do Produto', 'Preco']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists: # Adiciona o cabeçalho apenas se o arquivo não existia ou estava vazio
            writer.writeheader()

        writer.writerow(data)
    print(f"Dados salvos em '{filename}' com sucesso.")

# --- Execução Principal ---
if __name__ == "__main__":
    print("Iniciando Monitor de Preços...")
    html_content = get_product_page(URL_PRODUTO)

    if html_content:
        print("Conteúdo HTML da página obtido com sucesso.")
        # print(html_content[:1000]) # Descomente para ver o HTML bruto (apenas os primeiros 1000 chars)

        nome, preco = extract_product_info(html_content)

        if nome and preco is not None:
            print(f"\n--- Informações do Produto ---")
            print(f"Nome: {nome}")
            print(f"Preço: R$ {preco:.2f}")
            print("------------------------------")

            # --- Coletar data/hora e salvar no CSV ---
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Formata a data e hora
            
            data_to_save = {
                'Data/Hora': current_time,
                'Nome do Produto': nome,
                'Preco': f"{preco:.2f}" # Salva o preço como string formatada no CSV
            }
            save_to_csv(data_to_save)

        else:
            print("\nNão foi possível extrair todas as informações do produto.")
    else:
        print("\nNão foi possível obter o conteúdo da página para extração.")

    print("Monitor de Preços Finalizado por enquanto.")

    # --- NOVO CÓDIGO ABAIXO: Função principal para agendamento e loop ---

def check_price():
    """
    Função que encapsula toda a lógica de verificar e salvar o preço.
    Será agendada para rodar repetidamente.
    """
    print(f"\n--- Verificando preço em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    html_content = get_product_page(URL_PRODUTO)

    if html_content:
        nome, preco = extract_product_info(html_content)

        if nome and preco is not None:
            print(f"Produto: {nome}")
            print(f"Preço Atual: R$ {preco:.2f}")

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_to_save = {
                'Data/Hora': current_time,
                'Nome do Produto': nome,
                'Preco': f"{preco:.2f}"
            }
            save_to_csv(data_to_save)
        else:
            print("Não foi possível extrair todas as informações do produto nesta rodada.")
    else:
        print("Não foi possível obter o conteúdo da página nesta rodada.")
    print("------------------------------------------------------------------")

# --- Execução Principal (Modificada para agendamento) ---
if __name__ == "__main__":
    print("Iniciando Monitor de Preços (agendado)...")

    # Executa a função imediatamente ao iniciar
    check_price() 

    # Agende a tarefa para rodar a cada 5 minutos (para teste)
    # Você pode mudar para .every().hour, .every().day.at("HH:MM"), etc.
    schedule.every(1).minutes.do(check_price) 
    # Para testar mais rápido, pode usar .every(10).seconds.do(check_price)

    while True:
        schedule.run_pending() # Executa quaisquer tarefas agendadas que estejam prontas
        time.sleep(1) # Pausa por 1 segundo para não consumir CPU desnecessariamente