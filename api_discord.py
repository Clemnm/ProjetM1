import discord
from discord.ext import commands
import asyncio
import threading
import config
from dotenv import load_dotenv
import os

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération du token depuis les variables d'environnement
TOKEN = os.getenv('DISCORD_TOKEN')

class DiscordBot:
    """Classe gérant le bot Discord dans un thread séparé pour éviter les conflits avec PyQt5."""
   
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.dm_messages = True
        intents.message_content = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.loop = asyncio.new_event_loop()
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.message_received_callback = None

        self.bot.event(self.on_ready)
        self.bot.event(self.on_message)

        self.bot_thread.start()

    async def on_ready(self):
        print(f'Bot {self.bot.user} ok')

    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if isinstance(message.channel, discord.DMChannel) and message.author.id in config.contacts.values():
            contact_name = next((name for name, id in config.contacts.items() if id == message.author.id), "Inconnu")
            print(f" Message reçu de {contact_name}: {message.content}")
            if self.message_received_callback:
                self.message_received_callback(message.content)

    def run_bot(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.bot.start(TOKEN))

    async def send_message_discord(self, contact_name, message):
        try:
            contact_id = config.contacts.get(contact_name)
            if contact_id:
                user = await self.bot.fetch_user(contact_id)
                await user.send(message)
                print(f" Message envoyé à {contact_name} ({contact_id}) !")
            else:
                print("Utilisateur non trouvé.")
        except Exception as e:
            print(f" Erreur d'envoi du message : {e}")
    
    async def send_emergency_message_discord(self):
        try:
            for contact_name, contact_id in config.contacts.items():
                user = await self.bot.fetch_user(contact_id)
                await user.send("Urgence ⚠️")
                print(f" Message d'urgence envoyé à {contact_name} ({contact_id}) !")
        except Exception as e:
            print(f" Erreur lors de l'envoi du message d'urgence : {e}")


    def send_message(self, contact_name, message):
        asyncio.run_coroutine_threadsafe(self.send_message_discord(contact_name, message), self.loop)
   

    def send_emergency_message(self):
        asyncio.run_coroutine_threadsafe(self.send_emergency_message_discord(), self.loop)

    def set_message_received_callback(self, callback):
        self.message_received_callback = callback

if __name__ == "__main__":
    bot = DiscordBot()
    bot.send_message("Test de bot")