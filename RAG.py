# RAG COMPLETO PARA TREINOS - TODOS OS PASSOS DETALHADOS
# pip install langchain langchain-community langchain-ollama sentence-transformers faiss-cpu chromadb pypdf python-docx

import os
import glob
import json
from typing import List, Dict, Any
from datetime import datetime

# Importações LangChain
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

class RAGTreinosCompleto:
    def __init__(self, pasta_documentos: str = "documentos_treino", modelo_llm: str = "deepseek-r1:1.5b"):
        self.pasta_documentos = pasta_documentos
        self.modelo_llm = modelo_llm
        self.documentos_carregados = []
        self.chunks = []
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        self.vectorstore_tipo = "FAISS"  # ou "Chroma"
        
        print(f"🏋️ RAG Treinos inicializado")
        print(f"📁 Pasta documentos: {pasta_documentos}")
        print(f"🤖 Modelo LLM: {modelo_llm}")
    
    # PASSO 1: CARREGAR DOCUMENTOS
    def carregar_documentos(self) -> List[Document]:
        """Carrega documentos de diferentes formatos (.txt, .pdf, .docx, .md)"""
        print("\n📄 PASSO 1: CARREGAR DOCUMENTOS")
        print("-" * 50)
        
        if not os.path.exists(self.pasta_documentos):
            raise FileNotFoundError(f"Pasta '{self.pasta_documentos}' não encontrada!")
        
        documentos = []
        arquivos_processados = 0
        
        # Carregar arquivos .txt
        for arquivo in glob.glob(f"{self.pasta_documentos}/*.txt"):
            try:
                loader = TextLoader(arquivo, encoding='utf-8')
                docs = loader.load()
                documentos.extend(docs)
                arquivos_processados += 1
                print(f"✅ TXT: {os.path.basename(arquivo)} - {len(docs)} documentos")
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {e}")
        
        # Carregar arquivos .pdf
        for arquivo in glob.glob(f"{self.pasta_documentos}/*.pdf"):
            try:
                loader = PyPDFLoader(arquivo)
                docs = loader.load()
                documentos.extend(docs)
                arquivos_processados += 1
                print(f"✅ PDF: {os.path.basename(arquivo)} - {len(docs)} páginas")
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {e}")
        
        # Carregar arquivos .docx
        for arquivo in glob.glob(f"{self.pasta_documentos}/*.docx"):
            try:
                loader = Docx2txtLoader(arquivo)
                docs = loader.load()
                documentos.extend(docs)
                arquivos_processados += 1
                print(f"✅ DOCX: {os.path.basename(arquivo)} - {len(docs)} documentos")
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {e}")
        
        # Carregar arquivos .md
        for arquivo in glob.glob(f"{self.pasta_documentos}/*.md"):
            try:
                loader = TextLoader(arquivo, encoding='utf-8')
                docs = loader.load()
                documentos.extend(docs)
                arquivos_processados += 1
                print(f"✅ MD: {os.path.basename(arquivo)} - {len(docs)} documentos")
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {e}")
        
        self.documentos_carregados = documentos
        
        print(f"\n📊 RESUMO DO CARREGAMENTO:")
        print(f"   • Arquivos processados: {arquivos_processados}")
        print(f"   • Total de documentos: {len(documentos)}")
        
        # Estatísticas dos documentos
        total_chars = sum(len(doc.page_content) for doc in documentos)
        print(f"   • Total de caracteres: {total_chars:,}")
        print(f"   • Média de caracteres por documento: {total_chars // len(documentos) if documentos else 0:,}")
        
        return documentos
    
    # PASSO 2: DIVIDIR EM CHUNKS
    def dividir_textos_em_chunks(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        """Divide os textos em chunks menores para processamento"""
        print(f"\n✂️ PASSO 2: DIVIDIR TEXTOS EM CHUNKS")
        print("-" * 50)
        
        if not self.documentos_carregados:
            raise ValueError("Carregue os documentos primeiro!")
        
        # Configurar o text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        print(f"⚙️ Configurações do splitter:")
        print(f"   • Tamanho do chunk: {chunk_size}")
        print(f"   • Overlap: {chunk_overlap}")
        
        # Dividir documentos
        chunks = text_splitter.split_documents(self.documentos_carregados)
        self.chunks = chunks
        
        print(f"\n📊 RESULTADO DA DIVISÃO:")
        print(f"   • Chunks criados: {len(chunks)}")
        
        # Estatísticas dos chunks
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        print(f"   • Tamanho médio dos chunks: {sum(chunk_sizes) // len(chunk_sizes) if chunks else 0}")
        print(f"   • Menor chunk: {min(chunk_sizes) if chunks else 0}")
        print(f"   • Maior chunk: {max(chunk_sizes) if chunks else 0}")
        
        # Mostrar exemplo de chunk
        if chunks:
            print(f"\n📝 EXEMPLO DE CHUNK:")
            print(f"   Fonte: {chunks[0].metadata.get('source', 'N/A')}")
            print(f"   Tamanho: {len(chunks[0].page_content)} caracteres")
            print(f"   Prévia: {chunks[0].page_content[:200]}...")
        
        return chunks
    
    # PASSO 3: GERAR EMBEDDINGS
    def gerar_embeddings(self, modelo_embedding: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Configura o modelo de embeddings"""
        print(f"\n🧠 PASSO 3: GERAR EMBEDDINGS")
        print("-" * 50)
        
        print(f"⚙️ Configurando modelo de embeddings: {modelo_embedding}")
        
        # Opções de modelos
        modelos_disponiveis = {
            "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",  # Rápido, inglês
            "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # Multilíngue
            "portugues": "neuralmind/bert-base-portuguese-cased"  # Português específico
        }
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=modelo_embedding,
            model_kwargs={'device': 'cpu'},  # Use 'cuda' se tiver GPU
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print(f"✅ Modelo de embeddings configurado")
        print(f"   • Modelo: {modelo_embedding}")
        print(f"   • Dispositivo: CPU")
        
        # Testar embedding
        if self.chunks:
            print(f"\n🧪 TESTE DE EMBEDDING:")
            texto_teste = self.chunks[0].page_content[:100]
            embedding_teste = self.embeddings.embed_query(texto_teste)
            print(f"   • Texto teste: {texto_teste}")
            print(f"   • Dimensão do embedding: {len(embedding_teste)}")
            print(f"   • Primeiros 5 valores: {embedding_teste[:5]}")
    
    # PASSO 4: CRIAR VECTOR STORE
    def criar_vector_store(self, tipo: str = "FAISS", salvar: bool = True):
        """Cria o banco de vetores (FAISS ou Chroma)"""
        print(f"\n🗄️ PASSO 4: CRIAR VECTOR STORE ({tipo})")
        print("-" * 50)
        
        if not self.chunks:
            raise ValueError("Crie os chunks primeiro!")
        
        if not self.embeddings:
            raise ValueError("Configure os embeddings primeiro!")
        
        self.vectorstore_tipo = tipo
        
        print(f"⚙️ Criando {tipo} vector store...")
        print(f"   • Chunks para processar: {len(self.chunks)}")
        print(f"   • Gerando embeddings para todos os chunks...")
        
        if tipo == "FAISS":
            # Criar FAISS vectorstore
            self.vectorstore = FAISS.from_documents(
                documents=self.chunks,
                embedding=self.embeddings
            )
            
            if salvar:
                self.vectorstore.save_local("vectorstore_faiss")
                print(f"✅ FAISS vectorstore salvo em 'vectorstore_faiss'")
        
        elif tipo == "Chroma":
            # Criar Chroma vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=self.chunks,
                embedding=self.embeddings,
                persist_directory="vectorstore_chroma" if salvar else None
            )
            
            if salvar:
                self.vectorstore.persist()
                print(f"✅ Chroma vectorstore salvo em 'vectorstore_chroma'")
        
        else:
            raise ValueError("Tipo deve ser 'FAISS' ou 'Chroma'")
        
        print(f"\n📊 VECTOR STORE CRIADO:")
        print(f"   • Tipo: {tipo}")
        print(f"   • Documentos indexados: {len(self.chunks)}")
        
        # Testar busca
        print(f"\n🔍 TESTE DE BUSCA:")
        query_teste = "exercício para peito"
        docs_similares = self.vectorstore.similarity_search(query_teste, k=2)
        print(f"   • Query teste: '{query_teste}'")
        print(f"   • Documentos encontrados: {len(docs_similares)}")
        if docs_similares:
            print(f"   • Mais similar: {docs_similares[0].page_content[:100]}...")
    
    # PASSO 5: CONFIGURAR LANGCHAIN
    def configurar_langchain(self):
        """Configura o LLM e a cadeia de QA"""
        print(f"\n🔗 PASSO 5: CONFIGURAR LANGCHAIN")
        print("-" * 50)
        
        if not self.vectorstore:
            raise ValueError("Crie o vector store primeiro!")
        
        # Configurar LLM
        print(f"⚙️ Configurando LLM: {self.modelo_llm}")
        self.llm = OllamaLLM(
            model=self.modelo_llm,
            temperature=0.3,
            top_p=0.9
        )
        
        # Testar LLM
        print(f"🧪 Testando LLM...")
        try:
            resposta_teste = self.llm.invoke("Diga olá em uma palavra")
            print(f"   • Teste LLM: '{resposta_teste.strip()}'")
        except Exception as e:
            print(f"   ❌ Erro no teste LLM: {e}")
            print(f"   💡 Verifique se o Ollama está rodando: ollama run {self.modelo_llm}")
        
        # Configurar template de prompt
        template_prompt = """Você é um especialista em treinos e exercícios físicos. 
Use apenas as informações do contexto abaixo para responder à pergunta.
Se a informação não estiver no contexto, diga que não sabe.

Contexto: {context}

Pergunta: {question}

Resposta detalhada e útil:"""
        
        prompt = PromptTemplate(
            template=template_prompt,
            input_variables=["context", "question"]
        )
        
        # Configurar retriever
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}  # Retorna 4 documentos mais similares
        )
        
        # Criar cadeia de QA
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        print(f"✅ LangChain configurado:")
        print(f"   • LLM: {self.modelo_llm}")
        print(f"   • Retriever: {self.vectorstore_tipo}")
        print(f"   • Documentos por consulta: 4")
        print(f"   • Prompt personalizado: Sim")
    
    # PASSO 6: INTERFACE DE TERMINAL
    def interface_terminal(self):
        """Interface simples de terminal para chat"""
        print(f"\n💬 PASSO 6: INTERFACE DE TERMINAL")
        print("=" * 60)
        print(f"🏋️ SISTEMA RAG DE TREINOS ATIVO")
        print(f"🤖 Modelo: {self.modelo_llm}")
        print(f"🗄️ Vector Store: {self.vectorstore_tipo}")
        print(f"📄 Documentos: {len(self.chunks)} chunks")
        print("=" * 60)
        print("💡 Dicas:")
        print("   • Digite 'sair' para encerrar")
        print("   • Digite 'info' para ver estatísticas")
        print("   • Digite 'exemplo' para perguntas de exemplo")
        print("-" * 60)
        
        contador_perguntas = 0
        
        while True:
            pergunta = input(f"\n💪 Pergunta #{contador_perguntas + 1}: ").strip()
            
            if pergunta.lower() == 'sair':
                print("👋 Até logo!")
                break
            
            elif pergunta.lower() == 'info':
                self._mostrar_info()
                continue
            
            elif pergunta.lower() == 'exemplo':
                self._mostrar_exemplos()
                continue
            
            elif not pergunta:
                print("❌ Digite uma pergunta válida!")
                continue
            
            # Processar pergunta
            contador_perguntas += 1
            print(f"🤔 Processando... (Pergunta #{contador_perguntas})")
            
            try:
                inicio = datetime.now()
                resultado = self.qa_chain.invoke({"query": pergunta})
                fim = datetime.now()
                tempo = (fim - inicio).total_seconds()
                
                print(f"\n🤖 RESPOSTA:")
                print("-" * 40)
                print(resultado["result"])
                print("-" * 40)
                print(f"⏱️ Tempo: {tempo:.2f}s")
                print(f"📚 Fontes consultadas: {len(resultado['source_documents'])}")
                
                # Mostrar fontes (opcional)
                resposta_fontes = input("\n🔍 Ver fontes? (s/n): ").lower()
                if resposta_fontes == 's':
                    self._mostrar_fontes(resultado['source_documents'])
                
            except Exception as e:
                print(f"❌ Erro: {e}")
                print("💡 Verifique se o Ollama está rodando")
    
    def _mostrar_info(self):
        """Mostra informações do sistema"""
        print(f"\n📊 INFORMAÇÕES DO SISTEMA:")
        print(f"   • Documentos carregados: {len(self.documentos_carregados)}")
        print(f"   • Chunks criados: {len(self.chunks)}")
        print(f"   • Modelo LLM: {self.modelo_llm}")
        print(f"   • Vector Store: {self.vectorstore_tipo}")
        print(f"   • Pasta documentos: {self.pasta_documentos}")
    
    def _mostrar_exemplos(self):
        """Mostra exemplos de perguntas"""
        exemplos = [
            "Qual o melhor exercício para peito?",
            "Como fazer agachamento corretamente?",
            "Programa de treino para iniciantes",
            "Exercícios para fortalecer o core",
            "Diferença entre treino funcional e musculação",
            "Como treinar em casa sem equipamentos?",
            "Quantas repetições fazer para hipertrofia?",
            "Exercícios para dor nas costas"
        ]
        
        print(f"\n💡 EXEMPLOS DE PERGUNTAS:")
        for i, exemplo in enumerate(exemplos, 1):
            print(f"   {i}. {exemplo}")
    
    def _mostrar_fontes(self, source_docs):
        """Mostra as fontes consultadas"""
        print(f"\n📚 FONTES CONSULTADAS:")
        for i, doc in enumerate(source_docs, 1):
            fonte = doc.metadata.get('source', 'N/A')
            print(f"\n   {i}. {os.path.basename(fonte)}")
            print(f"      Trecho: {doc.page_content[:150]}...")
    
    # MÉTODO PRINCIPAL - EXECUTA TODOS OS PASSOS
    def executar_pipeline_completo(self):
        """Executa todo o pipeline RAG"""
        print("🚀 INICIANDO PIPELINE COMPLETO RAG")
        print("=" * 60)
        
        try:
            # Passo 1: Carregar documentos
            self.carregar_documentos()
            
            # Passo 2: Dividir em chunks
            self.dividir_textos_em_chunks()
            
            # Passo 3: Gerar embeddings
            self.gerar_embeddings()
            
            # Passo 4: Criar vector store
            self.criar_vector_store()
            
            # Passo 5: Configurar LangChain
            self.configurar_langchain()
            
            print(f"\n✅ PIPELINE COMPLETO!")
            print("=" * 60)
            
            # Passo 6: Interface
            self.interface_terminal()
            
        except Exception as e:
            print(f"\n❌ ERRO NO PIPELINE: {e}")
            print("💡 Verifique os pré-requisitos e tente novamente")

# FUNÇÃO PARA CARREGAR RAG EXISTENTE
def carregar_rag_existente(pasta_docs="documentos_treino", modelo="deepseek-r1:1.5b", vectorstore_tipo="FAISS"):
    """Carrega um RAG já configurado"""
    print("📂 Carregando RAG existente...")
    
    rag = RAGTreinosCompleto(pasta_docs, modelo)
    
    # Configurar embeddings
    rag.gerar_embeddings()
    
    # Carregar vectorstore
    if vectorstore_tipo == "FAISS" and os.path.exists("vectorstore_faiss"):
        rag.vectorstore = FAISS.load_local(
            "vectorstore_faiss", 
            rag.embeddings,
            allow_dangerous_deserialization=True
        )
        rag.vectorstore_tipo = "FAISS"
        print("✅ FAISS vectorstore carregado")
        
    elif vectorstore_tipo == "Chroma" and os.path.exists("vectorstore_chroma"):
        rag.vectorstore = Chroma(
            persist_directory="vectorstore_chroma",
            embedding_function=rag.embeddings
        )
        rag.vectorstore_tipo = "Chroma"
        print("✅ Chroma vectorstore carregado")
    else:
        raise FileNotFoundError("Vectorstore não encontrado! Execute o pipeline completo primeiro.")
    
    # Configurar LangChain
    rag.configurar_langchain()
    
    return rag

# EXECUÇÃO PRINCIPAL
if __name__ == "__main__":
    print("🏋️ RAG TREINOS - SISTEMA COMPLETO")
    print("=" * 50)
    
    # Verificar se já existe vectorstore
    if os.path.exists("vectorstore_faiss") or os.path.exists("vectorstore_chroma"):
        print("📂 Vectorstore encontrado!")
        escolha = input("Usar vectorstore existente? (s/n): ").lower()
        
        if escolha == 's':
            try:
                # Determinar tipo de vectorstore
                tipo = "FAISS" if os.path.exists("vectorstore_faiss") else "Chroma"
                rag = carregar_rag_existente(vectorstore_tipo=tipo)
                rag.interface_terminal()
            except Exception as e:
                print(f"❌ Erro ao carregar: {e}")
                print("🔄 Executando pipeline completo...")
                rag = RAGTreinosCompleto()
                rag.executar_pipeline_completo()
        else:
            # Pipeline completo
            rag = RAGTreinosCompleto()
            rag.executar_pipeline_completo()
    else:
        # Primeira execução
        print("🆕 Primeira execução - Pipeline completo")
        rag = RAGTreinosCompleto()
        rag.executar_pipeline_completo()