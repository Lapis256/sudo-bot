from os import environ

from discord import Intents, AllowedMentions, MemberCacheFlags
from dotenv import load_dotenv
from uvloop import install

from cog import SudoCog
from bot import SudoBot


def run():
    install()
    load_dotenv()

    bot = SudoBot(
        max_messages=None,
        chunk_guilds_at_startup=False,
        member_cache_flags=MemberCacheFlags.none(),
        allowed_mentions=AllowedMentions.none(),
        intents=Intents(guild_messages=True, guilds=True),
        command_prefix=environ["COMMAND_PREFIX"],
        case_insensitive=True
    )
    bot.add_cog(SudoCog(bot))
    bot.run(environ["TOKEN"])

run()
