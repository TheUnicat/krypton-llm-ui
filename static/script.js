document.addEventListener('DOMContentLoaded', (event) => {
    const replyButton = document.getElementById('replyButton'); // Get the button by ID

    // Function to be called when button is clicked
    function getReply() {
        console.log("Button clicked!");
        // Your code to get a reply or perform an action goes here
    }

    // Check if the button exists and is not disabled before adding the event listener
    if (replyButton) {
        replyButton.addEventListener('click', function() {
            if (!this.disabled) {
                getReply();
            }
        });
    }
});

function chatScrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// JavaScript function to clear the chat messages
function clearChatMessages() {
  const chatContainer = document.querySelector('.chat-container');
  localStorage.removeItem("conversationId");
  chatContainer.innerHTML = ''; // Clears the chat container
}

async function selectConversation(conversationId) {
  try {
    const response = await fetch(`/retrieve_conversation?id=${conversationId}`);
    const conversation = await response.json();
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.innerHTML = ''; // Clear existing messages

    for (const message of conversation.conversation) {
      const messageElement = appendMessage(message.role);
      // Create and append the message text div
      const messageTextElement = messageElement.querySelector('.message-content .message-text');
      messageTextElement.innerHTML = processText(message.message);

      if (message.role == "You") {
          addEditButton(messageElement.querySelector('.message-content .message-toolbar'));
      }
      messageElement.id = message.id;

      // Append the complete message element to the chat container
      chatContainer.appendChild(messageElement);
    }

    // Update conversation ID in localStorage and scroll to the latest message
    localStorage.setItem("conversationId", conversationId);
    chatScrollToBottom();
  } catch (error) {
    console.error('Error fetching conversation:', error);
  }
}



const imagePaths = {
    "ChatGPT": "chatgpt.png",
    "MrEagle": "mreagles.png",
    "You": "you.jpg"
};

