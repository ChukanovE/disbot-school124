import discord
from discord import utils


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_raw_reaction_add(self, payload):
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = utils.get(message.guild.members, id=payload.user_id)

        try:
            emoji = str(payload.emoji)
            role = utils.get(message.guild.roles, id=ROLES[emoji])

            if (len([i for i in member.roles if i.id not in EXCROLES]) <= MAX_ROLES_PER_USER):
                await member.add_roles(role)
                print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))
            else:
                await message.remove_reaction(payload.emoji, member)
                print('[ERROR] Too many roles for user {0.display_name}'.format(member))
        except KeyError as e:
            print('[ERROR] KeyError, no role found for ' + emoji)
        except Exception as e:
            print(repr(e))


    async def on_raw_reaction_remove(self, payload):
        channel = self.get_channel(payload.channel_id)  # получаем объект канала
        message = await channel.fetch_message(payload.message_id)  # получаем объект сообщения
        member = utils.get(message.guild.members, id=payload.user_id)  # получаем объект пользователя который поставил реакцию

        try:
            emoji = str(payload.emoji)  # эмоджик который выбрал юзер
            role = utils.get(message.guild.roles, id=ROLES[emoji])  # объект выбранной роли (если есть)
            await member.remove_roles(role)
            print('[SUCCESS] Role {1.name} has been remove for user {0.display_name}'.format(member, role))
        except KeyError as e:
            print('[ERROR] KeyError, no role found for ' + emoji)
        except Exception as e:
            print(repr(e))

TOKEN = 'Njk1MzMxNTg5MDM0NDc1NTgw.XoYoCw.eJLQ7ScSEhSF0sP4yDYF2SkbLMc'

POST_ID = 695341653266923530

ROLES = {
    '🦘': 695228071388643348, #9V
    '🐵': 695228339773898802, #9G
    '🦚': 695220848390307891, #6A
    '🐙': 695221302574972989, #6B
    '🦔': 695221905908695121, #6V
    '🦀': 695227323397439520 #5G
}

EXCROLES = ()

MAX_ROLES_PER_USER = 1
client = MyClient()
client.run(TOKEN)
