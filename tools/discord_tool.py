import json
import discord
import asyncio
import threading
from queue import Queue

# Define global variables but do not execute blocking operations
discord_token = None
client = None


def run_async_in_thread(async_func, *args):
    """
    Runs an async function in a separate thread, waits for the result, and returns it.
    This function is blocking and should be used to bridge async functions in sync code.
    """
    # Queue to store the async function's result or exception
    result_queue = Queue()

    def thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Schedule the coroutine to be run and wait for its result
            result = loop.run_until_complete(async_func(*args))
            result_queue.put(result)
        except Exception as e:
            result_queue.put(e)
        finally:
            loop.close()

    # Start the thread that runs the async function
    thread = threading.Thread(target=thread_target)
    thread.start()
    thread.join()  # Wait for the thread to finish

    # Retrieve the result from the queue
    result = result_queue.get()
    if isinstance(result, Exception):
        raise result  # Reraise exceptions from the async function

    return result

def setup_client():
    global client, discord_token

    # Load the token
    with open("krypton_storage/secrets.json", "r") as file:
        discord_token = json.load(file)["discord_bot_token"]

    # Initialize intents and client
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')


async def find_user_id_by_username(username):
    print("hi")
    for guild in client.guilds:  # Iterate through each guild the bot is part of
        async for member in guild.fetch_members(limit=None):  # Async iterator for members of the guild
            if member.name == username:  # Check if the member's username matches
                return member.id  # Return the user's ID if a match is found
    return None  # Return None if no user with the given username is found in any of the guilds

def send_message_to_user_sync(username, message):
    """
    Synchronous wrapper around the asynchronous send_message_to_user function.
    """
    return run_async_in_thread(send_message_to_user, username, message)

async def send_message_to_user(username, message):
    print("sending")
    print(username)
    user = await client.fetch_user(await find_user_id_by_username(username))
    if user:
        await user.send(message)
    else:
        print("User not found.")

def read_messages_from_dm_sync(username, n=10):
    """
    Synchronous wrapper around the asynchronous read_messages_from_dm function.
    """
    return run_async_in_thread(read_messages_from_dm, username, n)

async def read_messages_from_dm(username, n=10):
    user_id = await find_user_id_by_username(username)
    user = await client.fetch_user(user_id)
    dm_channel = await user.create_dm()
    reply_content = ""

    # Use an async for loop to iterate through the history
    async for message in dm_channel.history(limit=n):
        content = f"**{message.author}:**\n{message.content}"
        reply_content += content + '\n\n'
        # Break if reply_content exceeds a certain length to prevent excessive length
        if len(reply_content) >= 1900:
            reply_content = reply_content[:1900] + '... (truncated due to length)'
            break

    return reply_content

def run_bot():
    setup_client()
    client.run(discord_token)

def run_bot_in_thread():
    def target():
        setup_client()
        client.run(discord_token)

    bot_thread = threading.Thread(target=target)
    bot_thread.start()
    # Note: The thread will continue to run in the background,
    # allowing the main thread to proceed immediately.

# Call this function from your main code or entry point
run_bot_in_thread()

# This ensures the bot runs only if this script is executed directly, not when imported
if __name__ == "__main__":
    run_bot()