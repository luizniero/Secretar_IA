# agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Carrega variáveis do .env (inclui OPENAI_API_KEY)
load_dotenv()

# Histórico de chat global (1 sessão por vez)
chat_history = []

# Lê o prompt de sistema
with open("prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()

# Inicializa o modelo (ajuste o nome/temperatura se quiser)
llm = ChatOpenAI(model="gpt-4o", temperature=0.3, max_tokens=500)

def run_chat_agent(user_message: str) -> str:
    """
    Envia a mensagem do usuário para a LLM junto com o histórico e retorna a resposta.
    Não usa tools nem agentes — apenas chat puro.
    """
    global chat_history

    try:
        # Monta a lista de mensagens na ordem correta:
        # 1) SystemMessage (instruções), 2) histórico acumulado, 3) a nova mensagem do usuário
        messages = [SystemMessage(content=system_prompt)] + chat_history + [HumanMessage(content=user_message)]

        # Chama o modelo diretamente
        ai_msg = llm.invoke(messages)
        print(f"[LLM]: {ai_msg.content}")

        # Atualiza o histórico
        chat_history.append(HumanMessage(content=user_message))
        chat_history.append(AIMessage(content=ai_msg.content))

        return ai_msg.content

    except Exception as e:
        print(f"Erro ao executar o chat: {e}")
        return "Desculpe, houve um erro ao processar sua solicitação."

def reset_chat_history():
    """Reseta o histórico do chat."""
    global chat_history
    chat_history = []
    print("Histórico do chat foi resetado.")
