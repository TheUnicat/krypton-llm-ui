function chatScrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// JavaScript function to clear the chat messages
function clearChatMessages(id=null) {
  const chatContainer = document.querySelector('.chat-container');
  if (!id) {
      localStorage.removeItem("conversationId");
      chatContainer.innerHTML = ''; // Clears the chat container
      return;
      }

  const targetElement = chatContainer.querySelector(`#${id}`);

    let nextSibling = targetElement.nextElementSibling;

    // Remove all elements after the target element
    while (nextSibling) {
      const toRemove = nextSibling;
      nextSibling = nextSibling.nextElementSibling;
      chatContainer.removeChild(toRemove);
    }

}

async function selectConversation(conversationId) {
    try {
        let currentConversation = document.getElementById(localStorage.getItem("conversationId"));
        currentConversation.classList.remove('is-current-conversation');
    } catch(e) {
        console.error(e);
    }
  try {
    const response = await fetch(`/retrieve_conversation?id=${conversationId}`);
    const conversation = await response.json();
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.innerHTML = ''; // Clear existing messages

    for (const message of conversation.conversation) {
    let messageElement;

    if (typeof message.role === "string") {
        messageElement = appendMessage(message.role);
    } else {
        // Assuming message.role is an array and contains at least two elements
        messageElement = appendMessage(`${message.role[0]} ${message.role[1]}`);
    }

      // Create and append the message text div
      const messageTextElement = messageElement.querySelector('.message-content .message-text');
      messageTextElement.innerHTML = processText(message.message);

      message.image_data.forEach(item => {
        const img = new Image();
        img.src = "data:" + item.mime + ";base64," + item.base64;
        img.alt = 'Loaded from base64 data';
        img.style.width = '80%'; // Set the width or adjust as needed
        img.style.height = 'auto'; // Adjust height as needed
        messageTextElement.appendChild(img);
    });

      if (message.role === "You") {
          addEditButton(messageElement.querySelector('.message-content .message-toolbar'));
      }
      messageElement.id = message.id;

      // Append the complete message element to the chat container
      chatContainer.appendChild(messageElement);
    }

    // Update conversation ID in localStorage and scroll to the latest message
    localStorage.setItem("conversationId", conversationId);
    chatScrollToBottom();
    const item = document.getElementById(conversationId);
    item.classList.add('is-current-conversation');
  } catch (error) {
    console.error('Error fetching conversation:', error);
  }
}


