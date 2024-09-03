import nextcord
from nextcord.ext import commands
import requests
import json
import re
from base64 import b64encode, b64decode
import logging


logging.basicConfig(level=logging.INFO)

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


DISCORD_BOT_TOKEN = 'asd'
GITHUB_API_TOKEN = 'asd'


ALLOWED_CHANNEL_ID = asd
REWARD_ROLE_ID = asd

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}!')

def extract_hard_ids(text):
    pattern = re.compile(r'[a-fA-F0-9-]{36}')
    return pattern.findall(text)

def update_github_file(path, new_content):
    if not GITHUB_API_TOKEN:
        logging.error("GitHub API token is not set.")
        return
    
    repo = 'sad'
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_API_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            update_data = {
                "message": "Automated creation: HWID file",
                "content": b64encode(json.dumps(new_content).encode()).decode('utf-8')
            }
            response = requests.put(url, headers=headers, json=update_data)
            response.raise_for_status()
            logging.info("File created successfully.")
        else:
            logging.error(f"HTTP error occurred: {err}")
            return

    existing_content_encoded = data['content']
    existing_content = json.loads(b64decode(existing_content_encoded).decode('utf-8'))

    existing_content.extend(new_content)
    existing_content = list(set(existing_content))

    updated_content = json.dumps(existing_content, indent=4)
    encoded_content = b64encode(updated_content.encode()).decode('utf-8')

    update_data = {
        "message": "Automated update: Added HWIDs",
        "content": encoded_content,
        "sha": data['sha']
    }

    response = requests.put(url, headers=headers, json=update_data)
    response.raise_for_status()
    logging.info("File updated successfully.")

async def give_role(member):
    guild = member.guild
    role = guild.get_role(REWARD_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
            logging.info(f"Role {role.name} given to {member.name}.")
        except Exception as e:
            logging.error(f"Failed to give role to {member.name}: {e}")
    else:
        logging.error(f"Role with ID {REWARD_ROLE_ID} not found.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    hard_ids = extract_hard_ids(message.content)
    
    if hard_ids:
        logging.info(f"Found HWIDs in message from {message.author}: {hard_ids}")

        repo = 'asd'
        path = 'sad'
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {
            "Authorization": f"token {GITHUB_API_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            existing_content_encoded = data['content']
            existing_content = json.loads(b64decode(existing_content_encoded).decode('utf-8'))
        except requests.exceptions.HTTPError as err:
            if response.status_code == 404:
                existing_content = []
            else:
                logging.error(f"GitHub file fetch error: {err}")
                return

        hard_ids_set = set(existing_content)
        new_hard_ids = set(hard_ids)
        
        added_hard_ids = new_hard_ids - hard_ids_set
        if added_hard_ids:
            formatted_json = list(hard_ids_set.union(added_hard_ids))
            update_github_file(path, formatted_json)
            logging.info(f"Updated HWIDs in GitHub: {added_hard_ids}")

            for hwid in added_hard_ids:
                if hwid in message.content:
                    await give_role(message.author)
                    await message.channel.send(f"{message.author.mention} HWID `{hwid}`가 등록되었습니다!")
                    logging.info(f"Gave role to user {message.author} for HWID {hwid}")
                    
        else:
            await message.channel.send(f"{message.author.mention} HWID `{hard_ids[0]}`는 이미 등록된 HWID입니다.")
            logging.info(f"HWID {hard_ids[0]} already exists.")

    await bot.process_commands(message)


bot.run(DISCORD_BOT_TOKEN)
