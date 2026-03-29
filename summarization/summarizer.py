import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from openai import OpenAI
from markdown_pdf import MarkdownPdf, Section

# Tenta carregar dotenv caso o pacote python-dotenv esteja instalado
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuração do OpenRouter
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    api_key = input("OPENROUTER_API_KEY não encontrada. Digite sua chave da OpenRouter: ").strip()
    if not api_key:
        print("Erro: A chave de API da OpenRouter é obrigatória.")
        exit(1)

openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "Nenhum título encontrado"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)


system_prompt = "You are an assistant that analyzes the content of a website \
and provides a short summary, ignoring text that might be related to navigation. \
Respond in markdown and in English."


def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}\n"
    user_prompt += "The contents of this website are as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt


def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]


def summarize(url, model="nvidia/nemotron-3-super-120b-a12b:free"):
    print(f"Fetching content from {url}...")
    website = Website(url)
    print(f"Generating summary with OpenRouter ({model})...")
    response = openai.chat.completions.create(
        model=model,
        messages=messages_for(website)
    )
    return response.choices[0].message.content


def save_as_pdf(markdown_text, url):
    # Diretório baseado no local do script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    summaries_dir = os.path.join(base_dir, "summaries")
    
    # Cria diretório de resumos se não existir
    os.makedirs(summaries_dir, exist_ok=True)
    
    # Extrai o domínio principal para dar nome ao arquivo
    domain = urlparse(url).netloc
    if not domain:
        domain = "site_summary"
        
    # Remove prefixo www. se houver para o nome do arquivo ficar mais limpo
    if domain.startswith("www."):
        domain = domain[4:]
    
    filepath = os.path.join(summaries_dir, f"{domain}.pdf")
    
    print(f"Saving the summary to {filepath}...")
    pdf = MarkdownPdf(toc_level=0)
    pdf.add_section(Section(markdown_text))
    pdf.save(filepath)
    print("Summary completed successfully!")


def main():
    print("=== WEBSITE SUMMARIZER (OpenRouter) ===")
    url = input("Enter the URL of the website you want to summarize (press Enter for default): ").strip()
    
    if not url:
        url = "https://ramoneirao.github.io/portfolio/"
        print(f"Using default URL: {url}")
        
    if not url.startswith("http"):
        url = "https://" + url
        
    try:
        # Você pode alterar o modelo aqui para qualquer um suportado pelo OpenRouter
        summary = summarize(url)
        save_as_pdf(summary, url)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
