import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
import schedule
import smtplib # Módulo para enviar emails
from email.mime.text import MIMEText # Para criar o corpo do email
import pandas as pd # Importe pandas
import matplotlib.pyplot as plt # Importe matplotlib para gráficos

# --- Configurações Iniciais ---
# !!! IMPORTANTE: PREENCHA ESTA LISTA COM AS SUAS URLs DE PRODUTOS DA AMAZON !!!
PRODUTOS_PARA_MONITORAR = [
    {
        "nome": "Echo Dot 5a Geração (Preta)",
        "url": "https://www.amazon.com.br/Echo-Dot-5%C2%AA-gera%C3%A7%C3%A3o-Cor-Preta/dp/B09B8VGCR8/"
    },
    {
        "nome": "Jogo The Last Of Us II",
        # URL simplificada é mais robusta para scraping:
        "url": "https://www.amazon.com.br/Last-Us-Part-Remastered-PlayStation/dp/B0CP689L59/" 
    },
    # Adicione mais produtos aqui, se desejar
    # {
    #     "nome": "Nome do Terceiro Produto",
    #     "url": "https://www.amazon.com.br/url/do/terceiro/produto/"
    # },
]

# Headers para simular uma requisição de navegador mais completa.
HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
            })

# --- Configurações de E-mail ---
# !!! PREENCHA COM SEUS DADOS DE EMAIL E SENHA DE APLICATIVO !!!
SENDER_EMAIL = "jefinhozit00@gmail.com"
SENDER_PASSWORD = "poyh omvz pmnv qrgn" # Sua senha de aplicativo do Gmail (NÃO a sua senha normal!)
# Lista de endereços de e-mail para múltiplos destinatários
RECEIVER_EMAILS = ["jefinhozit00@gmail.com", "enricolimafreitas@gmail.com", "arthurapanizza@gmail.com","miguelpauloalvesdias@gmail.com"] 
# Certifique-se de que os emails são válidos!

# --- Variável para armazenar o último preço conhecido (agora um dicionário por URL) ---
last_known_prices = {}

# --- Funções de Scraping e Salvamento ---
def get_product_page(url):
    """
    Faz uma requisição HTTP GET para a URL do produto com headers de navegador
    e retorna o conteúdo HTML.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
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
    Salva os dados (data, nome_produto, preco, URL) em um arquivo CSV.
    Cria o arquivo com cabeçalho se ele não existir.
    """
    file_exists = False
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            file_exists = True
            if not f.read(1): # Verifica se o arquivo está vazio
                file_exists = False
    except FileNotFoundError:
        pass # O arquivo não existe, então file_exists continua False

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Data/Hora', 'Nome do Produto', 'Preco', 'URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)
    print(f"Dados salvos em '{filename}' com sucesso.")

# --- Função para Enviar Notificação por E-mail (HTML) ---
def send_email_notification(subject, body):
    """
    Envia uma notificação por e-mail usando as credenciais configuradas.
    """
    try:
        msg = MIMEText(body, 'html', 'utf-8') 
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECEIVER_EMAILS) # Usa a lista de e-mails para o cabeçalho 'To'

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Notificação por e-mail enviada para {', '.join(RECEIVER_EMAILS)}!") 
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        # Mensagem de erro atualizada para usar a lista de destinatários
        print(f"Verifique suas credenciais (SENDER_EMAIL, SENDER_PASSWORD) e as permissões de segurança da conta (senha de aplicativo para Gmail). Destinatários: {', '.join(RECEIVER_EMAILS)}")