const imagePaths = {
    "ChatGPT": "chatgpt.png",
    "MrEagle": "mreagles.png",
    "You": "you.jpg",
    "Claude": "claude.png",
    "Fireworks": "fireworks.png"
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
  let imagePath = "/images/" + imagePaths[author.split(" ")[0]];
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
  const conversationId = localStorage.getItem('conversationId');
    //default gpt-3.5-turbo
    const modelName = localStorage.getItem('modelName') || 'ChatGPT';
    const modelVersion = localStorage.getItem('modelVersion') || '3.5';
    const api = localStorage.getItem('api') || 'OpenAI';
    // Encode the prompt and include the model in the query string
    var messageElement = appendMessage(modelName);
    const messageContentElement = promptElement.querySelector('.message-content');

    const fileInput = document.getElementById('fileInputButton');
    const files = fileInput.files;

    if (files.length > 0) {
        // Directly append each file under the 'images' field
        Array.from(files).forEach(file => {
            // Create an image element for the selected file
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.style.width = '80%';
            img.style.height = 'auto';

            // Append the image element to the message-content element
            messageContentElement.appendChild(img);
        });
    }

      const imagesFlag = await uploadImages(); // This now returns a boolean
      // Modify the event source URL to include the images flag
      const eventSourceUrl = `/stream?id=${encodeURIComponent(conversationId)}&prompt=${encodeURIComponent(prompt)}&api=${encodeURIComponent(api)}&model_name=${encodeURIComponent(modelName)}&model_version=${encodeURIComponent(modelVersion)}&message_id=${encodeURIComponent(messageId)}&images=${imagesFlag}`;
      const eventSource = new EventSource(eventSourceUrl);




  eventSource.onmessage = async function(event) {
    let data = event.data;

    try {
        data = JSON.parse(data);
     if (data.conversation_id) {
        if (messageId) {
            clearChatMessages(messageId);
            messageElement = appendMessage(modelName);
        }
        localStorage.setItem('conversationId', data.conversation_id);  // Set the conversationId in localStorage
        promptElement.id = data.message_id;
       } else if (data.new_title) {
          await prependConversationItem({ "id": localStorage.getItem("conversationId"), "title": data.new_title });
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
        console.error(error);
        if (data === 'None') {
          if (!conversationId) {
            if (messageId) {
                await selectConversation(conversationId);
            }
               eventSource.close();
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
            // First, replace all newline characters with <br>
            const codeWithLineBreaks = match[1].replace(/\\n/g, '\n');

            // Wrap the modified code block with triple backticks and apply syntax highlighting
            const highlightedCode = applySyntaxHighlighting(`\`\`\`${codeWithLineBreaks}\`\`\``);
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
    conversations.reverse().forEach(conversation => prependConversationItem(conversation));
  } catch (error) {
    console.error('Failed to load recent conversations:', error);
  }
}

function prependConversationItem(conversation) {
  const conversationsList = document.querySelector('.conversations-list');
  const listItem = document.createElement('li');
  listItem.className = 'conversation-item';
  listItem.id = conversation.id; // Assuming conversation["id"] is the ID

  listItem.innerHTML = `
    <span class="title-text">${conversation.title.replace(/\\/g, '')}</span>
    <div class="conversation-toolbar">
      <button class="conversation-options-btn">
        <svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="icon-md">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M3 12C3 10.8954 3.89543 10 5 10C6.10457 10 7 10.8954 7 12C7 13.1046 6.10457 14 5 14C3.89543 14 3 13.1046 3 12ZM10 12C10 10.8954 10.8954 10 12 10C13.1046 10 14 10.8954 14 12C14 13.1046 13.1046 14 12 14C10.8954 14 10 13.1046 10 12ZM17 12C17 10.8954 17.8954 10 19 10C20.1046 10 21 10.8954 21 12C21 13.1046 20.1046 14 19 14C17.8954 14 17 13.1046 17 12Z" fill="black"/>
        </svg>
      </button>
      <div class="options-bar" style="display: none;">
        <div class="delete-option">Delete</div>
        <div class="rename-option">Rename</div>
      </div>
    </div>`;

  const optionsBtn = listItem.querySelector('.conversation-options-btn');
  const optionsBar = listItem.querySelector('.options-bar');

    const renameOption = listItem.querySelector('.rename-option'); // Assuming your rename option has a class 'rename-option'

    renameOption.addEventListener('click', function() {
      const currentTitleElement = this.closest('.conversation-item').querySelector('.title-text');
      const currentTitle = currentTitleElement.innerText;

      const modalContent = `
        <textarea id="renameTextarea" placeholder="Enter new name">${currentTitle}</textarea>
        <button id="submitRename">Submit</button>
      `;

      // Assuming openModal function exists and takes HTML string as parameter
      openModal(modalContent);

      // Assuming modal's submit button can be immediately selected after modal is opened
      document.querySelector('#submitRename').addEventListener('click', function() {
        const newName = document.querySelector('#renameTextarea').value.trim();
        if (newName) {
          currentTitleElement.innerText = newName;
          renameConversation(conversation.id, newName); // Placeholder function
          closeModal(); // Assuming you have a function to close the modal
        }
      });
    });


  optionsBtn.addEventListener('click', (event) => {
    const isDisplayed = optionsBar.style.display !== 'none';
    optionsBar.style.display = isDisplayed ? 'none' : 'block';
    listItem.classList.toggle('options-bar-visible', !isDisplayed);
    event.stopPropagation();
  });

  document.addEventListener('click', (event) => {
    if (!listItem.contains(event.target)) {
      optionsBar.style.display = 'none';
      listItem.classList.remove('options-bar-visible');
    }
  });

    // Add event listener for Delete option
    const deleteOption = listItem.querySelector('.delete-option');
    deleteOption.addEventListener('click', function() {
      // Call the delete function
      deleteConversation(conversation.id);

      // Find the nearest ancestor .conversation-item element and remove it from the DOM
      const conversationItem = this.closest('.conversation-item');
      if (conversationItem) {
        conversationItem.remove();
      }

      if (conversation.id === localStorage.getItem("conversationId")) {
        clearChatMessages();
      }
    });

  listItem.setAttribute('onclick', `selectConversation('${conversation.id}')`);

  conversationsList.prepend(listItem); // Changed to prepend to add it at the beginning of the list
}


document.addEventListener('DOMContentLoaded', async function() {
    loadAndAppendModels();
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

            // clear the prompt input after sending the message
            if (userPrompt.value !== undefined) {
                userPrompt.value = '';
                adjustTextareaHeight(userPrompt);
                sendBtn.disabled = true;
                sendBtn.style.background = 'lightgrey'; // Disabled state color
            }
        }
    }
    sendBtn.addEventListener('click', sendMessage);

    userPrompt.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage(); // Call the sendMessage function
        }
    });

    userPrompt.addEventListener('input', function() {
        const text = userPrompt.value.trim();
        sendBtn.disabled = text.length === 0;
        if(text.length > 0) {
            sendBtn.style.background = '';
        } else {
            sendBtn.style.background = 'lightgrey'; // Disabled state color
        }
    });
});

