from asyncio import Task
from dataclasses import dataclass

import discord.utils as utils
from discord import Role


@dataclass
class SudoMember:
    guild_id: int
    member_id: int
    role: Role
    task: Task


class SudoManager:
    def __init__(self):
        self.members = []

    def get(self, ctx):
        member = utils.get(self.members, guild_id=ctx.guild.id, member_id=ctx.author.id)
        return member

    def add(self, ctx, role, task):
        if self.get(ctx) is not None:
            return

        member = SudoMember(guild_id=ctx.guild.id, member_id=ctx.author.id, role=role, task=task)
        self.members.append(member)
        return member

    def pop(self, ctx):
        member = self.get(ctx)
        if member is None:
            return

        self.members.remove(member)
        return member

    def cancel(self, ctx):
        member = self.pop(ctx)
        member.task.cancel()