# --- Função para Plotar Histórico de Preços (Gráficos) ---
def plot_price_history(filename='historico_precos.csv', plot_filename='historico_precos_grafico.png'):
    """
    Lê o histórico de preços do CSV e gera um gráfico de linha para cada produto.
    """
    try:
        df = pd.read_csv(filename)

        # Converte as colunas para os tipos corretos
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])
        df['Preco'] = pd.to_numeric(df['Preco'])

        plt.figure(figsize=(12, 7)) # Define o tamanho da figura do gráfico

        # Plota uma linha para cada produto único
        for url in df['URL'].unique():
            df_produto = df[df['URL'] == url]
            nome_produto = df_produto['Nome do Produto'].iloc[0] # Pega o nome do produto
            plt.plot(df_produto['Data/Hora'], df_produto['Preco'], label=nome_produto, marker='o')

        plt.title('Histórico de Preços dos Produtos Monitorados', fontsize=16)
        plt.xlabel('Data e Hora', fontsize=12)
        plt.ylabel('Preço (R$)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7) # Adiciona um grid ao gráfico
        plt.legend(loc='best', fontsize=10) # Adiciona a legenda
        plt.xticks(rotation=45, ha='right') # Rotaciona os labels do eixo X para melhor visualização
        plt.tight_layout() # Ajusta o layout para evitar cortes
        
        plt.savefig(plot_filename) # Salva o gráfico como um arquivo de imagem
        plt.close() # Fecha a figura para liberar memória
        print(f"Gráfico do histórico de preços salvo como '{plot_filename}'")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{filename}' não foi encontrado para gerar o gráfico.")
    except pd.errors.EmptyDataError:
        print(f"Aviso: O arquivo '{filename}' está vazio. Não há dados para gerar o gráfico.")
    except Exception as e:
        print(f"Erro ao gerar o gráfico: {e}")


# --- Função principal para agendamento e loop ---
def check_all_products():
    """
    Função que itera sobre todos os produtos na lista PRODUTOS_PARA_MONITORAR
    e verifica seus preços, salvando, notificando por e-mail se houver queda,
    e gerando o gráfico de histórico.
    """
    global last_known_prices

    print(f"\n--- Iniciando verificação de MÚLTIPLOS produtos em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    for produto_info in PRODUTOS_PARA_MONITORAR:
        nome_curto_produto = produto_info["nome"]
        url_produto = produto_info["url"]
        
        print(f"\nVerificando: {nome_curto_produto} ({url_produto})")
        
        html_content = get_product_page(url_produto)

        if html_content:
            nome_extraido, preco = extract_product_info(html_content)
            nome_final = nome_extraido if nome_extraido != "Nome não encontrado" else nome_curto_produto

            if nome_final and preco is not None:
                print(f"  Produto: {nome_final}")
                print(f"  Preço Atual: R$ {preco:.2f}")

                # Lógica de Notificação de Queda de Preço
                if url_produto in last_known_prices and last_known_prices[url_produto] is not None:
                    if preco < last_known_prices[url_produto]:
                        preco_anterior = last_known_prices[url_produto]
                        queda_absoluta = preco_anterior - preco
                        queda_percentual = (queda_absoluta / preco_anterior) * 100 if preco_anterior > 0 else 0

                        subject = f"🚨 Queda de Preço: {nome_final} por R$ {preco:.2f}!"
                        
                        # CORPO DO E-MAIL CUSTOMIZADO (HTML)
                        body = f"""
                        <html>
                        <head></head>
                        <body>
                            <p>Olá!</p>
                            <p>Identificamos uma <strong>queda no preço</strong> do produto que você está monitorando:</p>
                            <ul>
                                <li>🛒 <strong>Produto:</strong> {nome_final}</li>
                                <li>📉 <strong>Preço Anterior:</strong> R$ {preco_anterior:.2f}</li>
                                <li>💲 <strong>Preço Atual:</strong> <strong style="color: green; font-size: 1.2em;">R$ {preco:.2f}</strong></li>
                                <li>⬇️ <strong>Queda:</strong> R$ {queda_absoluta:.2f} ({queda_percentual:.2f}%)</li>
                            </ul>
                            <p>Aproveite a oferta!</p>
                            <p>🔗 <a href="{url_produto}">Clique aqui para ver o produto na Amazon</a></p>
                            <p>Atenciosamente,<br>Seu Monitor de Preços Python</p>
                        </body>
                        </html>
                        """
                        
                        send_email_notification(subject, body) # Chama a função de e-mail
                    elif preco > last_known_prices[url_produto]:
                        print(f"  Preço de '{nome_final}' aumentou para R$ {preco:.2f}.")
                    else:
                        print(f"  Preço de '{nome_final}' permaneceu o mesmo (R$ {preco:.2f}).")
                else:
                    print(f"  Preço inicial para '{nome_final}' definido. Nenhuma comparação ainda.")

                last_known_prices[url_produto] = preco # Atualiza o último preço conhecido para esta URL

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data_to_save = {
                    'Data/Hora': current_time,
                    'Nome do Produto': nome_final,
                    'Preco': f"{preco:.2f}",
                    'URL': url_produto
                }
                save_to_csv(data_to_save)
            else:
                print(f"  Não foi possível extrair todas as informações para '{nome_curto_produto}' nesta rodada.")
        else:
            print(f"  Não foi possível obter o conteúdo da página para '{nome_curto_produto}' nesta rodada.")
        
        time.sleep(2) # Pausa por 2 segundos entre cada requisição para não sobrecarregar o site

    print("\n--- Verificação de múltiplos produtos CONCLUÍDA ---")
    plot_price_history() # <<<--- CHAMA A FUNÇÃO DE GERAR O GRÁFICO AQUI!


# --- Execução Principal (Modificada para agendamento) ---
if __name__ == "__main__":
    print("Iniciando Monitor de Preços (agendado para múltiplos produtos com notificação por e-mail e gráfico)...")

    # Tenta carregar os últimos preços conhecidos do CSV ao iniciar.
    try:
        with open('historico_precos.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            if rows:
                # Carrega o último preço de cada URL única no histórico
                for row in rows:
                    last_known_prices[row['URL']] = float(row['Preco'].replace(',', '.'))
                print(f"Últimos preços conhecidos carregados do CSV para {len(last_known_prices)} produtos.")
    except FileNotFoundError:
        print("Arquivo de histórico não encontrado. Começando com preços iniciais para cada produto.")
    except Exception as e:
        print(f"Erro ao carregar últimos preços do CSV: {e}")

    # Executa a função imediatamente ao iniciar
    check_all_products() 

    # Agende a tarefa para rodar a cada 1 minuto (para teste)
    schedule.every(1).minutes.do(check_all_products) 
    # Para uso real, considere intervalos maiores: .every().hour, .every().day.at("HH:MM")

    while True:
        schedule.run_pending()
        time.sleep(1)