// Define the toggleSidebar function at a higher scope
function toggleSidebar() {
  var sidebar = document.getElementById('sidebar');
  var toggleButton = document.getElementById('sidebarToggle');
  var isOpen = sidebar.style.left === '0px';

    sidebar.style.left = isOpen ? '-20%' : '0px';
    toggleButton.style.left = isOpen ? '1%' : '19%';

    // If the sidebar is opened, shift the chat-container and input-container to the right
    document.querySelector('.chat-container').style.marginLeft = isOpen ? '0' : '4%';
    document.querySelector('.input-container').style.marginLeft = isOpen ? '0' : '4%';
    document.querySelector('#modelInfoContainer').style.marginLeft = isOpen ? '0' : '15%';

  localStorage.setItem("sidebarStatus", !isOpen);
}

// Use the DOMContentLoaded event listener to wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
  var toggleButton = document.getElementById('sidebarToggle');
  populateConversationHistory();

  // Attach the toggleSidebar function to the click event of the toggle button
  toggleButton.addEventListener('click', toggleSidebar);

  // Retrieve the sidebar status from localStorage and open/close the sidebar accordingly
  var savedStatus = localStorage.getItem("sidebarStatus") === 'true'; // Ensure correct comparison
  if (savedStatus) {
    toggleSidebar(); // This will open the sidebar if it was open previously
  }
});


