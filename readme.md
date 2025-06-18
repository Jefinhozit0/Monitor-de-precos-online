# 📈 Monitor de Preços de Produtos Online

Um script robusto em Python para monitorar o preço de múltiplos produtos em sites de e-commerce (focado na Amazon Brasil), registrar seu histórico, enviar notificações por e-mail sobre quedas de preço e gerar visualizações gráficas do histórico.

---

## Funcionalidades ✨

Este monitor de preços oferece as seguintes funcionalidades avançadas:

* **Coleta Automatizada de Dados**: Acessa páginas de produtos em e-commerces (Amazon Brasil) utilizando requisições HTTP configuradas para simular um navegador real.
* **Web Scraping Inteligente**: Extrai dinamicamente o nome e o preço dos produtos do código HTML das páginas web.
* **Monitoramento de Múltiplos Produtos**: Permite configurar e rastrear o preço de uma lista de produtos diferentes simultaneamente.
* **Persistência de Dados**: Salva o histórico de preços de todos os produtos (Data/Hora, Nome do Produto, Preço, URL) em um arquivo CSV (`historico_precos.csv`), possibilitando o rastreamento das variações ao longo do tempo.
* **Agendamento Automático**: O script pode ser configurado para rodar em intervalos regulares (minutos, horas, dias), verificando e registrando os preços sem intervenção manual.
* **Notificações por E-mail**: Envia alertas personalizados por e-mail (com formatação HTML rica) para múltiplos destinatários sempre que uma queda de preço for detectada para qualquer um dos produtos monitorados.
* **Visualização Gráfica do Histórico**: Gera automaticamente um gráfico de linha (`historico_precos_grafico.png`) mostrando a evolução dos preços de todos os produtos ao longo do tempo.
* **Tratamento de Erros**: Inclui tratamento para falhas comuns, como problemas de acesso à página (403 Forbidden, 404 Not Found), erros na extração de dados e falhas no envio de e-mail.

---

## Tecnologias Utilizadas 🛠️

* **Python 3**: Linguagem de programação principal.
* **`requests`**: Biblioteca para fazer requisições HTTP e interagir com sites.
* **`BeautifulSoup4`**: Biblioteca para parsing de HTML e extração de dados (web scraping).
* **`pandas`**: Poderosa biblioteca para manipulação e análise de dados (leitura de CSV, filtragem, etc.).
* **`matplotlib`**: Biblioteca para criação de gráficos estáticos e interativos em Python.
* **`schedule`**: Biblioteca para agendar a execução de tarefas Python em intervalos definidos.
* **`smtplib`**: Módulo padrão do Python para enviar e-mails usando o protocolo SMTP.
* **`email.mime.text`**: Módulo padrão do Python para criar mensagens de e-mail formatadas (incluindo HTML).
* **`csv`**: Módulo padrão do Python para trabalhar com arquivos CSV.
* **`datetime`**: Módulo padrão do Python para lidar com datas e horas.

---

## Como Configurar e Rodar 🚀

### Pré-requisitos

Certifique-se de ter o [Python 3](https://www.python.org/downloads/) instalado em seu sistema. É **altamente recomendável** utilizar um ambiente virtual para isolar as dependências do projeto.

### Instalação

1.  **Clone o repositório** para o seu computador:
    ```bash
    git clone [https://github.com/Jefinhozit0/Monitor-de-pre-os-online.git](https://github.com/Jefinhozit0/Monitor-de-pre-os-online.git)
    cd Monitor-de-pre-os-online
    ```

2.  **Crie e ative um ambiente virtual**:
    ```bash
    python -m venv .venv
    # No Windows (PowerShell):
    .\.venv\Scripts\Activate.ps1
    # No Linux/macOS:
    source ./.venv/bin/activate
    ```

3.  **Instale as dependências** do projeto:
    ```bash
    pip install requests beautifulsoup4 pandas matplotlib schedule
    ```

### Configuração do Projeto

1.  **Abra o arquivo `monitor_preco.py`** em seu editor de texto.

2.  **Configure os Produtos para Monitorar**:
    * Localize a lista `PRODUTOS_PARA_MONITORAR` no início do script.
    * Preencha esta lista com dicionários, cada um contendo o `"nome"` (para sua referência) e a `"url"` do produto na Amazon Brasil que você deseja monitorar. Use URLs simplificadas (sem parâmetros de rastreamento longos) para maior robustez.
        ```python
        PRODUTOS_PARA_MONITORAR = [
            {"nome": "Echo Dot 5a Geração (Preta)", "url": "[https://www.amazon.com.br/Echo-Dot-5%C2%AA-gera%C3%A7%C3%A3o-Cor-Preta/dp/B09B8VGCR8/](https://www.amazon.com.br/Echo-Dot-5%C2%AA-gera%C3%A7%C3%A3o-Cor-Preta/dp/B09B8VGCR8/)"},
            {"nome": "Jogo The Last Of Us II", "url": "[https://www.amazon.com.br/Last-Us-Part-Remastered-PlayStation/dp/B0CP689L59/](https://www.amazon.com.br/Last-Us-Part-Remastered-PlayStation/dp/B0CP689L59/)"},
            # Adicione mais produtos conforme necessário
        ]
        ```
    * **Ajuste os seletores de HTML (opcional)**: O script usa seletores comuns da Amazon (IDs como `productTitle`, `priceblock_ourprice`, classes como `a-price-whole`). Se para algum produto o script não conseguir extrair o nome ou o preço, você precisará **inspecionar a página do produto no navegador** (clique direito -> "Inspecionar") para encontrar os seletores HTML exatos e ajustar a função `extract_product_info` de acordo.

3.  **Configure as Notificações por E-mail**:
    * Localize as variáveis `SENDER_EMAIL`, `SENDER_PASSWORD` e `RECEIVER_EMAILS`.
    * `SENDER_EMAIL`: Seu endereço de e-mail (ex: `seu_email@gmail.com`).
    * `SENDER_PASSWORD`: **IMPORTANTE:** Se estiver usando Gmail (ou outros provedores com verificação em duas etapas), você precisará gerar uma **senha de aplicativo (App Password)** nas configurações de segurança da sua conta Google e usar essa senha de 16 caracteres aqui. **Não utilize sua senha principal.**
    * `RECEIVER_EMAILS`: Uma **lista** de endereços de e-mail para onde as notificações serão enviadas (ex: `["seu_email@gmail.com", "amigo@example.com"]`).

### Como Rodar

Com o ambiente virtual ativado e todas as dependências instaladas:

```bash
python monitor_preco.py