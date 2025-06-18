# 📈 Monitor de Preços de Produtos Online

Um script em Python para monitorar o preço de um produto específico em um site de e-commerce (atualmente Amazon Brasil), registrar seu histórico de preços em um arquivo CSV e exibir as informações mais recentes.

---

## Funcionalidades ✨

* **Coleta de Dados**: Acessa a página de um produto usando requisições HTTP.
* **Web Scraping**: Extrai o nome e o preço do produto diretamente do HTML da página.
* **Persistência de Dados**: Salva o histórico de preços (data/hora, nome do produto, preço) em um arquivo CSV, permitindo rastrear as variações ao longo do tempo.
* **Tratamento de Erros**: Inclui tratamento para falhas na requisição HTTP e na extração/conversão do preço.

---

## Tecnologias Utilizadas 🛠️

* **Python 3**: Linguagem de programação principal.
* **`requests`**: Biblioteca para fazer requisições HTTP.
* **`BeautifulSoup4`**: Biblioteca para parsing de HTML e extração de dados (web scraping).
* **`csv`**: Módulo padrão do Python para trabalhar com arquivos CSV.
* **`datetime`**: Módulo padrão do Python para lidar com datas e horas.

---

## Como Configurar e Rodar 🚀

### Pré-requisitos

Certifique-se de ter o [Python 3](https://www.python.org/downloads/) instalado em seu sistema. É altamente recomendável usar um ambiente virtual para gerenciar as dependências.

### Instalação

1.  **Clone o repositório** (ou baixe o arquivo `monitor_preco.py`):
    ```bash
    git clone [https://github.com/Jefinhozit0/Monitor-de-pre-os-online.git]
    cd SEU_REPOSITORIO
    ```


2.  **Crie e ative um ambiente virtual** (recomendado):
    ```bash
    python -m venv .venv
    # No Windows (PowerShell):
    .\.venv\Scripts\Activate.ps1
    # No Linux/macOS:
    source ./.venv/bin/activate
    ```

3.  **Instale as dependências** do projeto:
    ```bash
    pip install requests beautifulsoup4
    ```

### Configuração do Produto

1.  **Abra o arquivo `monitor_preco.py`** em seu editor de texto.
2.  **Altere a variável `URL_PRODUTO`** (linha 7) para a URL do produto que você deseja monitorar na Amazon Brasil.
    * Exemplo: `URL_PRODUTO = "https://www.amazon.com.br/Echo-Dot-5%C2%AA-gera%C3%A7%C3%A3o-Cor-Preta/dp/B09B8VGCR8/"`
3.  **Ajuste os seletores de HTML (opcional)**: O script tenta encontrar o nome (`id="productTitle"`) e o preço (`class="a-price-whole"`, `id="priceblock_ourprice"`, etc.) usando IDs e classes comuns da Amazon. Se o script não conseguir encontrar o preço ou o nome, você precisará **inspecionar a página do produto no navegador** (clique direito -> "Inspecionar") para encontrar os seletores HTML exatos e ajustar a função `extract_product_info`.

### Como Rodar

Com o ambiente virtual ativo e as dependências instaladas:

```bash
python monitor_preco.py