from inspect import getdoc

from discord.ext.commands import Bot, CommandNotFound, MissingRequiredArgument


class SudoBot(Bot):
    """
    sudoコマンドを使用すると5分間だけsudo用ロールを付与してくれるbotです。
    sudo用ロールは元のロールの名前の前に、"su:"を付けたロールをsudo用ロールとみなします。
    また、createコマンドを使う事で、ロールを作成する事ができます。
    """

    def __init__(self, *args, **kwargs):
        description = getdoc(self)
        super().__init__(*args, description=description, **kwargs)

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return

        elif isinstance(error, MissingRequiredArgument):
            await ctx.reply("引数が足りません。")

        else:
            await super().on_command_error(ctx, error)

    async def on_ready(self):
        print("ready")
