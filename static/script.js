// ── Application State ────────────────────────────────────────────────────────
let messages = [];            // UI message objects
let conversationHistory = []; // {role, content} pairs sent to /chat
let isLoading = false;

// ── DOM Elements ─────────────────────────────────────────────────────────────
const welcomeScreen     = document.getElementById('welcomeScreen');
const messagesContainer = document.getElementById('messagesContainer');
const loadingIndicator  = document.getElementById('loadingIndicator');
const messagesEnd       = document.getElementById('messagesEnd');
const clearBtn          = document.getElementById('clearBtn');
const chatForm          = document.getElementById('chatForm');
const messageInput      = document.getElementById('messageInput');
const sendButton        = document.getElementById('sendButton');
const sendIcon          = document.getElementById('sendIcon');
const loadingSpinner    = document.getElementById('loadingSpinner');

// Preference selects
const styleSelect = document.getElementById('styleSelect');
const mediumSelect = document.getElementById('mediumSelect');
const skillSelect  = document.getElementById('skillSelect');
const focusSelect  = document.getElementById('focusSelect');

// ── Initialise ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  setupEventListeners();
  updateSendButton();
});

function setupEventListeners() {
  chatForm.addEventListener('submit', handleSubmit);
  clearBtn.addEventListener('click', clearChat);
  messageInput.addEventListener('input', handleInputChange);
  messageInput.addEventListener('keydown', handleKeyDown);
}

// ── Input Helpers ─────────────────────────────────────────────────────────────
function handleSubmit(e) {
  e.preventDefault();
  const content = messageInput.value.trim();
  if (!content || isLoading) return;
  sendMessage(content);
}

function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSubmit(e);
  }
}

function handleInputChange() {
  autoResizeTextarea();
  updateSendButton();
}

function autoResizeTextarea() {
  messageInput.style.height = 'auto';
  const newHeight = Math.min(messageInput.scrollHeight, 128);
  messageInput.style.height = newHeight + 'px';
}

function updateSendButton() {
  const hasContent = messageInput.value.trim().length > 0;
  sendButton.disabled = !hasContent || isLoading;
}

// ── Preference Reader ─────────────────────────────────────────────────────────
/**
 * Build a preferences object from the current dropdown values.
 * Null-coalesces empty strings so unset fields are excluded cleanly.
 */
function getPreferences() {
  const prefs = {
    style:       styleSelect.value  || null,
    medium:      mediumSelect.value || null,
    skill_level: skillSelect.value  || null,
    focus:       focusSelect.value  || null,
  };
  // Return null when every field is unset (no preference context needed).
  const hasAny = Object.values(prefs).some(v => v !== null);
  return hasAny ? prefs : null;
}

/** Human-readable summary of active preferences for the pref badge. */
function getActivePrefLabel() {
  const parts = [];
  if (styleSelect.value)  parts.push(styleSelect.options[styleSelect.selectedIndex].text);
  if (mediumSelect.value) parts.push(mediumSelect.options[mediumSelect.selectedIndex].text);
  if (skillSelect.value)  parts.push(skillSelect.options[skillSelect.selectedIndex].text);
  if (focusSelect.value)  parts.push(focusSelect.options[focusSelect.selectedIndex].text);
  return parts.length > 0 ? parts.join(' · ') : null;
}

