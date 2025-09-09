# agent.py
import os
from dotenv import load_dotenv # Importar para carregar variáveis de ambiente
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import Ferramentas # Importe suas ferramentas

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Embora o ChatOpenAI geralmente pegue automaticamente, é bom ter aqui.


# Histórico de chat global (simplificado para um único chat por vez)
chat_history = []

# Carrega o prompt
with open("prompt.txt", "r", encoding="utf-8") as file:
    system_prompt = file.read()


# Definir o prompt do agente
prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        MessagesPlaceholder(variable_name="chat_history"), # Para o contexto da conversa
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"), # Essencial para o agente usar ferramentas
    ]
)

# Inicializar o LLM
# Garanta que o LLM tenha acesso à sua chave de API, idealmente via variável de ambiente.
llm = ChatOpenAI(model="gpt-4o", temperature=0.3) # Temperatura mais baixa para agentes focados em tarefas

# Inicializar as ferramentas
appointment_tools = Ferramentas()
tools = [
    appointment_tools.consulta_disponibilidade,
    appointment_tools.agenda_consulta
]


# Criar o agente
agent = create_openai_tools_agent(llm, tools, prompt)

# Criar o executor do agente
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True) # verbose=True é ótimo para depuração!

def run_chat_agent(user_message: str) -> str:
    global chat_history # Indica que vamos modificar a variável global

    try:
        # Adicionar a mensagem do usuário ao histórico ANTES de chamar o agente
        chat_history.append(HumanMessage(content=user_message))

        # Chamar o agente com a nova mensagem e o histórico
        # O AgentExecutor.invoke processará a mensagem, decidirá usar ferramentas se necessário,
        # e retornará a resposta final do agente.
        response = agent_executor.invoke({"input": user_message, "chat_history": chat_history})
        agent_response_content = response["output"]

        # Adicionar a resposta do agente ao histórico
        chat_history.append(AIMessage(content=agent_response_content))

        return agent_response_content
    except Exception as e:
        print(f"Erro ao executar o agente: {e}")
        return "Desculpe, houve um erro ao processar sua solicitação."

def reset_chat_history():
    """Reseta o histórico do chat."""
    global chat_history # Indica que vamos modificar a variável global
    chat_history = []
    print("Histórico do chat foi resetado.")