from telethon import TelegramClient, errors
from telethon.errors import FloodWaitError
from colorama import Fore, Style
import asyncio
import os
import random

# Function to save API details to a file
def save_api_details(api_id, api_hash, phone_number, session_num):
    with open(f"api_details_{session_num}.txt", "w") as file:
        file.write(f"{api_id}\n{api_hash}\n{phone_number}")

# Function to load API details from the file
def load_api_details(session_num):
    if os.path.exists(f"api_details_{session_num}.txt"):
        with open(f"api_details_{session_num}.txt", "r") as file:
            api_id = int(file.readline().strip())
            api_hash = file.readline().strip()
            phone_number = file.readline().strip()
            return api_id, api_hash, phone_number
    else:
        return None, None, None

# Function to remove a saved session
def remove_saved_session(session_num):
    session_file = f"session_{session_num}.session"
    api_details_file = f"api_details_{session_num}.txt"

    if os.path.exists(session_file):
        os.remove(session_file)
        print(Fore.GREEN + f"Deleted session file: {session_file}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"Session file not found: {session_file}" + Style.RESET_ALL)

    if os.path.exists(api_details_file):
        os.remove(api_details_file)
        print(Fore.GREEN + f"Deleted API details file: {api_details_file}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"API details file not found: {api_details_file}" + Style.RESET_ALL)

# Function to forward the original saved message
async def forward_original_saved_message(client, saved_message_id, saved_messages_chat, groups, session_name):
    for group in groups:
        try:
            await client.forward_messages(group.id, saved_message_id, saved_messages_chat)
            print(Fore.GREEN + f"[{session_name}] Message forwarded to group: {group.name}")
            delay = random.randint(5, 10)
            await asyncio.sleep(delay)
        except FloodWaitError as e:
            print(Fore.RED + f"[{session_name}] Rate limited. Waiting for {e.seconds} seconds...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(Fore.RED + f"[{session_name}] Error forwarding message to {group.name}: {str(e)}")

# Function to leave a group
async def leave_group(client, group, session_name):
    try:
        await client.kick_participant(group.id, 'me')
        print(Fore.YELLOW + f"[{session_name}] Left group: {group.name}" + Style.RESET_ALL)
        await asyncio.sleep(5)
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Failed to leave group {group.name}: {str(e)}")

# Function to process a single session
async def process_session(client, groups, session_name, saved_message_id, saved_messages_chat):
    try:
        print(Fore.CYAN + f"[{session_name}] Starting message forwarding." + Style.RESET_ALL)
        await forward_original_saved_message(client, saved_message_id, saved_messages_chat, groups, session_name)
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Error processing session: {str(e)}")

# Main function
async def main():
    print(Fore.RED + r"""
       ______  __  _____    _   __
      / / __ \/ / / /   |  / | / /
 __  / / / / / /_/ / /| | /  |/ / 
/ /_/ / /_/ / __  / ___ |/ /|  /  
\____/\____/_/ /_/_/  |_/_/ |_/   
                                  
""" + Style.RESET_ALL)

    print(Fore.GREEN + "Script made by @JohanOGU" + Style.RESET_ALL)

    print(Fore.CYAN + "Choose an option:" + Style.RESET_ALL)
    print("1 - Auto forward (forwards your last saved msg)")
    print("2 - Group leave (leaves groups where the message couldn't be forwarded)")
    print("3 - Remove a saved session login")
    option = int(input(Fore.CYAN + "Enter option number: " + Style.RESET_ALL))

    if option == 3:  # Remove a session
        session_num = int(input(Fore.CYAN + "Enter the session number to remove: " + Style.RESET_ALL))
        remove_saved_session(session_num)
        return

    num_sessions = int(input(Fore.CYAN + "Enter number of sessions: " + Style.RESET_ALL))

    clients = []
    for session_num in range(1, num_sessions + 1):
        print(Fore.CYAN + f"\nSession {session_num} Configuration:" + Style.RESET_ALL)

        api_id, api_hash, phone_number = load_api_details(session_num)

        if not api_id or not api_hash or not phone_number:
            api_id = int(input(Fore.CYAN + f"Enter API ID for Session {session_num}: " + Style.RESET_ALL))
            api_hash = input(Fore.CYAN + f"Enter API Hash for Session {session_num}: " + Style.RESET_ALL)
            phone_number = input(Fore.CYAN + f"Enter Phone Number for Session {session_num} (e.g. +1234567890): " + Style.RESET_ALL)
            save_api_details(api_id, api_hash, phone_number, session_num)

        session_name = f"session_{session_num}"
        client = TelegramClient(session_name, api_id, api_hash)
        try:
            await client.start(phone_number)
            print(Fore.GREEN + f"[{session_name}] Session started successfully.")
            clients.append((client, session_name))
        except Exception as e:
            print(Fore.RED + f"[{session_name}] Failed to start session: {str(e)}")

    rounds = int(input(Fore.CYAN + "\nEnter number of rounds for all groups: " + Style.RESET_ALL))
    interval = int(input(Fore.CYAN + "Enter delay (in seconds) after all groups are processed: " + Style.RESET_ALL))

    all_groups = []
    for client, session_name in clients:
        try:
            saved_messages_chat = await client.get_entity('me')
            messages = await client.get_messages(saved_messages_chat, limit=1)
            if not messages:
                print(Fore.RED + f"[{session_name}] No saved messages found.")
                continue
            saved_message_id = messages[0].id

            dialogs = await client.get_dialogs()
            groups = [dialog for dialog in dialogs if dialog.is_group]
            all_groups.append((client, groups, session_name, saved_message_id, saved_messages_chat))
            print(Fore.GREEN + f"[{session_name}] Found {len(groups)} groups.")
        except Exception as e:
            print(Fore.RED + f"[{session_name}] Failed to fetch data: {str(e)}")

    if option == 1:  # Auto forward
        for round_number in range(1, rounds + 1):
            print(Fore.YELLOW + f"\nStarting round {round_number}..." + Style.RESET_ALL)
            tasks = [
                process_session(client, groups, session_name, saved_message_id, saved_messages_chat)
                for client, groups, session_name, saved_message_id, saved_messages_chat in all_groups
            ]
            await asyncio.gather(*tasks)  # Concurrent execution of all sessions
            if round_number < rounds:
                print(Fore.CYAN + f"\nWaiting {interval} seconds before the next round..." + Style.RESET_ALL)
                await asyncio.sleep(interval)

    elif option == 2:  # Group leave
        for client, groups, session_name, saved_message_id, saved_messages_chat in all_groups:
            for group in groups:
                try:
                    await forward_original_saved_message(client, saved_message_id, saved_messages_chat, [group], session_name)
                except Exception:
                    await leave_group(client, group, session_name)

    print(Fore.GREEN + "All sessions finished." + Style.RESET_ALL)

    # Disconnect all clients at the end
    for client, session_name in clients:
        await client.disconnect()
        print(Fore.GREEN + f"[{session_name}] Disconnected successfully.")

if __name__ == "__main__":
    asyncio.run(main())