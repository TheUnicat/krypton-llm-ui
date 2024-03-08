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
        messageTextElement.textContent = message.message;

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

    console.log(data)

    try {
        data = JSON.parse(data);
     if (data.conversation_id) {
        localStorage.setItem('conversationId', data.conversation_id);  // Set the conversationId in localStorage
        }
    } catch (error) {
        if (data === 'None') {
          eventSource.close(); // Close the connection if it's the last message
        } else {
          // If the message element's text is empty, set its text. Otherwise, create a new message element
          const messageTextDiv = messageElement.querySelector('.message-text');
          messageTextDiv.innerHTML = messageTextDiv.innerText + data;

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

    // Populate the sidebar with the most recent conversations
    conversations.forEach(conversation => {
      const listItem = document.createElement('li');
      listItem.className = 'conversation-item';
      listItem.id = conversation.id; // Assuming conversation["id"] is the ID
      listItem.textContent = conversation.title;
      listItem.setAttribute('onclick', `selectConversation('${conversation.id}')`); // Example of a function to select a conversation
      conversationsList.appendChild(listItem);
      conversationsList.scrollBottom = conversationsList.scrollHeight;
    });
  } catch (error) {
    console.error('Failed to load recent conversations:', error);
  }
}

document.addEventListener('DOMContentLoaded', function() {
    const sendBtn = document.getElementById('sendBtn');
    const userPrompt = document.getElementById('prompt');

    sendBtn.addEventListener('click', function() {
        // Extracting the text from the element with ID 'prompt'
        const userText = userPrompt.innerText || userPrompt.value; // Works for both divs and input fields

        // Calling appendMessage with "You" and the extracted text
        appendMessage("You", userText);

        // Calling getAI function afterwards
        getAI(userText);

        // Optionally, clear the prompt input after sending the message
        if (userPrompt.value !== undefined) {
            userPrompt.value = ''; // Only clear if it's an input field
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


