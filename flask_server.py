# RAG_SERVER.PY - Servidor Web para Sistema RAG
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import time
from datetime import datetime
import threading
import queue

# Importar o sistema RAG existente
from RAG import carregar_rag_existente, RAGTreinosCompleto

app = Flask(__name__)
CORS(app)

# Variáveis globais
rag_system = None
chat_history = []
system_stats = {
    'total_queries': 0,
    'avg_response_time': 0,
    'system_status': 'Carregando...',
    'last_query_time': None
}

class RAGServer:
    def __init__(self):
        self.rag = None
        self.loading = True
        self.error = None
        
    def initialize_rag(self):
        """Inicializa o sistema RAG em thread separada"""
        try:
            print("🚀 Inicializando sistema RAG...")
            
            # Tentar carregar RAG existente
            if os.path.exists("vectorstore_faiss"):
                self.rag = carregar_rag_existente()
                print("✅ RAG carregado com sucesso!")
            else:
                print("❌ Vectorstore não encontrado. Execute RAG.py primeiro!")
                self.error = "Vectorstore não encontrado. Execute 'python RAG.py' primeiro para criar a base de dados."
                
        except Exception as e:
            print(f"❌ Erro ao carregar RAG: {e}")
            self.error = f"Erro ao carregar sistema: {str(e)}"
        finally:
            self.loading = False
    
    def query(self, question):
        """Processa uma pergunta e retorna resposta"""
        if self.loading:
            return {"error": "Sistema ainda carregando, aguarde..."}
        
        if self.error:
            return {"error": self.error}
        
        if not self.rag:
            return {"error": "Sistema RAG não inicializado"}
        
        try:
            start_time = time.time()
            
            # Processar pergunta
            resultado = self.rag.qa_chain.invoke({"query": question})
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Atualizar estatísticas
            system_stats['total_queries'] += 1
            system_stats['avg_response_time'] = (
                (system_stats['avg_response_time'] * (system_stats['total_queries'] - 1) + response_time) 
                / system_stats['total_queries']
            )
            system_stats['last_query_time'] = datetime.now().isoformat()
            system_stats['system_status'] = 'Online'
            
            # Preparar resposta
            sources = []
            for doc in resultado.get('source_documents', []):
                sources.append({
                    'filename': os.path.basename(doc.metadata.get('source', 'Unknown')),
                    'content': doc.page_content[:200] + "..."
                })
            
            response = {
                'answer': resultado['result'],
                'sources': sources,
                'response_time': round(response_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            # Salvar no histórico
            chat_history.append({
                'question': question,
                'answer': resultado['result'],
                'timestamp': datetime.now().isoformat(),
                'response_time': response_time
            })
            
            return response
            
        except Exception as e:
            return {"error": f"Erro ao processar pergunta: {str(e)}"}

# Inicializar servidor RAG
rag_server = RAGServer()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def api_query():
    """Endpoint para processar perguntas"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Pergunta não pode estar vazia"}), 400
        
        response = rag_server.query(question)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Retorna estatísticas do sistema"""
    stats = system_stats.copy()
    stats['chat_history_count'] = len(chat_history)
    stats['rag_loaded'] = rag_server.rag is not None
    stats['loading'] = rag_server.loading
    stats['error'] = rag_server.error
    
    if rag_server.rag:
        stats['documents_count'] = len(rag_server.rag.documentos_carregados) if hasattr(rag_server.rag, 'documentos_carregados') else 0
        stats['chunks_count'] = len(rag_server.rag.chunks) if hasattr(rag_server.rag, 'chunks') else 0
        stats['model'] = rag_server.rag.modelo_llm if hasattr(rag_server.rag, 'modelo_llm') else 'Unknown'
    
    return jsonify(stats)

@app.route('/api/history')
def api_history():
    """Retorna histórico de conversas"""
    return jsonify(chat_history[-20:])  # Últimas 20 conversas

@app.route('/api/examples')
def api_examples():
    """Retorna exemplos de perguntas"""
    examples = [
        "Qual o melhor exercício para peito?",
        "Como fazer agachamento corretamente?",
        "Programa de treino para iniciantes",
        "Exercícios para fortalecer o core",
        "Diferença entre treino funcional e musculação",
        "Como treinar em casa sem equipamentos?",
        "Quantas repetições fazer para hipertrofia?",
        "Exercícios para dor nas costas",
        "Técnica correta do deadlift",
        "Treino para ganhar massa muscular"
    ]
    return jsonify(examples)

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """Recebe feedback do usuário"""
    try:
        data = request.get_json()
        feedback = {
            'question': data.get('question'),
            'answer': data.get('answer'),
            'rating': data.get('rating'),
            'comment': data.get('comment', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Salvar feedback
        feedback_file = 'feedback_web.json'
        try:
            with open(feedback_file, 'r') as f:
                feedbacks = json.load(f)
        except FileNotFoundError:
            feedbacks = []
        
        feedbacks.append(feedback)
        
        with open(feedback_file, 'w') as f:
            json.dump(feedbacks, f, indent=2)
        
        return jsonify({"success": True, "message": "Feedback salvo com sucesso!"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin')
def admin():
    """Página de administração"""
    return render_template('admin.html')

@app.route('/api/admin/reload')
def api_admin_reload():
    """Recarrega o sistema RAG"""
    try:
        global rag_server
        rag_server = RAGServer()
        
        # Inicializar em thread separada
        thread = threading.Thread(target=rag_server.initialize_rag)
        thread.start()
        
        return jsonify({"success": True, "message": "Sistema sendo recarregado..."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_templates_folder():
    """Cria pasta templates se não existir"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("📁 Pasta 'templates' criada")

def create_static_folder():
    """Cria pasta static se não existir"""
    if not os.path.exists('static'):
        os.makedirs('static')
        print("📁 Pasta 'static' criada")

if __name__ == '__main__':
    print("🚀 INICIANDO SERVIDOR RAG")
    print("=" * 50)
    
    # Criar pastas necessárias
    create_templates_folder()
    create_static_folder()
    
    # Inicializar RAG em thread separada
    init_thread = threading.Thread(target=rag_server.initialize_rag)
    init_thread.start()
    
    print("🌐 Servidor será iniciado em:")
    print("   • http://localhost:5000")
    print("   • http://127.0.0.1:5000")
    print("=" * 50)
    
    # Iniciar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)