function addEditButton(targetElement) {
  // Create the button element
  const button = document.createElement('button');
  button.setAttribute('class', 'edit-btn');
  button.setAttribute('onclick', 'editMessage(this)');

  // Set the innerHTML of the button to include the SVG
  button.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-md">
  <path fill-rule="evenodd" clip-rule="evenodd" d="M13.2929 4.29291C15.0641 2.52167 17.9359 2.52167 19.7071 4.2929C21.4783 6.06414 21.4783 8.93588 19.7071 10.7071L18.7073 11.7069L11.1603 19.2539C10.7182 19.696 10.1489 19.989 9.53219 20.0918L4.1644 20.9864C3.84584 21.0395 3.52125 20.9355 3.29289 20.7071C3.06453 20.4788 2.96051 20.1542 3.0136 19.8356L3.90824 14.4678C4.01103 13.8511 4.30396 13.2818 4.7461 12.8397L13.2929 4.29291ZM13 7.41422L6.16031 14.2539C6.01293 14.4013 5.91529 14.591 5.88102 14.7966L5.21655 18.7835L9.20339 18.119C9.40898 18.0847 9.59872 17.9871 9.7461 17.8397L16.5858 11L13 7.41422ZM18 9.5858L14.4142 6.00001L14.7071 5.70712C15.6973 4.71693 17.3027 4.71693 18.2929 5.70712C19.2831 6.69731 19.2831 8.30272 18.2929 9.29291L18 9.5858Z" fill="currentColor">
  </path></svg>
  `;

  // Append the newly created button to the targetElement
  targetElement.appendChild(button);
}


function appendMessage(author, text = null) {
  const chatMessagesContainer = document.querySelector('.chat-container');

  // Initialize an empty message element
  let messageElement = document.createElement('div');
  messageElement.classList.add('message');
  let imagePath = "/images/" + imagePaths[author];
  messageElement.innerHTML = `
    <img class="profile-picture" src=${imagePath} alt="${author}">
    <div class="message-content">
        <div class="user-name">${author}</div>
        <div class="message-text">${text ? text : ""}</div>
        <div class="message-toolbar"></div>
    </div>

  `;

  // Append the new message element with the edit button to the chat container
  chatMessagesContainer.append(messageElement);
  chatScrollToBottom();

  // Return the new message element in case further manipulation is needed
  return messageElement;
}



async function getAI(prompt, promptElement, messageId=null) {
  const chatMessagesContainer = document.querySelector('.chat-container');
  const conversationId = localStorage.getItem('conversationId'); // Ensure this is the correct key
      // Retrieve the model from localStorage, defaulting to 'gpt-3.5-turbo' if not found
    const modelName = localStorage.getItem('modelName') || 'ChatGPT';
    const modelVersion = localStorage.getItem('modelVersion') || '3.5';

    // Encode the prompt and include the model in the query string
    const eventSource = new EventSource(`/stream?id=${conversationId}&prompt=${encodeURIComponent(prompt)}&model_name=${encodeURIComponent(modelName)}&model_version=${encodeURIComponent(modelVersion)}&message_id=${encodeURIComponent(messageId)}`);
    // Pass the conversationId as a query parameter


  var messageElement = appendMessage(modelName);
  let accumulatedResponse = "";


  eventSource.onmessage = async function(event) {
    //console.log(event);
    let data = event.data;

    try {
        data = JSON.parse(data);
     if (data.conversation_id) {
        if (messageId) {
            clearChatMessages();
            await selectConversation(conversationId);
            messageElement = appendMessage(modelName);
        }
        localStorage.setItem('conversationId', data.conversation_id);  // Set the conversationId in localStorage
        promptElement.id = data.message_id;
       } else if (data.new_title) {
          await selectConversation(localStorage.getItem("conversationId"));
          eventSource.close();
          return;
        }    else if (data.error) {
            let errorMessage = JSON.stringify(data.error);

            // Define the formatted error message with the error-box class
            let formattedErrorMessage = `<div class="error-box">${errorMessage}</div>`;

            // Append the formatted error message to the current innerHTML of the messageElement
            messageElement.innerHTML += formattedErrorMessage;

             chatScrollToBottom();
            eventSource.close();
        }
    } catch (error) {
        if (data === 'None') {
          if (!conversationId) {
            eventSource.close(); // Close the connection if it's the last message
            return;
            }
        } else {
              // If the message element's text is empty, set its text. Otherwise, create a new message element
              const messageTextDiv = messageElement.querySelector('.message-text');
              messageTextDiv.innerHTML = processText(data);

              hljs.highlightAll();
              chatScrollToBottom();
        }
    }
    chatScrollToBottom();
  };

  // Handle any errors that occur by logging them
  eventSource.onerror = function(error) {
    console.error('EventSource failed:', error);
    eventSource.close(); // Close the connection on error
  };
}

function processText(text) {
    // Regular expression to match code blocks and non-code blocks
    const regex = /```([\s\S]*?)```|([^`]+)/g;
    let parts = [];
    let match;

    // Iterate over the text and collect all matches
    while ((match = regex.exec(text)) !== null) {
        // If it's a code block (matched by the first group of the regex), keep it unchanged
        if (match[1]) {
            // Wrap the code block with triple backticks and apply syntax highlighting
            const highlightedCode = applySyntaxHighlighting(`\`\`\`${match[1]}\`\`\``);
            parts.push(highlightedCode);
        } else if (match[2]) {
            // If it's not a code block (matched by the second group of the regex), replace \n with <br>
            const modifiedText = match[2].replace(/\\n/g, '<br>');
            parts.push(modifiedText);
        }
    }

    // Join all parts back together
    return parts.join('');
}

