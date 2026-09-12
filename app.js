const prompt = document.querySelector('#prompt');
const response = document.querySelector('#assistant-response');
const send = document.querySelector('#send-button');
const voice = document.querySelector('#voice-button');
const transcript = document.querySelector('#transcript');
const speakToggle = document.querySelector('#speak-toggle');

function addMessage(role, text) {
  const item = document.createElement('li');
  item.className = `message ${role}`;
  item.innerHTML = `<span>${role === 'user' ? 'YOU' : 'MEGATRON'}</span><p></p>`;
  item.querySelector('p').textContent = text;
  transcript.prepend(item);
}

function say(text) {
  if (!speakToggle.checked || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.06;
  utterance.pitch = 0.88;
  window.speechSynthesis.speak(utterance);
}

function offlineReply(text) {
  const lower = text.toLowerCase();
  if (lower.includes('help')) return 'I am online. Ask for the time, date, a briefing, or start a search with “search for”.';
  if (lower.includes('time')) return `It is ${new Intl.DateTimeFormat([], { hour: 'numeric', minute: '2-digit' }).format(new Date())}.`;
  if (lower.includes('date')) return `Today is ${new Intl.DateTimeFormat([], { weekday: 'long', month: 'long', day: 'numeric' }).format(new Date())}.`;
  return `I heard “${text}”. Start Megatron with server.py to enable notes, tasks, and web search commands.`;
}

async function askMegatron(text) {
  const message = text.trim();
  if (!message) return;
  addMessage('user', message);
  response.textContent = 'Processing request…';
  prompt.value = '';
  try {
    const request = await fetch('/api/assistant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });
    if (!request.ok) throw new Error('Assistant service unavailable');
    const result = await request.json();
    addMessage('assistant', result.reply);
    response.textContent = result.reply;
    say(result.reply);
    if (result.action?.url) window.open(result.action.url, '_blank', 'noopener');
  } catch {
    const reply = offlineReply(message);
    addMessage('assistant', reply);
    response.textContent = reply;
    say(reply);
  }
}

send.addEventListener('click', () => askMegatron(prompt.value));
prompt.addEventListener('keydown', (event) => { if (event.key === 'Enter') askMegatron(prompt.value); });
document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => askMegatron(button.dataset.prompt)));

voice.addEventListener('click', () => {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) { response.textContent = 'Voice input is not available in this browser. Type a request instead.'; return; }
  const recognition = new Recognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  voice.textContent = '◉';
  response.textContent = 'Listening…';
  recognition.onresult = (event) => askMegatron(event.results[0][0].transcript);
  recognition.onerror = () => { response.textContent = 'I could not hear that. Please try again.'; };
  recognition.onend = () => { voice.textContent = '⌁'; };
  recognition.start();
});

function updateClock() {
  document.querySelector('#clock').textContent = new Intl.DateTimeFormat([], { hour: '2-digit', minute: '2-digit' }).format(new Date());
}
updateClock();
setInterval(updateClock, 30000);
