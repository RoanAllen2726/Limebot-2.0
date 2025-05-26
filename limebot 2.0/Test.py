import asyncio
from twitchio.ext import commands

# Twitch bot class to handle chat messages
class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token='oauth:8iioachuzqm2rbwtn50levxrz9p69p', prefix='!', initial_channels=['robo2726'])
        self.channel = None  # Initialize self.channel as None

    async def event_ready(self):
        print(f'Logged in as {self.nick}')
        print(f'Connected to channel {self.connected_channels}')

        # Retrieve the channel object and store it in self.channel
        self.channel = self.get_channel('robo2726')
        if self.channel:
            print(f'Channel {self.channel.name} is ready for messages!')

    async def event_message(self, message):
        # Ensure the message has an author before processing
        if message.author and message.author.name.lower() == 'limebot2726':
            return  # Ignore messages from the bot itself

    async def send_chat_message(self, message):
        # Ensure that the channel object is available before sending messages
        if self.channel is not None:
            await self.channel.send(message)
        else:
            print("Channel is not ready yet.")

# Function to send a test message without capturing audio
async def send_test_message(bot):
    await bot.wait_for_ready()  # Wait until the bot is connected and ready
    while True:
        test_message = "This is a test message from the bot!"
        print(f"Sending: {test_message}")
        await bot.send_chat_message(test_message)

        # Wait for 10 seconds (or 300 seconds for 5 minutes) before sending again
        await asyncio.sleep(10)

if __name__ == '__main__':
    bot = TwitchBot()

    # Start the Twitch bot and the test message loop
    bot.loop.create_task(send_test_message(bot))
    bot.run()
