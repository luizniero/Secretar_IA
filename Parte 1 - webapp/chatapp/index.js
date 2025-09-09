// Inicializa a conexão com o servidor WebSocket
var socket = new WebSocket('ws://localhost:8765');

// Define o que acontece quando o servidor envia uma mensagem.
// chama mostrarMensagem com o parâmetro 'bot' (usado na escolha do classname no css)
socket.onmessage = function(event) {
  mostrarMensagem("Bot", event.data, "bot");
};

// Lida com o envio do formulário
window.onload = function() {
  var form = document.getElementById('form');
  var input = document.getElementById('input');

  form.onsubmit = function(event) {
    event.preventDefault();

    var mensagem = input.value;
    if (!mensagem) return;

    mostrarMensagem("Você", mensagem, "user");
    // envio a mensagem para o servidor websocket
    socket.send(mensagem);
    input.value = '';
  };
};

// Função para adicionar mensagem no chat
function mostrarMensagem(remetente, texto, classe) {
  var chat = document.getElementById('chat');
  var div = document.createElement('div');
  div.className = 'msg ' + classe;
  div.textContent = texto;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}
