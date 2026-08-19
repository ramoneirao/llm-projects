import os
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings

# ----------------------------------------------------------------------------------------
# CARREGANDO VARIÁVEIS DE AMBIENTE E CONFIGURAÇÕES
# ----------------------------------------------------------------------------------------
load_dotenv(override=True)

api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    raise ValueError("Nenhuma chave de API da OpenRouter foi encontrada. Verifique o seu arquivo .env.")

# Variáveis extraídas do build_vector_store.py para manter a compatibilidade
MODEL = 'nvidia/nemotron-3-ultra-550b-a55b:free'
DB_NAME = 'RAG/vetor-knowledge-base'

# ----------------------------------------------------------------------------------------
# CONEXÃO COM O BANCO DE DADOS VETORIAL (CHROMA)
# ----------------------------------------------------------------------------------------
# Utilizando o mesmo modelo de embeddings usado na criação do banco
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Conectando ao ChromaDB existente criado pelo build_vector_store.py
vectorstore = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)

# ----------------------------------------------------------------------------------------
# CONFIGURAÇÃO DO RETRIEVER E DO LLM
# ----------------------------------------------------------------------------------------
retriever = vectorstore.as_retriever()

# Configurando o ChatOpenAI para usar a base_url da OpenRouter e a chave correta
llm = ChatOpenAI(
    model_name=MODEL,
    temperature=0, # Respostas mais consistentes e baseadas nos fatos
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1"
)

# ----------------------------------------------------------------------------------------
# LÓGICA DE GERAÇÃO AUMENTADA POR RECUPERAÇÃO (RAG)
# ----------------------------------------------------------------------------------------
SYSTEM_PROMPT_TEMPLATE = """
Você é um assistente prestativo e experiente que representa a empresa InsureLLM.
Você está conversando com um usuário sobre a InsureLLM.
Responda às perguntas do usuário SEMPRE em Português (PT-BR).
Se for relevante, use o contexto fornecido abaixo para responder à pergunta.
Se você não souber a resposta baseada no contexto, diga que não sabe.

Contexto:
{context}
"""

def answer_question(question: str, history):
    # 1. Recupera os documentos relevantes do banco de dados vetorial
    docs = retriever.invoke(question)
    
    # 2. Formata o contexto unindo os conteúdos recuperados
    context = "\n\n".join(doc.page_content for doc in docs)
    
    # 3. Formata o prompt do sistema com o contexto
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)
    
    # 4. Envia o prompt de sistema e a pergunta do usuário para o LLM
    response = llm.invoke([
        SystemMessage(content=system_prompt), 
        HumanMessage(content=question)
    ])
    
    return response.content

# ----------------------------------------------------------------------------------------
# INTERFACE GRÁFICA (GRADIO)
# ----------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("Iniciando interface do Chatbot RAG...")
    app = gr.ChatInterface(
        fn=answer_question,
        title="Assistente Especialista - InsureLLM",
        description="Faça perguntas sobre os documentos indexados na sua base de conhecimento."
    )
    app.launch()