function applySyntaxHighlighting(codeBlock) {
    // Extract the code from within the triple backticks, and add a newline
    const code = codeBlock.slice(3, -3).trim();

    // Apply syntax highlighting using highlight.js
    // `language` variable can be used to detect the language automatically or set manually
    const highlightedCode = hljs.highlightAuto(code).value;
    const language = hljs.highlightAuto(code).language;

    // Return the highlighted code wrapped in a div with pre and code tags, including a top bar
    // with the language name and a "Copy code" button
    return `
        <div class="code-container" style="position: relative;">
            <div class="code-header">
                <span class="language-label">${language}</span>
                <button class="copy-btn" onclick="copyToClipboard(this)">Copy code</button>
            </div>
            <pre><code class="hljs">${highlightedCode}</code></pre>
        </div>
    `;
}


function copyToClipboard(button) {
    // Get the code block within the same container as the button
    const codeContainer = button.closest('.code-container');
    const codeBlock = codeContainer.querySelector('pre code');

    // Copy the code text to the clipboard
    navigator.clipboard.writeText(codeBlock.textContent.split("\n").slice(1).join("\n")).then(() => {
        // Provide feedback that the text was copied
        button.textContent = 'Copied!';
        // Reset button text after 2 seconds
        setTimeout(() => { button.textContent = 'Copy code'; }, 2000);
    }).catch(err => {
        console.error('Failed to copy text', err);
        // Provide feedback for a failed copy
        button.textContent = 'Copy failed';
    });
}



// Assume this initialization code is already part of your code base, calling highlightAll on DOMContentLoaded
document.addEventListener('DOMContentLoaded', (event) => {
    hljs.highlightAll();
});

    const textarea = document.getElementById('prompt');
    const sendButton = document.getElementById('sendBtn');

    textarea.addEventListener('input', () => {
      const text = textarea.value.trim();
      if (text) {
        sendButton.disabled = false;
        sendButton.style.background = 'blue'; // Change this to any color you prefer
      } else {
        sendButton.disabled = true;
        sendButton.style.background = 'lightgrey';
      }
    });

async function populateConversationHistory() {
  try {
    const response = await fetch('/get_recent_conversations');
    const conversations = await response.json();
    const conversationsList = document.querySelector('.conversations-list');
    conversationsList.innerHTML = ''; // Clear the list before adding new items

    // Loop through conversations and prepend them to the list
    conversations.forEach(conversation => prependConversationItem(conversation));
  } catch (error) {
    console.error('Failed to load recent conversations:', error);
  }
}

function prependConversationItem(conversation) {
  const conversationsList = document.querySelector('.conversations-list');
  const listItem = document.createElement('li');
  listItem.className = 'conversation-item';
  listItem.id = conversation.id; // Assuming conversation["id"] is the ID
  listItem.textContent = conversation.title;
  listItem.setAttribute('onclick', `selectConversation('${conversation.id}')`); // Example of a function to select a conversation
  conversationsList.appendChild(listItem); // Prepend to add it at the beginning of the list
}

populateConversationHistory();