// ── Core Send Logic ───────────────────────────────────────────────────────────
async function sendMessage(content) {
  const userMessage = {
    id: Date.now().toString(),
    content: content,
    type: 'user',
    timestamp: new Date(),
  };
  messages.push(userMessage);
  displayMessage(userMessage);

  messageInput.value = '';
  messageInput.style.height = 'auto';
  hideWelcomeScreen();
  showClearButton();
  setLoadingState(true);

  // Append the user turn to history before sending.
  conversationHistory.push({ role: 'user', content: content });

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message:     content,
        history:     conversationHistory.slice(0, -1), // history without current turn
        preferences: getPreferences(),
      }),
    });

    const data = await response.json();
    const isError =
      !data.reply ||
      data.reply.startsWith('Error:') ||
      data.reply.startsWith('System Error:');

    const aiMessage = {
      id: (Date.now() + 1).toString(),
      content: data.reply || 'No response received.',
      type: 'ai',
      prefLabel: getActivePrefLabel(),
      timestamp: new Date(),
      isError: isError,
    };
    messages.push(aiMessage);
    displayMessage(aiMessage);

    // Append assistant reply to history for subsequent turns.
    if (!isError) {
      conversationHistory.push({ role: 'assistant', content: data.reply });
    } else {
      // Remove the user turn we pushed if there was an error.
      conversationHistory.pop();
    }

  } catch (error) {
    conversationHistory.pop(); // roll back the failed user turn
    const errorMessage = {
      id: (Date.now() + 1).toString(),
      content: 'Error: ' + error.message,
      type: 'ai',
      timestamp: new Date(),
      isError: true,
    };
    messages.push(errorMessage);
    displayMessage(errorMessage);
  } finally {
    setLoadingState(false);
  }
}

// ── Message Rendering ─────────────────────────────────────────────────────────
function displayMessage(message) {
  const messageEl = document.createElement('div');
  messageEl.className = 'message ' + message.type;

  const time = message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // Avatar icons: person for user, palette for AI
  const avatarIcon = message.type === 'user'
    ? `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none"
         viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
         <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
         <circle cx="12" cy="7" r="4"/>
       </svg>`
    : `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none"
         viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
         <circle cx="12" cy="12" r="10"/>
         <circle cx="8.5" cy="9" r="1.5" fill="currentColor" stroke="none"/>
         <circle cx="15.5" cy="9" r="1.5" fill="currentColor" stroke="none"/>
         <circle cx="7"    cy="14" r="1.5" fill="currentColor" stroke="none"/>
         <circle cx="17"   cy="14" r="1.5" fill="currentColor" stroke="none"/>
         <path d="M12 20c2 0 4-1.5 4-4h-8c0 2.5 2 4 4 4z"/>
       </svg>`;

  const senderLabel = message.type === 'user' ? 'You' : 'Art Inspiration Agent';

  // Preference badge on AI messages when preferences are active.
  const prefBadge = (message.type === 'ai' && message.prefLabel)
    ? `<span class="pref-badge">${message.prefLabel}</span>`
    : '';

  messageEl.innerHTML = `
    <div class="message-wrapper">
      <div class="message-header">
        <div class="message-avatar">${avatarIcon}</div>
        <div class="message-info">
          <span class="message-sender">${senderLabel}</span>
          ${prefBadge}
        </div>
      </div>
      <div class="message-bubble">
        <p class="message-text">${escapeHtml(message.content)}</p>
      </div>
      <div class="message-footer">
        <span>${time}</span>
      </div>
    </div>
  `;

  messagesContainer.appendChild(messageEl);
  scrollToBottom();
}

/** Minimal HTML escape to prevent XSS from API responses. */
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── UI State Helpers ──────────────────────────────────────────────────────────
function setLoadingState(loading) {
  isLoading = loading;
  updateSendButton();
  messageInput.disabled = loading;

  if (loading) {
    loadingIndicator.style.display = 'block';
    sendIcon.style.display = 'none';
    loadingSpinner.style.display = 'block';
  } else {
    loadingIndicator.style.display = 'none';
    sendIcon.style.display = 'block';
    loadingSpinner.style.display = 'none';
  }

  if (loading) scrollToBottom();
}

function hideWelcomeScreen() { welcomeScreen.style.display = 'none'; }
function showWelcomeScreen()  { welcomeScreen.style.display = 'flex'; }
function showClearButton()    { clearBtn.style.display = 'flex'; }
function hideClearButton()    { clearBtn.style.display = 'none'; }

function clearChat() {
  messages = [];
  conversationHistory = [];
  messagesContainer.innerHTML = '';
  showWelcomeScreen();
  hideClearButton();
  setLoadingState(false);
  updateSendButton();
}

function scrollToBottom() {
  messagesEnd.scrollIntoView({ behavior: 'smooth' });
}
