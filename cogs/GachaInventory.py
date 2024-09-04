import json
import random
import os
import asyncio
import nextcord
from nextcord.ext import commands

class GachaInventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self.gacha_cooldown = {}

    def get_users(self):
        """Lấy dữ liệu người dùng từ file JSON."""
        if not os.path.exists("users.json"):
            return {}
        with open("users.json", "r") as f:
            return json.load(f)

    def save_users(self, users):
        """Lưu dữ liệu người dùng vào file JSON."""
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)

    def get_characters(self):
        """Lấy danh sách nhân vật từ file JSON."""
        with open("characters.json", "r") as f:
            return json.load(f)

    @commands.command(name="roll")
    async def roll(self, ctx):
        """Thực hiện roll."""
        user_id = str(ctx.author.id)
        users = self.get_users()
        characters = self.get_characters()

        # Kiểm tra cooldown
        if user_id in self.gacha_cooldown:
            remaining_time = self.gacha_cooldown[user_id] - ctx.message.created_at.timestamp()
            if remaining_time > 0:
                await ctx.send(f"{ctx.author.mention} ⏳ Bạn phải đợi {int(remaining_time)} giây nữa mới có thể roll tiếp.")
                return

        if user_id not in users:
            users[user_id] = {"balance": 0, "characters": []}
        if "characters" not in users[user_id]:
            users[user_id]["characters"] = []

        if len(users[user_id]["characters"]) >= 100:
            await ctx.send(f"{ctx.author.mention} ❌ Túi đồ của bạn đã đầy. Vui lòng xóa bớt nhân vật.")
            return

        cost = 10000000  # 10 triệu VND cho mỗi lần roll
        if users[user_id]["balance"] < cost:
            await ctx.send(f"{ctx.author.mention} 💸 Bạn không có đủ tiền để roll.")
            return

        # Trừ tiền
        users[user_id]["balance"] -= cost

        # Roll nhân vật
        total_rate = sum(char["drop_rate"] for char in characters)
        pick = random.uniform(0, total_rate)
        current = 0
        for char in characters:
            current += char["drop_rate"]
            if current >= pick:
                new_character = char
                break

        # Thêm nhân vật vào túi đồ
        users[user_id]["characters"].append(new_character)

        # Lưu dữ liệu
        self.save_users(users)

        # Tạo Embed hiển thị nhân vật roll
        embed = nextcord.Embed(
            title="🎉 Roll Thành Công!",
            description=f"Bạn đã nhận được **{new_character['name']}**!",
            color=0x00ff00
        )
        embed.add_field(name="Độ hiếm", value=new_character["rarity"], inline=True)
        embed.add_field(name="Giá trị", value=f"{new_character['value']:,} VND", inline=True)
        embed.set_image(url=new_character["image_url"])

        await ctx.send(embed=embed)

        # Cập nhật cooldown
        self.gacha_cooldown[user_id] = ctx.message.created_at.timestamp() + 7  # 7 giây cooldown

    @commands.command(name="inv")
    async def inventory(self, ctx):
        """Hiển thị túi đồ của người chơi."""
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users or not users[user_id]["characters"]:
            await ctx.send(f"{ctx.author.mention} ❌ Túi đồ của bạn đang trống.")
            return

        characters = users[user_id]["characters"]
        per_page = 7
        total_pages = (len(characters) + per_page - 1) // per_page

        current_page = 0

        def create_embed(page):
            embed = nextcord.Embed(
                title=f"🎒 Túi Đồ Của Bạn - Trang {page + 1}/{total_pages}",
                color=0x00ff00
            )
            start = page * per_page
            end = start + per_page
            for i, char in enumerate(characters[start:end], start=start + 1):
                embed.add_field(
                    name=f"{i}. {char['name']} ({char['rarity']})",
                    value=f"Giá trị: {char['value']:,} VND",
                    inline=False
                )
            return embed

        message = await ctx.send(embed=create_embed(current_page))

        if total_pages > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                    if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                        current_page += 1
                        await message.edit(embed=create_embed(current_page))
                    elif str(reaction.emoji) == "⬅️" and current_page > 0:
                        current_page -= 1
                        await message.edit(embed=create_embed(current_page))

                    await message.remove_reaction(reaction.emoji, user)

                except asyncio.TimeoutError:
                    break

            await message.clear_reactions()

    @commands.command(name="schar")
    async def sell_character(self, ctx, stt: int = None):
        """Bán nhân vật hoặc tất cả nhân vật khỏi túi đồ."""
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users or not users[user_id]["characters"]:
            await ctx.send(f"{ctx.author.mention} ❌ Túi đồ của bạn đang trống.")
            return

        if stt is None:
            total_value = sum(char["value"] for char in users[user_id]["characters"])
            users[user_id]["balance"] += total_value
            users[user_id]["characters"] = []
            self.save_users(users)
            await ctx.send(f"{ctx.author.mention} ✅ Đã bán tất cả nhân vật trong túi đồ, bạn nhận được {total_value:,} VND.")
        else:
            if stt < 1 or stt > len(users[user_id]["characters"]):
                await ctx.send(f"{ctx.author.mention} ❌ STT không hợp lệ.")
                return

            sold_char = users[user_id]["characters"].pop(stt - 1)
            users[user_id]["balance"] += sold_char["value"]
            self.save_users(users)
            await ctx.send(f"{ctx.author.mention} ✅ Đã bán **{sold_char['name']}** với giá {sold_char['value']:,} VND.")

def setup(bot):
    bot.add_cog(GachaInventory(bot))
