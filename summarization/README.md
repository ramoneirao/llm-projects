# 📄 Website Summarizer

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

O **Website Summarizer** é uma ferramenta de automação construída em Python que extrai o conteúdo de páginas web, processa informações relevantes (ignorando menus de navegação, scripts e estilos) e utiliza grandes modelos de linguagem (LLMs) para gerar um resumo conciso do site. O resultado final é exportado e salvo automaticamente em formato PDF.

Este repositório faz parte dos estudos contínuos de LLMs e oferece suporte a dois provedores de inferência:
1. **OpenRouter (Nuvem)** - Acesso a modelos externos robustos, como `nvidia/nemotron-3-super-120b-a12b`.
2. **Ollama (Local)** - Inferência offline focada em privacidade com modelos como `phi3`.

---

## Funcionalidades Principais

- 🌐 **Web Scraping Inteligente**: Utiliza `BeautifulSoup` para higienizar e extrair apenas o texto principal de uma URL, descartando elementos inúteis ao modelo (tags `<script>`, `<style>`, inputs, etc.).
- **Integração Flexível de LLMs**: Compatibilidade total com a API da OpenAI para conectar-se facilmente ao OpenRouter ou a uma instância local do Ollama.
- **Resumos em Markdown**: Instruções avançadas via *System Prompt* direcionam a geração de resumos limpos e diretos, focados em capturar a essência da página ou suas principais notícias.
- **Geração Automática de PDF**: Converte silenciosamente os resumos gerados em Markdown para documentos PDF legíveis e os salva em uma pasta dedicada (`/summaries`).
- **URL Default Inteligente**: Se nenhuma URL for fornecida pelo usuário, a ferramenta tem um *fallback* configurável e automático.

---

## Arquitetura do Projeto

O módulo é composto pelos seguintes scripts principais:

- `summarizer.py`: O script principal focado em execução via nuvem usando a API do **OpenRouter**. Ele gerencia as chaves de API via variáveis de ambiente (`.env`) e permite que diferentes modelos da plataforma sejam utilizados com facilidade.
- `summarizerLocal.py`: Uma versão totalmente offline do script, configurada para se comunicar com o **Ollama** rodando localmente (porta `11434`), sem custos de API e com inferência executada diretamente na sua máquina.

---

## Pré-requisitos

Antes de iniciar, certifique-se de que sua máquina atende aos requisitos abaixo:

- **Python 3.8+** instalado.
- Gerenciador de dependências e ambientes virtuais (recomendado o uso do [uv](https://github.com/astral-sh/uv) para sincronização de dependências).
- **(Opcional)** [Ollama](https://ollama.com/) instalado em sua máquina e com serviço ativo para executar o `summarizerLocal.py`. Modelo recomendado e configurado por padrão: `phi3`.

---

## Instalação

1. Clone o repositório principal:
```bash
git clone https://github.com/ramoneirao/LLM-studies.git
cd LLM-studies/summarization
```

2. Sincronize/instale as dependências do projeto (exemplo usando `uv`):
```bash
uv sync
```
*(As dependências requeridas incluem `requests`, `beautifulsoup4`, `openai`, `markdown-pdf` e `python-dotenv`).*

---

## Configuração

### Para uso com o OpenRouter (`summarizer.py`):
O script baseado no OpenRouter requer uma chave de API para funcionar.
Crie um arquivo `.env` na raiz da pasta `summarization` ou exporte a variável de ambiente:

```env
OPENROUTER_API_KEY="sk-or-v1-sua-chave-aqui..."
```

*(Se o arquivo `.env` não for encontrado, o script solicitará a chave interativamente pelo terminal.)*

### Para uso com o Ollama (`summarizerLocal.py`):
Nenhuma chave de API é necessária. Apenas certifique-se de que o daemon do Ollama está rodando localmente e que você fez o *pull* do modelo:
```bash
ollama serve
ollama pull phi3
```

---

## Como Usar

Para executar qualquer um dos scripts, ative seu ambiente virtual e use os seguintes comandos.

### Usando o OpenRouter (Nuvem)
```bash
python summarizer.py
```

### Usando o Ollama (Local)
```bash
python summarizerLocal.py
```

Ao rodar, o sistema exibirá o seguinte prompt interativo:
```text
=== WEBSITE SUMMARIZER ===
Enter the URL of the website you want to summarize (press Enter for default):
```

Cole a URL desejada ou pressione `Enter` para rodar uma análise de demonstração com um link padrão pré-configurado. O script fará o *fetching*, chamará o LLM e, ao final, avisará que o PDF foi salvo:

```text
Fetching content from https://example.com...
Generating summary with OpenRouter (nvidia/nemotron-3-super-120b-a12b:free)...
Saving the summary to .../summaries/example.com.pdf...
Summary completed successfully!
```

**Onde encontro meus PDFs?**
Todos os resumos convertidos serão salvos automaticamente em um diretório chamado `summaries/` dentro da pasta onde o script é executado.

---

## Contribuindo

Contribuições são super bem-vindas! Caso queira melhorar a extração de páginas ( lidando melhor com sites protegidos ), otimizar os prompts ou adicionar suporte a novos serviços, sinta-se à vontade para abrir uma issue ou enviar um *Pull Request*.

## Licença

Este projeto focado em estudos faz parte de uma iniciativa educacional. Sinta-se livre para usá-lo, modificá-lo e estudá-lo conforme achar necessário.
