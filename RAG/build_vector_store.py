import os
import glob
import tiktoken
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.manifold import TSNE
import plotly.graph_objects as go
from openai import OpenAI
from transformers import AutoTokenizer


# ----------------------------------------------------------------------------------------
#  CARREGANDO A CHAVE DE API DA OPENROUTER
# ----------------------------------------------------------------------------------------
load_dotenv(override=True)
api_key = os.getenv('OPENROUTER_API_KEY')

if not api_key:
    print("Nenhuma chave de API da OpenRouter foi encontrada - por favor verifique o seu arquivo .env!")
elif not api_key.startswith("sk-or-"):
    print("Uma chave de API foi encontrada, mas não começa com sk-or-; por favor, verifique se você está usando a chave correta da OpenRouter")
else:
    print("Chave de API da OpenRouter encontrada e parece boa até agora!")

openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)
MODEL = 'nvidia/nemotron-3-ultra-550b-a55b:free'
TOKENIZER_MODEL = 'nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16'
DB_NAME = 'RAG/vetor-knowledge-base'


# ----------------------------------------------------------------------------------------
# VERIFICAÇÃO DA BASE DE CONHECIMENTO
# ----------------------------------------------------------------------------------------
knowledge_base_path = "RAG/knowledge-base/**/*.md"
files = glob.glob(knowledge_base_path, recursive=True)
print(f"Encontrados {len(files)} arquivos de conhecimento na pasta 'knowledge-base'.")

entire_knowledge_base = ""

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        entire_knowledge_base += f.read()
        entire_knowledge_base += "\n\n"

print(f"Total de caracteres na base de conhecimento: {len(entire_knowledge_base):,}")


# ----------------------------------------------------------------------------------------
# CONTAGEM DE TOKENS
# ----------------------------------------------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
encoding = tokenizer.encode(entire_knowledge_base)
num_tokens = len(encoding)
print(f"Total de tokens na base de conhecimento: {num_tokens:,}")


# ----------------------------------------------------------------------------------------
# CARREGANDO A BASE DE CONHECIMENTO USANDO LANGCHAIN
# ----------------------------------------------------------------------------------------
arquivos = glob.glob("RAG/knowledge-base/*")
documentos = []

for arquivo in arquivos:
    tipo_doc = os.path.basename(arquivo)
    laoder = DirectoryLoader(arquivo, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    arquivos_carregados = laoder.load()
    for doc in arquivos_carregados:
        doc.metadata["tipo_doc"] = tipo_doc
        documentos.append(doc)

print(f"Total de documentos carregados: {len(documentos)}")
#print(documentos[1])

# ----------------------------------------------------------------------------------------
# DIVIDINDO OS DOCUMENTOS EM FRAGMENTOS
# ----------------------------------------------------------------------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = text_splitter.split_documents(documentos)
#print(f"Total de fragmentos criados: {len(chunks)}")
#print(f"Exemplo de fragmento:\n{chunks[0]}")


# ----------------------------------------------------------------------------------------
# CRIANDO EMBEDDINGS PARA CADA FRAGMENTO
# ----------------------------------------------------------------------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

if os.path.exists(DB_NAME):
    Chroma(persist_directory=DB_NAME, embedding_function=embeddings).delete_collection()

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB_NAME
)

print(f"Base de dados vetorial '{DB_NAME}' criada com {vector_store._collection.count()} vetores.")

# Verificando a quantidade de vetores e dimensões 
collection = vector_store._collection
count = collection.count()

sample_embedding = collection.get(limit=1, include=["embeddings"])["embeddings"][0]
dimensions = len(sample_embedding)
print(f"Há {count:,} vetores com {dimensions:,} dimensões na base de dados vetorial '{DB_NAME}'.")


# ----------------------------------------------------------------------------------------
# VISUALIZANDO OS EMBEDDINGS COM TSNE (2D)
# ----------------------------------------------------------------------------------------

resultado = collection.get(include=['embeddings', 'documents', 'metadatas'])

vetores = np.array(resultado['embeddings'])
documentos = resultado['documents']
metadatas = resultado['metadatas']

tipo_doc = [metadata['tipo_doc'] for metadata in metadatas]

cores = [['blue', 'green', 'red', 'orange'][
        ['products', 'employees', 'contracts', 'company'].index(t)
    ]for t in tipo_doc
]

# Reduzindo a dimensionalidade dos embeddings para 2D usando t-SNE

tsne = TSNE(
    n_components=2,
    random_state=42
)

reduced_vectors = tsne.fit_transform(vetores)

# Criando gráfico 2D
fig = go.Figure(
    data=[
        go.Scatter(
            x=reduced_vectors[:, 0],
            y=reduced_vectors[:, 1],
            mode='markers',
            marker=dict(
                size=5,
                color=cores,
                opacity=0.8),
            text=[
                f"Type: {t}<br>Text: {d[:100]}..."
                for t, d in zip(tipo_doc, documentos)],
            hoverinfo='text')
    ]
)

fig.update_layout(
    title='Visualização dos Embeddings com t-SNE',
    xaxis_title='x',
    yaxis_title='y',
    width=800,
    height=600,
    margin=dict(r=20, b=10, l=10, t=40)
)

# fig.show()


# ----------------------------------------------------------------------------------------
# VISUALIZANDO OS EMBEDDINGS EM 3D COM t-SNE
# ----------------------------------------------------------------------------------------

tsne = TSNE(n_components=3, random_state=42)

reduced_vectors = tsne.fit_transform(vetores)

# Criando gráfico 3D
fig = go.Figure(
    data=[
        go.Scatter3d(
            x=reduced_vectors[:, 0],
            y=reduced_vectors[:, 1],
            z=reduced_vectors[:, 2],
            mode='markers',
            marker=dict(
                size=5,
                color=cores,
                opacity=0.8),
            text=[
                f"Tipo: {t}<br>Texto: {d[:100]}..."
                for t, d in zip(tipo_doc, documentos)],
            hoverinfo='text')
    ]
)

fig.update_layout(
    title='Visualização 3D dos Embeddings com t-SNE',
    scene=dict(
        xaxis_title='x',
        yaxis_title='y',
        zaxis_title='z'),
    width=900,
    height=700,
    margin=dict(r=10, b=10, l=10, t=40)
)

fig.show()