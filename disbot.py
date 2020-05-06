import discord
from discord import utils
from discord.ext import commands
import os

PREFIX = '.'
client = commands.Bot(command_prefix=PREFIX)
client.remove_command('help')


@client.event
async def on_command_error(ctx, error):
    pass


@client.command(pass_context=True)
async def help(ctx):
    emb = discord.Embed(title='Навигация по командам', colour=discord.Color.green())
    emb.add_field(name='{}clear'.format(PREFIX), value='Очистка чата')
    emb.add_field(name='{}mute'.format(PREFIX), value='Блокировка чата')
    emb.add_field(name='{}clear'.format(PREFIX), value='Снятие ограничение чата')
    emb.add_field(name='{}bt'.format(PREFIX), value='Писать от имени бота')
    emb.add_field(name='{}bma'.format(PREFIX), value='Писать от имени бота в личные сообщения, анонимно. '
                                                     'После команды указать пользователя через @, '
                                                     'затем указать количество слов в заголовке сообщения, '
                                                     'после написать сообщение'
                                                     '\n.bma @Nick_Name 2 Школа 124 Завтра уроков нет.'
                                                     '\nВ заголовке 2 слова - Школа 124')
    emb.add_field(name='{}bmt'.format(PREFIX), value='Писать от имени бота в личные сообщения. Аналогично с .bma')
    await ctx.channel.purge(limit=1)
    await ctx.send(embed=emb)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def clear(ctx, ammount=0):
    await ctx.channel.purge(limit=ammount + 1)


@client.command()
@commands.has_permissions(administrator=True)
async def bt(ctx):
    await ctx.channel.purge(limit=1)
    bttext = ' '.join(ctx.message.content.split(' ')[1:])
    await ctx.send(bttext)


@client.command()
@commands.has_permissions(administrator=True)
async def bma(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    n = int(' '.join(ctx.message.content.split(' ')[2:3]))
    bmatext = ' '.join(ctx.message.content.split(' ')[n + 3:])
    # await member.send(bttext)
    titletext = ' '.join(ctx.message.content.split(' ')[3:n + 3])
    emb = discord.Embed(title=titletext, colour=discord.Color.dark_blue())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name='Специально для {}'.format(member), value=bmatext)
    emb.set_footer(text='Сообщение от анонима')
    await member.send(embed=emb)

@client.command()
async def bmt(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    n = int(' '.join(ctx.message.content.split(' ')[2:3]))
    bmatext = ' '.join(ctx.message.content.split(' ')[n + 3:])
    # await member.send(bttext)
    titletext = ' '.join(ctx.message.content.split(' ')[3:n + 3])
    emb = discord.Embed(title=titletext, colour=discord.Color.orange())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name='Специально для {}'.format(member), value=bmatext)
    emb.set_footer(text='Сообщение от {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)
    await member.send(embed=emb)



@client.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    emb = discord.Embed(title='Молчанка', colour=discord.Color.red())
    mute_role = discord.utils.get(ctx.message.guild.roles, name='MUTE')
    await member.add_roles(mute_role)
    # await ctx.send(f'{member.mention} - выдана молчанка.')
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name='Не надо так', value='{}'.format(member.mention) + ', тебя заставили замолчать.')
    # emb.set_footer(text='{}'.format(ctx.author.name) + ' заставил замаолчать.', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)


@client.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    emb = discord.Embed(title='Помилование', colour=discord.Color.blue())
    mute_role = discord.utils.get(ctx.message.guild.roles, name='MUTE')
    await member.remove_roles(mute_role)
    # await ctx.send(f'Молчанка снята с {member.mention}.')
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name='Молчанка снята', value='{}'.format(member.mention) + ', можешь говорить.')
    emb.set_footer(text='{}'.format(ctx.author.name) + ' разрешил говорить.', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)


@client.event
async def on_ready():
    print('Logged on as!')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Выставляю 2'))


@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == POST_ID:
        channel = client.get_channel(payload.channel_id)  # получаем объект канала
        message = await channel.fetch_message(payload.message_id)  # получаем объект сообщения
        member = utils.get(message.guild.members,
                           id=payload.user_id)  # получаем объект пользователя который поставил реакцию

        try:
            emoji = str(payload.emoji)  # эмоджик который выбрал юзер
            role = utils.get(message.guild.roles, id=ROLES[emoji])  # объект выбранной роли (если есть)

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


@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)  # получаем объект канала
    message = await channel.fetch_message(payload.message_id)  # получаем объект сообщения
    member = utils.get(message.guild.members,
                       id=payload.user_id)  # получаем объект пользователя который поставил реакцию

    try:
        emoji = str(payload.emoji)  # эмоджик который выбрал юзер
        role = utils.get(message.guild.roles, id=ROLES[emoji])  # объект выбранной роли (если есть)

        await member.remove_roles(role)
        print('[SUCCESS] Role {1.name} has been remove for user {0.display_name}'.format(member, role))

    except KeyError as e:
        print('[ERROR] KeyError, no role found for ' + emoji)
    except Exception as e:
        print(repr(e))


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(title='Ошибка использование команды', colour=discord.Color.dark_teal())
        emb.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        emb.add_field(name='{}'.format(ctx.author.name), value='рановато тебе использовать эту команду')
        await ctx.send(embed=emb)


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(title='Ошибка использование команды', colour=discord.Color.dark_teal())
        emb.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        emb.add_field(name='{}'.format(ctx.author.name), value='рановато тебе использовать эту команду')
        await ctx.send(embed=emb)


@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(title='Ошибка использование команды', colour=discord.Color.dark_teal())
        emb.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        emb.add_field(name='{}'.format(ctx.author.name), value='рановато тебе использовать эту команду')
        await ctx.send(embed=emb)


@bt.error
async def bt_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(title='Ошибка использование команды', colour=discord.Color.dark_teal())
        emb.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        emb.add_field(name='{}'.format(ctx.author.name), value='рановато тебе использовать эту команду')
        await ctx.send(embed=emb)

@bma.error
async def bma_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(title='Ошибка использование команды', colour=discord.Color.dark_teal())
        emb.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        emb.add_field(name='{}'.format(ctx.author.name), value='рановато тебе использовать эту команду')
        await ctx.send(embed=emb)


TOKEN = os.environ.get('BOT_TOKEN')
POST_ID = 695341653266923530
ROLES = {
    '🦘': 695228071388643348,  # 9V
    '🐵': 695228339773898802,  # 9G
    '🦚': 695220848390307891,  # 6A
    '🐙': 695221302574972989,  # 6B
    '🦔': 695221905908695121,  # 6V
    '🦀': 695227323397439520,  # 5G
    '🐟': 695959589669306429  # Индивидуальное обучение
}
EXCROLES = ()
MAX_ROLES_PER_USER = 1
# RUN
client.run(str(TOKEN))
