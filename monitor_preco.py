import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
import schedule
import smtplib # Módulo para enviar emails
from email.mime.text import MIMEText # Para criar o corpo do email

# --- Configurações Iniciais ---
# !!! IMPORTANTE: SUBSTITUA ESTA URL PELA URL DO SEU PRODUTO REAL DA AMAZON !!!
URL_PRODUTO = "https://www.amazon.com.br/Echo-Dot-5%C2%AA-gera%C3%A7%C3%A3o-Cor-Preta/dp/B09B8VGCR8/?_encoding=UTF8&pd_rd_w=Uyk7p&content-id=amzn1.sym.8fbb3d34-c3f1-46af-9d99-fd6986f6ec8f&pf_rd_p=8fbb3d34-c3f1-46af-9d99-fd6986f6ec8f&pf_rd_r=NK3QTBYVED3VWK53GP53&pd_rd_wg=SWg1j&pd_rd_r=91effca1-6985-472a-9ac0-93ee557014a4&ref_=pd_hp_d_btf_crs_zg_bs_16209062011&th=1"

# Headers para simular uma requisição de navegador mais completa.
HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecomcure-Requests': '1',
            'Referer': 'https://www.google.com/'
            })

# --- Configurações de E-mail ---
# !!! PREENCHA COM SEUS DADOS DE EMAIL !!!
SENDER_EMAIL = "jefinhozit00@gmail.com"  # Seu email (o que vai enviar)
SENDER_PASSWORD = "poyh omvz pmnv qrgn"  # Sua senha de aplicativo do Gmail (NÃO a sua senha normal!)
RECEIVER_EMAIL = "jefinhozit00@gmail.com"  # Email para onde a notificação será enviada (pode ser o seu mesmo)

# --- Variável para armazenar o último preço conhecido (para notificar sobre quedas) ---
last_known_price = None

# ... (funções get_product_page, extract_product_info, save_to_csv permanecem as mesmas) ...

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

    titulo_element = soup.find(id="productTitle")
    if titulo_element:
        nome_produto = titulo_element.get_text(strip=True)
    else:
        print("Aviso: Elemento do título (ID 'productTitle') não encontrado.")

    preco_inteiro_element = soup.find(class_="a-price-whole")
    preco_fracao_element = soup.find(class_="a-price-fraction")

    if preco_inteiro_element and preco_fracao_element:
        preco_str = preco_inteiro_element.get_text(strip=True) + preco_fracao_element.get_text(strip=True)
    elif soup.find(id="priceblock_ourprice"):
        preco_element = soup.find(id="priceblock_ourprice")
        preco_str = preco_element.get_text(strip=True)
    elif soup.find(id="priceblock_dealprice"):
        preco_element = soup.find(id="priceblock_dealprice")
        preco_str = preco_element.get_text(strip=True)
    else:
        preco_str = None
        print("Aviso: Elemento de preço não encontrado com os seletores comuns. Verifique o HTML da página.")

    if preco_str:
        preco_str = preco_str.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
        try:
            preco = float(preco_str)
        except ValueError:
            print(f"Erro: Não foi possível converter o preço '{preco_str}' para número.")
            preco = None

    return nome_produto, preco


def save_to_csv(data, filename='historico_precos.csv'):
    """
    Salva os dados (data, nome_produto, preco) em um arquivo CSV.
    Cria o arquivo com cabeçalho se ele não existir.
    """
    file_exists = False
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            file_exists = True
            if not f.read(1):
                file_exists = False
    except FileNotFoundError:
        pass

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Data/Hora', 'Nome do Produto', 'Preco']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)
    print(f"Dados salvos em '{filename}' com sucesso.")


def send_email_notification(subject, body):
    """
    Envia uma notificação por e-mail.
    """
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        # Para Gmail, use smtp.gmail.com na porta 587 (TLS)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: # Usar SMTP_SSL para porta 465
            #server.starttls() # starttls é para porta 587
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Notificação por e-mail enviada para {RECEIVER_EMAIL}!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        print("Verifique suas credenciais, senha de aplicativo (para Gmail/Outlook) e permissões de segurança.")


def check_price():
    """
    Função que encapsula toda a lógica de verificar e salvar o preço,
    incluindo a lógica de notificação.
    """
    global last_known_price # Permite modificar a variável global

    print(f"\n--- Verificando preço em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    html_content = get_product_page(URL_PRODUTO)

    if html_content:
        nome, preco = extract_product_info(html_content)

        if nome and preco is not None:
            print(f"Produto: {nome}")
            print(f"Preço Atual: R$ {preco:.2f}")

            # Lógica de Notificação de Queda de Preço
            if last_known_price is not None: # Se já temos um preço anterior
                if preco < last_known_price:
                    subject = f"🚨 Queda de Preço: {nome} por R$ {preco:.2f}!"
                    body = (f"O preço de '{nome}' caiu!\n"
                            f"Preço anterior: R$ {last_known_price:.2f}\n"
                            f"Preço atual: R$ {preco:.2f}\n"
                            f"Link do produto: {URL_PRODUTO}")
                    send_email_notification(subject, body)
                elif preco > last_known_price:
                    print(f"Preço de '{nome}' aumentou para R$ {preco:.2f}.")
                else:
                    print(f"Preço de '{nome}' permaneceu o mesmo (R$ {preco:.2f}).")
            else:
                print("Preço inicial definido. Nenhuma comparação ainda.")

            last_known_price = preco # Atualiza o último preço conhecido

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

    # Tenta carregar o último preço conhecido do CSV ao iniciar para evitar notificações falsas.
    # Isso é um pouco mais avançado, mas evita que a primeira verificação dispare uma notificação
    # se o last_known_price fosse apenas None.
    try:
        with open('historico_precos.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            if rows:
                last_known_price = float(rows[-1]['Preco'].replace(',', '.')) # Pega o último preço salvo
                print(f"Último preço conhecido carregado do CSV: R$ {last_known_price:.2f}")
    except FileNotFoundError:
        print("Arquivo de histórico não encontrado. Começando com o preço inicial.")
    except Exception as e:
        print(f"Erro ao carregar último preço do CSV: {e}")

    # Executa a função imediatamente ao iniciar
    check_price() 

    # Agende a tarefa para rodar a cada 5 minutos (para teste)
    schedule.every(1).minutes.do(check_price) 
    # Para testar mais rápido, pode usar .every(10).seconds.do(check_price)

    while True:
        schedule.run_pending()
        time.sleep(1)