document.addEventListener('DOMContentLoaded', function() {
    const sendBtn = document.getElementById('sendBtn');
    const userPrompt = document.getElementById('prompt');

    // Function to handle sending the message
    function sendMessage() {
        // Check if the button is not disabled
        if (!sendBtn.disabled) {
            // Extracting the text from the element with ID 'prompt'
            const userText = userPrompt.innerText || userPrompt.value; // Works for both divs and input fields

            // Calling appendMessage with "You" and the extracted text
            let promptElement = appendMessage("You", userText);
            // Calling getAI function afterwards
            getAI(userText, promptElement);

            // Optionally, clear the prompt input after sending the message
            if (userPrompt.value !== undefined) {
                userPrompt.value = ''; // Only clear if it's an input field
                sendBtn.disabled = true;
                sendBtn.style.background = 'lightgrey'; // Disabled state color
            }
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    userPrompt.addEventListener('keydown', function(event) {
        // Check if the ENTER key was pressed
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage(); // Call the sendMessage function
        }
    });


    // Optionally, enable the button when there's text to send
    userPrompt.addEventListener('input', function() {
        const text = userPrompt.value.trim();
        sendBtn.disabled = text.length === 0;
        if(text.length > 0) {
            sendBtn.style.background = ''; // Restore original background or set to a new color
        } else {
            sendBtn.style.background = 'lightgrey'; // Disabled state color
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
  var sidebar = document.getElementById('sidebar');
  var toggleButton = document.getElementById('sidebarToggle');


  populateConversationHistory();

  toggleButton.addEventListener('click', function () {
    var isOpen = sidebar.style.left === '0px';
    sidebar.style.left = isOpen ? '-20%' : '0px';
    toggleButton.style.left = isOpen ? '1%' : '21%';

    // If the sidebar is opened, shift the chat-container and input-container to the right
    document.querySelector('.chat-container').style.marginLeft = isOpen ? '0' : '4%';
    document.querySelector('.input-container').style.marginLeft = isOpen ? '0' : '4%';
    document.querySelector('#modelInfoContainer').style.marginLeft = isOpen ? '0' : '15%';
  });
});

// Event listener for the new chat button
document.addEventListener('DOMContentLoaded', function () {
  const newChatButton = document.getElementById('new-chat-button');

  if (localStorage.getItem("conversationId") != null) {
    selectConversation(localStorage.getItem("conversationId"));
  } else {
    clearChatMessages();
  }

  newChatButton.addEventListener('click', function () {
    clearChatMessages();
  });
});

document.addEventListener('DOMContentLoaded', function() {
  // Function to display the current model
  function displayCurrentModel() {
    const currentModelName = localStorage.getItem('modelName') || 'ChatGPT';
    document.getElementById('modelName').textContent = currentModelName;
    const currentModelVersion = localStorage.getItem('modelVersion') || '3.5';
    document.getElementById('modelVersion').textContent = currentModelVersion;
  }

  // Function to change the model
  window.changeModel = function(modelName, modelVersion) {
    localStorage.setItem('modelName', modelName);
    localStorage.setItem('modelVersion', modelVersion);
    displayCurrentModel();
    toggleDropdown(); // Hide the dropdown after selection
  }

  // Function to toggle the dropdown visibility
  function toggleDropdown() {
    console.log("OwO toggling");
    const dropdown = document.getElementById('modelDropdown');
    console.log(dropdown);
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
  }

  // Event listener for the model display click
  document.getElementById('modelName').addEventListener('click', toggleDropdown);

  displayCurrentModel(); // Display the current model when the page loads
});

function editMessage(editButton) {
  const messageElement = editButton.closest('.message');
  const messageContent = messageElement.querySelector('.message-content .message-text');
  const originalText = messageContent.innerText;

  // Indicate editing is starting
  messageElement.classList.add('editing');

  const textarea = document.createElement('textarea');
  textarea.value = originalText;
  textarea.rows = 4;
  textarea.style.width = '100%';
  messageContent.innerHTML = '';
  messageContent.appendChild(textarea);

  // Create Cancel button
  const cancelButton = document.createElement('button');
  cancelButton.innerText = 'Cancel';
  cancelButton.onclick = function() {
    messageContent.innerText = originalText;
    cancelButton.remove();
    saveButton.remove();
    // Editing is done, remove the class
    messageElement.classList.remove('editing');
  };

  // Create Save button
  const saveButton = document.createElement('button');
  saveButton.innerText = 'Save';
  saveButton.onclick = function() {
    saveMessage(messageElement, textarea.value);
    messageContent.innerText = textarea.value;
    cancelButton.remove();
    saveButton.remove();
    // Editing is done, remove the class
    messageElement.classList.remove('editing');
  };

  messageContent.appendChild(cancelButton);
  messageContent.appendChild(saveButton);
}

function saveMessage(messageElement, newText) {
  getAI(newText, messageElement, messageElement.id);
}