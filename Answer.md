# RAG (Retrieval-Augmented Generation) - Explicação Completa

## 🔍 O que é RAG?

**RAG (Retrieval-Augmented Generation)** é uma técnica que combina:
- **Retrieval (Recuperação)**: Busca informações relevantes em uma base de conhecimento
- **Generation (Geração)**: Usa um LLM para gerar respostas baseadas nas informações recuperadas

### Como funciona:
1. **Pergunta do usuário** → Sistema busca documentos relevantes
2. **Documentos encontrados** → Servem como contexto para o LLM
3. **LLM gera resposta** → Baseada no contexto + conhecimento próprio

## 🏋️ Escolha do Tema: Treinos e Exercícios Físicos

### Por que escolhi esse tema?

1. **Informação Específica**: Treinos requerem instruções precisas sobre técnicas, repetições, séries
2. **Segurança**: Informações incorretas podem causar lesões
3. **Personalização**: Diferentes níveis (iniciante, intermediário, avançado)
4. **Atualização Constante**: Novas técnicas e metodologias surgem frequentemente
5. **Pessoais**: Gosto muito de treinar porem as vezes não encontra uma boa divisão de treinos, por isso desedi implementar no sistema de chat

### Como o RAG ajuda nesse contexto?

- **Precisão**: Respostas baseadas em literatura científica e protocolos validados
- **Contextualização**: Considera nível do praticante, objetivos, limitações
- **Segurança**: Evita recomendações genéricas que podem ser perigosas
- **Atualização**: Fácil incorporação de novos estudos e metodologias
- **Personalização**: Adapta recomendações baseadas em perfil específico

## 🔧 Pipeline RAG Implementado

### 1. **Carregamento de Documentos**
```
📄 Tipos suportados: PDF, TXT, DOCX, MD
📊 Seu dataset: 15 arquivos, 758 documentos, 1.1M caracteres
```

### 2. **Chunking (Divisão em Pedaços)**
```
✂️ Configuração:
   • Tamanho: 1000 caracteres
   • Overlap: 200 caracteres
   • Resultado: 1598 chunks
```

### 3. **Embeddings (Vetorização)**
```
🧠 Modelo: sentence-transformers/all-MiniLM-L6-v2
   • Dimensão: 384
   • Normalização: Sim
   • Dispositivo: CPU
```

### 4. **Vector Store (Banco de Vetores)**
```
🗄️ FAISS (Facebook AI Similarity Search)
   • Índice: 1598 documentos
   • Busca: Similaridade coseno
   • Armazenamento: Local
```

### 5. **LLM e Chain**
```
🤖 Modelo: deepseek-r1:1.5b (via Ollama)
🔗 LangChain: RetrievalQA
📝 Prompt: Personalizado para treinos
```

## 📈 Vantagens do Sistema

### Para Usuários:
- Respostas específicas e contextualizadas
- Informações baseadas em fontes confiáveis
- Segurança nas recomendações
- Interface simples e intuitiva

### Para Desenvolvedores:
- Escalabilidade (fácil adicionar novos documentos)
- Flexibilidade (diferentes modelos e configurações)
- Transparência (mostra fontes das respostas)
- Custo baixo (modelo local)

## 🎯 Casos de Uso Práticos

### Perguntas que o sistema pode responder:
- "Qual exercício para fortalecer o core?"
- "Como fazer agachamento corretamente?"
- "Programa de treino para hipertrofia"
- "Exercícios para reabilitação de joelho"
- "Diferença entre treino funcional e musculação"

### Informações fornecidas:
- Técnica correta de execução
- Número de séries e repetições
- Músculos trabalhados
- Variações do exercício
- Precauções e contraindições

## 🔄 Fluxo Completo do Sistema

```
[Pergunta] → [Busca Vetorial] → [Recupera Documentos] → [LLM + Contexto] → [Resposta]
    ↓              ↓                    ↓                     ↓              ↓
"Treino para   Embeddings        4 docs mais          Prompt com        Resposta
 peito?"       da pergunta       similares            contexto          detalhada
```

## 📊 Métricas do Sistema Atual

- **Base de Conhecimento**: 15 PDFs especializados e 8 ficheiros md
- **Cobertura**: Treinos de força, cardio, funcional, reabilitação
- **Processamento**: 1598 chunks indexados
- **Velocidade**: ~2-3 segundos por resposta
- **Qualidade**: Respostas baseadas em fontes técnicas

## 🚀 Próximos Passos Sugeridos

1. **Ampliar Base**: Adicionar mais documentos científicos
2. **Melhorar Embeddings**: Testar modelos multilíngues
3. **Interface Web**: Criar interface mais amigável
4. **Feedback Loop**: Sistema de avaliação das respostas
5. **Especialização**: RAGs específicos por modalidade