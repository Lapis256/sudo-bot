import re
from asyncio import sleep
from itertools import product
from textwrap import dedent

from discord import Role, Forbidden
from discord.ext.commands import (
    Cog,
    command,
    has_guild_permissions,
    bot_has_guild_permissions,
    BadArgument,
    MissingPermissions,
    BotMissingPermissions
)

from manager import SudoManager


class SudoCog(Cog, name="Main"):
    def __init__(self, bot):
        self.loop = bot.loop
        self.manager = SudoManager()
        self.sudo_regex = re.compile("su:\s*(.+)")

    def find_sudo_role(self, guild_roles, member_roles):
        for mrole, grole in product(reversed(member_roles), guild_roles):
            if mrole.name in self.sudo_regex.findall(grole.name):
                return grole
        return None

    async def timeout_sudo(self, ctx):
        await sleep(5*60)
        member = self.manager.pop(ctx)
        await ctx.author.remove_roles(member.role)
        await ctx.reply(f"5分経ったったので {member.role.mention} を削除しました。")

    @bot_has_guild_permissions(manage_roles=True)
    @command(ignore_extra=True)
    async def sudo(self, ctx):
        """sudo用ロールを付け外しします。
        付与されるロールは元のロールの順位に依存します。
        5分経つと自動的にロールが外されます。"""

        if (member := self.manager.get(ctx)) is not None:
            self.manager.cancel(ctx)
            await ctx.author.remove_roles(member.role)
            await ctx.reply(f"{member.role.mention} を削除しました。")
            return

        role = self.find_sudo_role(ctx.guild.roles, ctx.author.roles)
        if role is None:
            await ctx.reply("sudo用ロールを持っていません。")
            return

        await ctx.author.add_roles(role)
        task = self.loop.create_task(self.timeout_sudo(ctx))
        self.manager.add(ctx, role, task)
        await ctx.reply(f"{role.mention} を一時的に追加しました。")

    @sudo.error
    async def sudo_error(self, ctx, error):
        if isinstance(error, BotMissingPermissions):
            await ctx.reply(
                "権限が不足しています。\n"
                "ロールの管理権限が必要です。\n"
                "または、sudo用ロールがbotのロールより上にあるのかもしれません。"
            )

        else:
            raise error

    @has_guild_permissions(manage_roles=True)
    @bot_has_guild_permissions(manage_roles=True)
    @command(ignore_extra=True)
    async def create(self, ctx, role: Role):
        """指定したロールのsudo用ロールを作るだけのコマンドです。
        権限は手動で設定する必要があります。"""

        created_role = await ctx.guild.create_role(name="su:" + role.name)
        await ctx.reply(created_role.mention + "を作成しました。\n権限を設定してください。")

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error, BadArgument):
            await ctx.reply("role引数が間違っています。\n関連付けるロールを指定してください。")

        elif isinstance(error, MissingPermissions):
            await ctx.reply("コマンドの実行に必要な権限を持っていません。\nロールの管理権限が必要です。")

        elif isinstance(error, BotMissingPermissions):
            await ctx.reply("権限が不足しています。\nロールの管理権限が必要です。")

        else:
            raise error
