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

// JavaScript function to clear the chat messages
function clearChatMessages() {
  const chatContainer = document.querySelector('.chat-container');
  localStorage.removeItem("conversationId");
  chatContainer.innerHTML = ''; // Clears the chat container
}

const namesToImages = {

}



function selectConversation(conversationId) {
  fetch(`/retrieve_conversation?id=${conversationId}`)
    .then(response => response.json())
    .then(conversation => {
      const chatContainer = document.querySelector('.chat-container');
      chatContainer.innerHTML = ''; // Clear existing messages

      conversation.conversation.forEach(message => {
        const messageElement = appendMessage(message.role);



        // Create and append the message text div
        const messageTextElement = document.createElement('div');
        messageTextElement.classList.add('message-text');
        messageTextElement.innerHTML = processText(message.message);

        messageElement.querySelector('.message-content').appendChild(messageTextElement);

        // Append the complete message element to the chat container
        chatContainer.appendChild(messageElement);

        // Update conversation ID in localStorage and scroll to the latest message
        localStorage.setItem("conversationId", conversationId);
        chatContainer.scrollTop = chatContainer.scrollHeight;
      });
    })
    .catch(error => console.error('Error fetching conversation:', error));
}


const imagePaths = {
    "ChatGPT": "chatgpt.png",
    "MrEagle": "mreagles.png",
    "You": "you.jpg"
};


function appendMessage(author, text=null) {
  const chatMessagesContainer = document.querySelector('.chat-container');

  // Initialize an empty message element
  let messageElement = document.createElement('div');
  messageElement.classList.add('message');
  let imagePath;
  imagePath = "/images/" + imagePaths[author];
  messageElement.innerHTML = `
    <img class="profile-picture" src=${imagePath} alt="ChatGPT">
    <div class="message-content">
      <div class="user-name">${author}</div>
      <div class="message-text">${text ? text : ""}</div>
    </div>
  `;

  chatMessagesContainer.append(messageElement);
  return messageElement;

  }

function getAI(prompt) {
  const chatMessagesContainer = document.querySelector('.chat-container');
  const conversationId = localStorage.getItem('conversationId'); // Ensure this is the correct key
      // Retrieve the model from localStorage, defaulting to 'gpt-3.5-turbo' if not found
    const modelName = localStorage.getItem('modelName') || 'ChatGPT';
    const modelVersion = localStorage.getItem('modelVersion') || '3.5';

    // Encode the prompt and include the model in the query string
    const eventSource = new EventSource(`/stream?id=${conversationId}&prompt=${encodeURIComponent(prompt)}&model_name=${encodeURIComponent(modelName)}&model_version=${encodeURIComponent(modelVersion)}`);
    // Pass the conversationId as a query parameter


  let messageElement = appendMessage(modelName);

  eventSource.onmessage = function(event) {
    console.log(event);
    let data = event.data;


    try {
        data = JSON.parse(data);
     if (data.conversation_id) {
        localStorage.setItem('conversationId', data.conversation_id);  // Set the conversationId in localStorage
       } else if (data.error) {
            let errorMessage = JSON.stringify(data.error);

            // Define the formatted error message with the error-box class
            let formattedErrorMessage = `<div class="error-box">${errorMessage}</div>`;

            // Append the formatted error message to the current innerHTML of the messageElement
            messageElement.innerHTML += formattedErrorMessage;
             chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
            eventSource.close();
        }


    } catch (error) {
        if (data === 'None') {
          eventSource.close(); // Close the connection if it's the last message
        } else {
          console.log("extra error", error);
          // If the message element's text is empty, set its text. Otherwise, create a new message element
          const messageTextDiv = messageElement.querySelector('.message-text');
          messageTextDiv.innerHTML = processText(messageTextDiv.innerHTML + data);
          hljs.highlightAll();

        }
    }

    // Auto-scroll to the newest message
    chatMessagesContainer.scrollBottom = chatMessagesContainer.scrollHeight;
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
            const modifiedText = match[2].replace(/\n/g, '<br>');
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
    const codeBlock = button.previousElementSibling.querySelector('code');
    // Split the text content into an array of lines
    const lines = codeBlock.textContent.split('\n');
    // Remove the first line (which contains the language name)
    lines.shift();
    // Join the remaining lines back into a single string
    const codeToCopy = lines.join('\n');

    // Copy the modified code to the clipboard
    navigator.clipboard.writeText(codeToCopy).then(() => {
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


console.log("Hewwo");

    const textarea = document.getElementById('prompt');
    console.log(textarea);
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
    conversations.forEach(conversation => prependConversationItem(conversationsList, conversation));
  } catch (error) {
    console.error('Failed to load recent conversations:', error);
  }
}

function prependConversationItem(conversationsList, conversation) {
  const listItem = document.createElement('li');
  listItem.className = 'conversation-item';
  listItem.id = conversation.id; // Assuming conversation["id"] is the ID
  listItem.textContent = conversation.title;
  listItem.setAttribute('onclick', `selectConversation('${conversation.id}')`); // Example of a function to select a conversation
  conversationsList.appendChild(listItem); // Prepend to add it at the beginning of the list
}

// Call the main function to fetch and populate conversations
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
            appendMessage("You", userText);

            // Calling getAI function afterwards
            getAI(userText);

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
            event.preventDefault(); // Prevent the default action to avoid form submission or newline
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


