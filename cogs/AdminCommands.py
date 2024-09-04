import nextcord
from nextcord.ext import commands
import datetime
import psutil
import asyncio
import json

# Thay đổi ID này thành ID người dùng được phép sử dụng các lệnh
AUTHORIZED_USER_IDS = [789428736868876298]  # Thay đổi ID tại đây

def is_authorized():
    def predicate(ctx):
        if ctx.author.id not in AUTHORIZED_USER_IDS:
            raise commands.CheckFailure("Bạn không phải là chủ sở hữu của tôi!")
        return True
    return commands.check(predicate)

# Đọc/ghi trạng thái kênh từ file JSON
def read_channel_states():
    try:
        with open('channel_states.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def write_channel_states(channel_states):
    with open('channel_states.json', 'w') as f:
        json.dump(channel_states, f)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.launch_time = datetime.datetime.utcnow()
        self.channel_states = read_channel_states()

    @commands.command(name="kick")
    @is_authorized()
    async def kick(self, ctx, member: nextcord.Member, *, reason=None):
        """Kick một thành viên khỏi server."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} đã bị kick. Lý do: {reason}")

    @commands.command(name="ban")
    @is_authorized()
    async def ban(self, ctx, member: nextcord.Member, *, reason=None):
        """Ban một thành viên khỏi server."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} đã bị ban. Lý do: {reason}")

    @commands.command(name="say")
    @is_authorized()
    async def say(self, ctx, *, message):
        """Bot sẽ lặp lại tin nhắn mà bạn nhập."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        await ctx.send(message)

    @commands.command(name="status")
    @is_authorized()
    async def status(self, ctx):
        """Hiển thị thông tin trạng thái của bot."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        uptime = datetime.datetime.utcnow() - self.bot.launch_time
        memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        embed = nextcord.Embed(title="Trạng thái Bot", color=0x00ff00)
        embed.add_field(name="Thời gian hoạt động", value=f"{uptime.days} ngày {uptime.seconds // 3600} giờ {uptime.seconds % 3600 // 60} phút", inline=False)
        embed.add_field(name="Sử dụng bộ nhớ", value=f"{memory_usage:.2f} MB", inline=False)
        embed.add_field(name="Số lượng thành viên", value=str(len(self.bot.users)), inline=False)
        embed.add_field(name="Số lượng máy chủ", value=str(len(self.bot.guilds)), inline=False)
        embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url="https://i.pinimg.com/originals/e8/43/64/e84364a25ec400b61557227bddf61afc.gif")  # Thay URL_ẢNH_THUMBNAIL bằng URL ảnh thumbnail của bạn

        await ctx.send(embed=embed)

    @commands.command(name="ping")
    @is_authorized()
    async def ping(self, ctx):
        """Kiểm tra độ trễ của bot."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        latency = round(self.bot.latency * 1000)  # Latency in milliseconds
        embed = nextcord.Embed(title="Ping", color=0x00ff00)
        embed.add_field(name="Độ trễ", value=f"{latency} ms", inline=False)
        embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_image(url="https://i.pinimg.com/originals/e8/43/64/e84364a25ec400b61557227bddf61afc.gif")  # Thay URL_ẢNH bằng URL ảnh mà bạn muốn hiển thị

        await ctx.send(embed=embed)

    @commands.command(name="mute")
    @is_authorized()
    async def mute(self, ctx, member: nextcord.Member, duration: int, *, reason=None):
        """Mute một thành viên trong một khoảng thời gian nhất định."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)
        
        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"{member.mention} đã bị mute trong {duration} phút. Lý do: {reason}")

        await asyncio.sleep(duration * 60)
        await member.remove_roles(mute_role, reason="Mute hết hạn")
        await ctx.send(f"{member.mention} đã được unmute.")

    @commands.command(name="unmute")
    @is_authorized()
    async def unmute(self, ctx, member: nextcord.Member):
        """Unmute một thành viên."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"{member.mention} đã được unmute.")
        else:
            await ctx.send(f"{member.mention} không có quyền mute.")

    @commands.command(name="clear")
    @is_authorized()
    async def clear(self, ctx, amount: int):
        """Xóa một số lượng tin nhắn nhất định."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        if amount < 1 or amount > 100:
            await ctx.send("Số lượng tin nhắn cần xóa phải từ 1 đến 100.")
            return

        await ctx.channel.purge(limit=amount)
        await ctx.send(f"Đã xóa {amount} tin nhắn.", delete_after=5)

    @commands.command(name="ruttien")
    @is_authorized()
    async def ruttien(self, ctx, stk: str, bank_name: str):
        """Rút tiền từ tài khoản ngân hàng."""
        if str(ctx.channel.id) in self.channel_states and not self.channel_states[str(ctx.channel.id)]:
            await ctx.send("Lệnh này đã bị vô hiệu hóa trong kênh này.")
            return
        await ctx.send(f"Đang xử lý yêu cầu rút tiền từ tài khoản {stk} tại ngân hàng {bank_name}.")
        await asyncio.sleep(3)  # Delay 3 giây
        await ctx.send(f"Rút tiền từ tài khoản {stk} tại ngân hàng {bank_name} thành công!")

    @commands.command(name="disable")
    @is_authorized()
    async def disable(self, ctx):
        """Vô hiệu hóa tất cả các lệnh của bot trong kênh hiện tại."""
        self.channel_states[str(ctx.channel.id)] = False
        write_channel_states(self.channel_states)
        await ctx.send("Các lệnh của bot đã bị vô hiệu hóa trong kênh này.")

    @commands.command(name="enable")
    @is_authorized()
    async def enable(self, ctx):
        """Kích hoạt tất cả các lệnh của bot trong kênh hiện tại."""
        self.channel_states[str(ctx.channel.id)] = True
        write_channel_states(self.channel_states)
        await ctx.send("Các lệnh của bot đã được kích hoạt trong kênh này.")

def setup(bot):
    bot.add_cog(AdminCommands(bot))