// Event listener for the new chat button
document.addEventListener('DOMContentLoaded', async function () {
  const newChatButton = document.getElementById('new-chat-button');
  await populateConversationHistory();
  if (localStorage.getItem("conversationId") != null) {
    selectConversation(localStorage.getItem("conversationId"));
  } else {
    clearChatMessages();
  }

  newChatButton.addEventListener('click', function () {
    document.getElementById(localStorage.getItem("conversationId")).classList.remove("is-current-conversation");
    clearChatMessages();
  });

  hljs.highlightAll();
  // Function to display the current model
  function displayCurrentModel() {
    document.getElementById('modelName').textContent = localStorage.getItem('modelName') || 'ChatGPT';
    document.getElementById('modelVersion').textContent = localStorage.getItem('modelVersion') || '3.5';

  }

  // Function to change the model
  window.changeModel = function(api, modelName, modelVersion) {
    localStorage.setItem('api', api);
    localStorage.setItem('modelName', modelName);
    localStorage.setItem('modelVersion', modelVersion);
    displayCurrentModel();
    toggleDropdown(); // Hide the dropdown after selection
  }

  // Function to toggle the dropdown visibility
  const dropdown = document.getElementById('modelDropdown');
  function toggleDropdown() {
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
  }

  // Event listener for the model display click
  document.getElementById('modelName').addEventListener('click', toggleDropdown);
  document.getElementById('modelVersion').addEventListener('click', toggleDropdown);

    document.addEventListener('click', (event) => {
      // Check if the clicked target is outside the modelDropdown element
      if (!document.getElementById("modelInfoContainer").contains(event.target)) {
        // Hide the modelDropdown
        if (dropdown.style.display !== 'none') {
            dropdown.style.display = 'none';
        }
      }
    });

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
    selectConversation(localStorage.getItem("conversationId"));
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

async function deleteConversation(conversationId) {
    await fetch(`/delete_conversation?id=${conversationId}`);
}

async function renameConversation(conversationId, newName) {
    await fetch(`/rename_conversation?id=${conversationId}&new_name=${newName}`);
}

function saveMessage(messageElement, newText) {
  getAI(newText, messageElement, messageElement.id);
}

document.getElementById('attachmentBtn').addEventListener('click', function() {
    document.getElementById('fileInputButton').click();
});

function loadAndAppendModels() {
    fetch('/get_models_html')
    .then(response => response.ok ? response.text() : Promise.reject('Failed to load'))
    .then(html => document.getElementById('modelDropdown').innerHTML = html)
    .catch(error => console.error('There has been a problem with your fetch operation:', error));
}

const modal = document.getElementById('modal');
const overlay = document.getElementById('modal-overlay');
const closeButton = document.querySelector('.close-button');
const modalBody = document.getElementById('modal-body');
const modalContent = document.getElementById('modal-content');

function openModal(htmlContent) {
    modalBody.innerHTML = htmlContent; // Set the HTML content
    modal.style.visibility = 'visible';
    modal.style.opacity = 1;
    closeButton.style.display = 'flex';
    overlay.style.visibility = 'visible';
    overlay.style.opacity = 1;
    modalContent.style.display = 'flex';
}

function closeModal() {
    modal.style.visibility = 'hidden';
    modal.style.opacity = 0;
    overlay.style.visibility = 'hidden';
    overlay.style.opacity = 0;
}

closeButton.addEventListener('click', closeModal);


function adjustTextareaHeight(textarea) {
  // Immediately adjust the height to 'auto' to calculate the potential scrollHeight correctly
  textarea.style.height = 'auto';

  // Determine if the content exceeds the visible boundary of the textarea
  const isOverflowing = textarea.scrollHeight > textarea.clientHeight;
  const maxHeight = 150;

  // Only adjust the height if there is overflow
  if (isOverflowing) {
    let newHeight = textarea.scrollHeight;
    if (newHeight > maxHeight) {
      newHeight = maxHeight; // Ensure the new height does not exceed the max height
      textarea.style.overflowY = 'scroll'; // Enable scrolling
    } else {
      textarea.style.overflowY = 'hidden'; // Hide scrollbar if the content is within the max height
    }
    textarea.style.height = newHeight + 'px';
  } else {
    textarea.style.height = '25px'; // Default height
    textarea.style.overflowY = 'hidden'; // Hide scrollbar when not overflowing
  }
}

document.getElementById('prompt').addEventListener('input', function() {
  adjustTextareaHeight(this);
});

document.getElementById('fileInputButton').addEventListener('change', function() {
  var fileInput = document.getElementById('fileInputButton');
  var files = fileInput.files;
  var previewContainer = document.getElementById('previewContainer');


  // Show or hide the preview container based on file selection
  previewContainer.style.display = files.length > 0 ? 'flex' : 'none';

  // Create previews for selected files
  Array.from(files).forEach(file => {
    if(file.type === "image/png" || file.type === "image/jpeg") {
      var filePreview = document.createElement('div');
      filePreview.className = 'file-preview';

      var fileName = document.createElement('span');
      fileName.className = 'file-name';
      fileName.textContent = file.name;

      var closeBtn = document.createElement('div');
      closeBtn.className = 'close-btn';
      closeBtn.textContent = '×';
      closeBtn.onclick = function() {
        // Logic to handle removing individual file previews
        filePreview.remove();
        // Additional logic needed to adjust file input if removing specific files
        // Consideration needed for managing fileInput.files since it's a read-only property
      };

      filePreview.appendChild(closeBtn);
      filePreview.appendChild(fileName);
      previewContainer.appendChild(filePreview);
    }
  });
});

async function uploadImages() {
  const fileInput = document.getElementById('fileInputButton');
  const files = fileInput.files;

  if (files.length > 0) {
    const formData = new FormData();
    // Directly append each file under the 'images' field
    Array.from(files).forEach(file => {
      formData.append('images', file);
    });

    try {
      // Perform the actual upload
      await fetch('/upload_images', {
        method: 'POST',
        body: formData,
      });

      //clear the input after upload
      previewContainer.innerHTML = "";
      previewContainer.style.display = 'none';
      fileInput.value = "";

      return true; // Indicate successful upload
    } catch (error) {
      console.error('Error uploading images:', error);
      return false; // Indicate failure
    }
  } else {
      return false;
  }
}
