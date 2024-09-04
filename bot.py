import nextcord
from nextcord.ext import commands
import json

# Intents
intents = nextcord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)

# Load extension
initial_extensions = [
    "cogs.economy", 
    "cogs.dice_game", 
    "cogs.blackjack", 
    "cogs.HorseRacing", 
    "cogs.StockInvestment", 
    "cogs.Shop", 
    "cogs.GachaInventory",
    "cogs.lottery",
    "cogs.AdminCommands"
]
for extension in initial_extensions:
    bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')

    # Cập nhật trạng thái cho bot
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name="Luv <3"))

@bot.command(name='info')
async def info(ctx):
   
    bot_info = {
        'name': 'Kuriyama',
        'version': '1.8.0',
        'developer': 'Puppy_z4nx',
        'description': 'Bot game làm lúc rảnh rỗi của một thằng loser.',
        'support_url': 'https://www.puppyz4nx.site/'  # URL hỗ trợ
    }

    # Gửi một tin nhắn văn bản trước
    await ctx.send("Dưới đây là thông tin chi tiết về bot:")

    # Tạo và gửi Embed
    embed = nextcord.Embed(
        title="📜 Thông tin Bot 📜",
        description="Dưới đây là thông tin chi tiết về bot.",
        color=nextcord.Color.from_rgb(0, 128, 255)  # Màu xanh dương tùy chỉnh
    )
    
    embed.set_author(name=bot_info['name'], icon_url='https://i.pinimg.com/564x/9f/12/ba/9f12ba4d1fe9cf5bfec81098ba7f04b2.jpg')  # Thay đổi icon URL nếu cần
    embed.set_thumbnail(url='https://i.pinimg.com/564x/f2/36/71/f2367152be44f0cb657eb0c672c7c732.jpg')  # Thay đổi URL của ảnh thumbnail nếu cần
    embed.set_footer(text=f"Phiên bản {bot_info['version']} | Được phát triển bởi {bot_info['developer']}")
    
    embed.add_field(name="🤖 Tên Bot", value=bot_info['name'], inline=False)
    embed.add_field(name="🔢 Phiên Bản", value=bot_info['version'], inline=False)
    embed.add_field(name="👨‍💻 Nhà Phát Triển", value=bot_info['developer'], inline=False)
    embed.add_field(name="📄 Mô Tả", value=bot_info['description'], inline=False)
    embed.add_field(name="🔗 Hỗ Trợ", value=f"Để được hỗ trợ, vui lòng truy cập [Web Own Bot]({bot_info['support_url']}).", inline=False)
    
    # Thêm ảnh lớn ở dưới cùng
    embed.set_image(url='https://i.pinimg.com/564x/ab/8d/87/ab8d87ced04f4cca63d0c743aece955c.jpg')  # Thay đổi URL của ảnh lớn nếu cần
    
    await ctx.send(embed=embed)

bot.run("TOken here")
