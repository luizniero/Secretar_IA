# chat_server.py
import asyncio
import websockets
from agent import run_chat_agent, reset_chat_history # Importe as funções atualizadas

async def handle_connection(websocket):
    print("Nova conexão estabelecida.")
    # Resetar o histórico do chat para cada nova conexão para garantir um novo começo
    #reset_chat_history()
    await websocket.send("Olá! Sou a secretar-IA do consultório dos agentes. Como posso te ajudar hoje?")
    async for message in websocket:
        print(f"[Usuário]: {message}")
        try:
            # Use run_chat_agent para processar a mensagem
            response = run_chat_agent(message)
            await websocket.send(response)
        except Exception as e:
            print(f"Erro ao processar mensagem com o agente: {e}")
            await websocket.send("Desculpe, houve um problema ao processar sua solicitação. Por favor, tente novamente mais tarde.")

async def main():
    async with websockets.serve(handle_connection, "localhost", 8765):
        print("Servidor WebSocket rodando em ws://localhost:8765")
        await asyncio.Future()  # Executa para sempre

if __name__ == "__main__":
    asyncio.run(main())