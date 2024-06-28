"""
Unifier Installer - A Discord bot to make installing Unifier easier
Copyright (C) 2024  Green

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os, sys
import getpass
import traceback
import json
from pathlib import Path

if os.name == "nt":
    python = 'py -3'
else:
    python = 'python3'

def status(code):
    if code != 0:
        raise RuntimeError("install failed")


try:
    status(os.system(python+' -m pip install --no-dependencies -r requirements.txt'))
except:
    print('ERROR: Could not install required dependencies!')
    print('Please make sure you haven\'t deleted requirements.txt and pip can run properly')
    sys.exit(1)

try:
    import discord
    import asyncio
    from discord.ext import commands
    from dotenv import load_dotenv, set_key, find_dotenv
except:
    print('ERROR: Could not import required dependencies!')
    print('In most cases restarting the bot should fix the issue, as the dependency installation was successful.')
    sys.exit(1)

cgroup = Path('/proc/self/cgroup')
if Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text():
    print('NOTE: It looks like you may be using Pterodactyl panel to install!')
    print('If this is the case, you can enter your ID and token inputs into "Type a command".\n')

print('[Owner user ID]')
print('The bot needs your user ID to know that you\'ll be installing the bot.')
print('In your Discord settings, go to Advanced, then enable Developer Mode.')
print('Right click on your profile picture, then press "Copy User ID".')
print('Your Discord ID should be an 18-19 digit number!')
while True:
    try:
        owner = int(input('Your user ID: ').replace(' ',''))
        break
    except:
        print('Incorrect ID, try again!')

print('\n[Bot token]')
print('The bot needs a token to start up. This is like your bot\'s password.')
print('If you don\'t have a bot already, go to https://discord.com/developers, then create an Application.')
print('Once you\'ve done so, go to "Bot", then press "Reset Token".')
print('This will generate a new token, which you can copy and paste into here to boot the bot.')
print('WARNING: DO NOT SHARE YOUR TOKEN WITH ANYONE, NOT EVEN US!')
token = getpass.getpass(prompt='Token: ')

installing = False
data = {}

bot = commands.Bot(command_prefix='u!',intents=discord.Intents.all())

async def install():
    global installing
    installing = True
    user = bot.get_user(owner)

    def limit(count):
        emojis = [
            ':one:', ':two:', ':three:', ':four:', ':five:'
        ]
        for index in range(count):
            emojis[index] = ':white_check_mark:'

        return ' '.join(emojis)

    embed = discord.Embed(
        title='Welcome to Unifier',
        description=(
            'Welcome to Unifier - an open source, fast, and versatile bridge bot.\n\n'+
            'Press "Next" to begin installation.'
        ),
        color=0xed4545
    )
    embed.set_image(url='https://pixels.onl/images/unifier-banner.png')

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                style=discord.ButtonStyle.blurple,
                label='Next'
            )
        )
    )

    while True:
        try:
            rootmsg = await user.send(embed=embed,components=components)
            break
        except:
            print('ERROR: The bot could not send a DM to you!')
            print('Open the server\'s Privacy Settings, then enable Direct Messages.')
            print('The bot will try again in 30 seconds!')
            await asyncio.sleep(30)

    print('Successfully sent instructions, check your DMs!')

    def check(interaction):
        return interaction.user.id == owner and interaction.message.id == rootmsg.id

    interaction = await bot.wait_for('component_interaction',check=check)

    embed.title = 'Basic configuration'
    embed.description = (
        limit(0)+'\n\nWhat do you want the prefix to be?\nA prefix is the text that comes before the command. So for '+
        'example, the prefix in `!help` would be `!`.'
    )
    embed.remove_image()

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Set prefix',
                style=discord.ButtonStyle.blurple,
                custom_id='summon_prefix'
            )
        )
    )

    await interaction.response.edit_message(embed=embed,components=components)

    interaction = await bot.wait_for('modal_submit',check=check)

    prefix = interaction.components[0].components[0].value.lower()

    data.update({'prefix':prefix})

    embed.description = (
        limit(0) + '\n\nHow often in seconds should Unifier periodically ping Discord API to prevent network idling?'+
        '\nIf this value is 0, Unifier will not periodically ping Discord API.'
    )

    value = 0

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='--',
                custom_id='sub10',
                style=discord.ButtonStyle.red,
                disabled=value <= 0
            ),
            discord.ui.Button(
                label='-',
                custom_id='sub1',
                style=discord.ButtonStyle.red,
                disabled=value <= 0
            ),
            discord.ui.Button(
                label=f'{value}',
                style=discord.ButtonStyle.gray,
                disabled=True
            ),
            discord.ui.Button(
                label='+',
                custom_id='add1',
                style=discord.ButtonStyle.green
            ),
            discord.ui.Button(
                label='++',
                custom_id='add10',
                style=discord.ButtonStyle.green
            )
        ),
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Done',
                custom_id='done',
                style=discord.ButtonStyle.blurple
            )
        )
    )

    await interaction.response.defer()

    await rootmsg.edit(embed=embed, components=components)
    await interaction.delete_original_message()

    while True:
        interaction = await bot.wait_for('component_interaction',check=check)
        if interaction.custom_id=='sub10':
            value -= 10
        elif interaction.custom_id=='sub1':
            value -= 1
        elif interaction.custom_id=='add10':
            value += 10
        elif interaction.custom_id=='add1':
            value += 1
        elif interaction.custom_id=='done':
            break

        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label='--',
                    custom_id='sub10',
                    style=discord.ButtonStyle.red,
                    disabled=value-10<0
                ),
                discord.ui.Button(
                    label='-',
                    custom_id='sub1',
                    style=discord.ButtonStyle.red,
                    disabled=value<=0
                ),
                discord.ui.Button(
                    label=f'{value}',
                    custom_id='value',
                    style=discord.ButtonStyle.gray,
                    disabled=True
                ),
                discord.ui.Button(
                    label='+',
                    custom_id='add1',
                    style=discord.ButtonStyle.green
                ),
                discord.ui.Button(
                    label='++',
                    custom_id='add10',
                    style=discord.ButtonStyle.green
                )
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label='Done',
                    custom_id='done',
                    style=discord.ButtonStyle.blurple
                )
            )
        )
        await interaction.response.edit_message(embed=embed,components=components)

    data.update({'ping':value})

    embed.description = (
        limit(0) + '\n\nHow often in seconds should Unifier backup its message cache?' +
        '\nIf this value is 0, Unifier will not periodically backup.'
    )

    value = 0

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='--',
                custom_id='sub10',
                style=discord.ButtonStyle.red,
                disabled=value <= 0
            ),
            discord.ui.Button(
                label='-',
                custom_id='sub1',
                style=discord.ButtonStyle.red,
                disabled=value <= 0
            ),
            discord.ui.Button(
                label=f'{value}',
                style=discord.ButtonStyle.gray,
                disabled=True
            ),
            discord.ui.Button(
                label='+',
                custom_id='add1',
                style=discord.ButtonStyle.green
            ),
            discord.ui.Button(
                label='++',
                custom_id='add10',
                style=discord.ButtonStyle.green
            )
        ),
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Done',
                custom_id='done',
                style=discord.ButtonStyle.blurple
            )
        )
    )

    await interaction.response.edit_message(embed=embed, components=components)

    while True:
        interaction = await bot.wait_for('component_interaction', check=check)
        if interaction.custom_id == 'sub10':
            value -= 10
        elif interaction.custom_id == 'sub1':
            value -= 1
        elif interaction.custom_id == 'add10':
            value += 10
        elif interaction.custom_id == 'add1':
            value += 1
        elif interaction.custom_id == 'done':
            break

        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label='--',
                    custom_id='sub10',
                    style=discord.ButtonStyle.red,
                    disabled=value - 10 < 0
                ),
                discord.ui.Button(
                    label='-',
                    custom_id='sub1',
                    style=discord.ButtonStyle.red,
                    disabled=value <= 0
                ),
                discord.ui.Button(
                    label=f'{value}',
                    custom_id='value',
                    style=discord.ButtonStyle.gray
                ),
                discord.ui.Button(
                    label='+',
                    custom_id='add1',
                    style=discord.ButtonStyle.green
                ),
                discord.ui.Button(
                    label='++',
                    custom_id='add10',
                    style=discord.ButtonStyle.green
                )
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label='Done',
                    custom_id='done',
                    style=discord.ButtonStyle.blurple
                )
            )
        )
        await interaction.response.edit_message(components=components)

    data.update({'periodic_backup': value})

    embed.description = (
            limit(0) + '\n\nEnable safe filetypes?' +
            '\nThis will restrict filetypes to common and safe ones only.'
    )

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Yes',
                custom_id='yes',
                style=discord.ButtonStyle.green
            ),
            discord.ui.Button(
                label='No',
                custom_id='no',
                style=discord.ButtonStyle.red
            )
        )
    )

    await interaction.response.edit_message(embed=embed,components=components)
    interaction = await bot.wait_for('component_interaction', check=check)
    if interaction.custom_id == 'yes':
        data.update({'safe_filetypes': True})
    else:
        data.update({'safe_filetypes': False})

    embed.description = (
        limit(0) + '\n\nEnable logging, reporting, and moderator pinging?'
    )

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Yes',
                custom_id='yes',
                style=discord.ButtonStyle.green
            ),
            discord.ui.Button(
                label='No',
                custom_id='no',
                style=discord.ButtonStyle.red
            )
        )
    )

    await interaction.response.edit_message(embed=embed,components=components)
    interaction = await bot.wait_for('component_interaction', check=check)
    if interaction.custom_id == 'yes':
        data.update({'enable_logging': True})
    else:
        data.update({'enable_logging': False})

    if interaction.custom_id == 'yes':
        embed.description = (
            limit(0) + '\n\nSelect your home server' +
            '\nThis will be treated as your bot\'s headquarters, where logs and reports will be logged.'
        )
        
        first = False

        while True:
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.SelectMenu(
                        min_values=1,
                        max_values=1,
                        options=[
                            discord.ui.SelectOption(
                               label=guild.name,
                               value=str(guild.id)
                            ) for guild in bot.guilds
                        ]
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        style=discord.ButtonStyle.gray,
                        label='Refresh'
                    )
                )
            )

            if (len(interaction.values) > 0 if interaction.values else False) and first:
                break

            first = True

            await interaction.response.edit_message(embed=embed, components=components)

            interaction = await bot.wait_for('component_interaction', check=check)

        data.update({'home_guild': int(interaction.values[0])})

        embed.description = (
                limit(0) + '\n\nSelect your logging channel' +
                '\nMessage logs will be logged here.'
        )

        first = False

        while True:
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.SelectMenu(
                        min_values=1,
                        max_values=1,
                        options=[
                            discord.ui.SelectOption(
                                label='#'+channel.name,
                                value=str(channel.id)
                            ) for channel in bot.get_guild(data['home_guild']).text_channels
                        ]
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        style=discord.ButtonStyle.gray,
                        label='Refresh'
                    )
                )
            )

            if (len(interaction.values) > 0 if interaction.values else False) and first:
                break

            first = True

            await interaction.response.edit_message(embed=embed, components=components)

            interaction = await bot.wait_for('component_interaction', check=check)

        data.update({'logs_channel': int(interaction.values[0])})

        embed.description = (
            limit(0) + '\n\nSelect your reports channel' +
            '\nReports will be logged here.'
        )

        first = False

        while True:
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.SelectMenu(
                        min_values=1,
                        max_values=1,
                        options=[
                            discord.ui.SelectOption(
                                label='#' + channel.name,
                                value=str(channel.id)
                            ) for channel in bot.get_guild(data['home_guild']).text_channels
                        ]
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        style=discord.ButtonStyle.gray,
                        label='Refresh'
                    )
                )
            )

            if (len(interaction.values) > 0 if interaction.values else False) and first:
                break

            first = True

            await interaction.response.edit_message(embed=embed, components=components)

            interaction = await bot.wait_for('component_interaction', check=check)

        data.update({'reports_channel': int(interaction.values[0])})

        embed.description = (
                limit(0) + '\n\nSelect your moderator role' +
                '\nThis will allow moderators to be pinged in an emergency.'
        )

        first = False

        while True:
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.SelectMenu(
                        min_values=1,
                        max_values=1,
                        options=[
                            discord.ui.SelectOption(
                                label=role.name,
                                value=str(role.id)
                            ) for role in bot.get_guild(data['home_guild']).roles
                        ]
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        style=discord.ButtonStyle.gray,
                        label='Refresh'
                    )
                )
            )

            if (len(interaction.values) > 0 if interaction.values else False) and first:
                break

            first = True

            await interaction.response.edit_message(embed=embed, components=components)

            interaction = await bot.wait_for('component_interaction', check=check)

        data.update({'moderator_role': int(interaction.values[0])})

    embed.description = (
            limit(0) + '\n\nEnable context menu commands?' +
            '\nThis will allow users to delete, report, and modping through a context menu.'
    )

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Yes',
                custom_id='yes',
                style=discord.ButtonStyle.green
            ),
            discord.ui.Button(
                label='No',
                custom_id='no',
                style=discord.ButtonStyle.red
            )
        )
    )

    await interaction.response.edit_message(embed=embed,components=components)
    interaction = await bot.wait_for('component_interaction', check=check)
    if interaction.custom_id == 'yes':
        data.update({'enable_ctx_commands': True})
    else:
        data.update({'enable_ctx_commands': False})

    embed.description = (
        limit(0) + '\n\nWhat would your main room be called?' +
        '\nThis room will receive automated system messages.'
    )

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Set main room',
                style=discord.ButtonStyle.blurple,
                custom_id='summon_mainroom'
            )
        )
    )

    await interaction.response.edit_message(embed=embed, components=components)

    interaction = await bot.wait_for('modal_submit', check=check)

    prefix = interaction.components[0].components[0].value.lower()

    data.update({'main_room': prefix})

    embed.description = (
        limit(0) + '\n\nEnable posts?' +
        '\nPosts allow users to share and react to their creations in a more organized manner.'
    )

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Yes',
                custom_id='yes',
                style=discord.ButtonStyle.green
            ),
            discord.ui.Button(
                label='No',
                custom_id='no',
                style=discord.ButtonStyle.red
            )
        )
    )

    await interaction.response.defer()

    await rootmsg.edit(embed=embed, components=components)
    await interaction.delete_original_message()

    interaction = await bot.wait_for('component_interaction', check=check)
    if interaction.custom_id == 'yes':
        data.update({'allow_posts': True})
        embed.description = (
            limit(0) + '\n\nWhat would your posts room be called?' +
            '\nUsers will be able to share posts in this room.'
        )

        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label='Set posts room',
                    style=discord.ButtonStyle.blurple,
                    custom_id='summon_postroom'
                )
            )
        )

        await interaction.response.edit_message(embed=embed, components=components)

        interaction = await bot.wait_for('modal_submit', check=check)
        prefix = interaction.components[0].components[0].value.lower()

        data.update({'posts_room': prefix})

        embed.description = (
                limit(0) + '\n\nWhat would your posts reference room be called?' +
                '\nUsers can comment on others\' posts in this room.'
        )

        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label='Set posts reference room',
                    style=discord.ButtonStyle.blurple,
                    custom_id='summon_postref'
                )
            )
        )

        await interaction.response.defer()

        await rootmsg.edit(embed=embed, components=components)
        await interaction.delete_original_message()

        interaction = await bot.wait_for('modal_submit', check=check)

        prefix = interaction.components[0].components[0].value.lower()

        data.update({'posts_ref_room': prefix})
    else:
        data.update({'allow_posts': False})

    embed.title = 'Select version'
    embed.description = limit(1) + '\n\nWhich version of Unifier would you like to install?'
    embed.add_field(
        name='Unifier',
        value='The full-scale version of Unifier.',
        inline=False
    )

    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label='Unifier',
                style=discord.ButtonStyle.blurple,
                custom_id='unifier-full-main'
            ),
            discord.ui.Button(
                label='Unifier Nightly',
                style=discord.ButtonStyle.gray,
                custom_id='unifier-full-dev'
            )
        )
    )

    await interaction.response.defer()

    await rootmsg.edit(embed=embed, components=components)
    await interaction.delete_original_message()

    interaction = await bot.wait_for('component_interaction', check=check)

    version = interaction.custom_id
    embed.clear_fields()
    if version.startswith('unifier-full'):
        branch = version.replace('unifier-full-','',1)
        embed.title = 'Finding Unifier...'
        embed.description = limit(2) + '\n\nChecking newest version from remote'
        os.system('rm -rf ' + os.getcwd() + '/install_check')
        await interaction.response.edit_message(embed=embed,components=None)
        await bot.loop.run_in_executor(
            None, lambda: os.system(
                'git clone --branch '+branch+' https://github.com/UnifierHQ/unifier-version "' + os.getcwd() + '/install_check"'
            )
        )
        try:
            with open('install_check/update.json', 'r') as file:
                new = json.load(file)
        except:
            embed.title = 'Install failed'
            embed.description = 'Could not find Unifier. Please review the error logs, then restart the installer.'
            embed.colour = 0xff0000
            await rootmsg.edit(embed=embed)
            sys.exit(1)

        embed.title = 'Installing Unifier...'
        embed.description = limit(3) + '\n\nDownloading Unifier from remote...'
        await rootmsg.edit(embed=embed)
        os.system('rm -rf ' + os.getcwd() + '/install')
        await bot.loop.run_in_executor(
            None, lambda: os.system(
                'git clone --branch '+new['version']+' https://github.com/UnifierHQ/unifier "' + os.getcwd() + '/install"'
            )
        )
        try:
            x = open(os.getcwd() + '/install/plugins/system.json', 'r')
            x.close()
        except:
            embed.title = 'Install failed'
            embed.description = 'Could not download Unifier. Please review the error logs, then restart the installer.'
            embed.colour = 0xff0000
            await rootmsg.edit(embed=embed)
            sys.exit(1)
        embed.title = 'Installing Unifier...'
        embed.description = limit(3) + '\n\nDownloading and installing dependencies...\nThis step can take a while.'
        await rootmsg.edit(embed=embed)
        x = open('install/requirements.txt')
        newdeps = x.read().split('\n')
        x.close()
        try:
            await bot.loop.run_in_executor(None, lambda: status(os.system(python+' -m pip install --no-dependencies ' + ' '.join(newdeps))))
        except:
            embed.title = 'Install failed'
            embed.description = 'Could not install dependencies. Please review the error logs, then restart the installer.'
            embed.colour = 0xff0000
            await rootmsg.edit(embed=embed)
            sys.exit(1)
        try:
            embed.title = 'Installing Unifier...'
            embed.description = limit(4) + '\n\nMoving Unifier files into place...'
            await rootmsg.edit(embed=embed)
            try:
                os.mkdir('plugins')
                os.mkdir('cogs')
                os.mkdir('utils')
                os.mkdir('emojis')
            except:
                pass
            status(os.system('cp "' + os.getcwd() + '/install/unifier.py" "' + os.getcwd() + '/unifier.py"'))
            status(os.system('cp "' + os.getcwd() + '/install/config.json" "' + os.getcwd() + '/config.json"'))
            status(os.system('cp "' + os.getcwd() + '/install/requirements.txt" "' + os.getcwd() + '/requirements.txt"'))
            status(os.system('cp "' + os.getcwd() + '/install/plugins/system.json" "' + os.getcwd() + '/plugins/system.json"'))
            status(os.system('cp "' + os.getcwd() + '/install/emojis/base.json" "' + os.getcwd() + '/emojis/base.json"'))
            for file in os.listdir(os.getcwd() + '/install/cogs'):
                status(os.system('cp "' + os.getcwd() + '/install/cogs/'+file + '" "' + os.getcwd() + '/cogs/'+file+'"'))
            for file in os.listdir(os.getcwd() + '/install/utils'):
                status(os.system('cp "' + os.getcwd() + '/install/utils/'+file + '" "' + os.getcwd() + '/utils/'+file+'"'))
            with open('config.json', 'r') as file:
                cfg = json.load(file)
            cfg.update(data)
            with open('config.json', 'w') as file:
                json.dump(cfg, file, indent=4)
            x = open('.env','w+')
            x.close()
            dotenv_file = find_dotenv()
            set_key(dotenv_file, "TOKEN", token)
            if new['release'] >= 46:
                # v2.0.0 and newer use nextcord, so novus is no longer needed
                status(os.system(python + ' -m pip uninstall -y novus'))
        except:
            embed.title = 'Install failed'
            embed.description = 'Could not install Unifier. Please review the error logs, then restart the installer.'
            embed.colour = 0xff0000
            await rootmsg.edit(embed=embed)
            sys.exit(1)
    embed.title = 'Install complete'
    embed.colour = 0x00ff00
    embed.description = (
        limit(5) + '\n\nCongratulations, Unifier was successfully installed!\n\n'+
        'To run Unifier, follow this guide: https://unifier-wiki.pixels.onl/setup-selfhosted/getting-started/unifier#running-unifier'
    )
    await rootmsg.edit(embed=embed)
    sys.exit(0)

@bot.event
async def on_component_interaction(interaction):
    if not interaction.custom_id.startswith('summon_'):
        return
    modal_id = interaction.custom_id.replace('summon_','',1)
    if modal_id=='prefix':
        modal = discord.ui.Modal(
            title='Set prefix',
            components=[
                discord.ui.ActionRow(
                    discord.ui.InputText(
                        style=discord.TextStyle.short,
                        label='Bot prefix',
                        placeholder='Prefix...',
                        value='u!',
                        max_length=5,
                        required=True
                    )
                )
            ]
        )
    elif modal_id=='mainroom':
        modal = discord.ui.Modal(
            title='Set main room',
            components=[
                discord.ui.ActionRow(
                    discord.ui.InputText(
                        style=discord.TextStyle.short,
                        label='Room name',
                        placeholder='Name...',
                        value='main',
                        max_length=20,
                        required=True
                    )
                )
            ]
        )
    elif modal_id=='postroom':
        modal = discord.ui.Modal(
            title='Set posts room',
            components=[
                discord.ui.ActionRow(
                    discord.ui.InputText(
                        style=discord.TextStyle.short,
                        label='Room name',
                        placeholder='Name...',
                        value='posts',
                        max_length=20,
                        required=True
                    )
                )
            ]
        )
    elif modal_id=='postref':
        modal = discord.ui.Modal(
            title='Set posts reference room',
            components=[
                discord.ui.ActionRow(
                    discord.ui.InputText(
                        style=discord.TextStyle.short,
                        label='Room name',
                        placeholder='Name...',
                        value='post-comments',
                        max_length=20,
                        required=True
                    )
                )
            ]
        )
    else:
        return

    await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f'Booted as {bot.user.name}!')
    user = bot.get_user(owner)
    if not user:
        print('ERROR: The bot doesn\'t share a server with you!')
        print('You must first add your bot to a server you\'re in, so the bot can DM you.')
        print('Please add the bot to your server using the following URL:')
        print(f'https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&scope=bot')
    else:
        if not installing:
            await install()

@bot.event
async def on_guild_join(guild):
    # user should not be None, but adding this just in case
    user = guild.get_member(owner)
    if user and not installing:
        await install()

try:
    bot.run(token)
except SystemExit:
    pass
except:
    traceback.print_exc()
    print('ERROR: Bot could not boot!')
    print('You must restart the installer script. Please make sure your token is correct!')
    sys.exit(1)
