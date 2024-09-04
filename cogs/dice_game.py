import random
import json
import os
import nextcord
from nextcord.ext import commands
from datetime import datetime

class DiceGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

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

    def format_currency(self, amount):
        """Định dạng số tiền để hiển thị."""
        return "{:,}".format(amount)

    def get_dice_emoji(self, number):
        """Trả về emoji đại diện cho số mặt xúc xắc."""
        dice_emojis = {
            1: "⚀",
            2: "⚁",
            3: "⚂",
            4: "⚃",
            5: "⚄",
            6: "⚅"
        }
        return dice_emojis.get(number, "🎲")

    @commands.command(name="tx")
    async def taixiu(self, ctx, choice: str, bet: str):
        """Lệnh chơi game tài xỉu."""
        user_id = str(ctx.author.id)
        choice = choice.lower()

        if choice not in ["tài", "xỉu"]:
            await ctx.send(f"{ctx.author.mention} ❌ Bạn phải chọn 'tài' hoặc 'xỉu'.")
            return

        users = self.get_users()

        # Khởi tạo dữ liệu người dùng nếu chưa có
        if user_id not in users:
            users[user_id] = {"balance": 0}

        # Kiểm tra cooldown
        if user_id in self.cooldowns:
            remaining_time = self.cooldowns[user_id] - ctx.message.created_at.timestamp()
            if remaining_time > 0:
                await ctx.send(f"{ctx.author.mention} ⏳ Bạn phải đợi {int(remaining_time)} giây nữa mới có thể chơi tiếp.")
                return

        if bet.lower() == "all":
            bet_amount = users.get(user_id, {}).get("balance", 0)
            if bet_amount > 1_000_000_000:
                bet_amount = 1_000_000_000  
        else:
            try:
                bet_amount = int(bet)
                if bet_amount <= 0 or bet_amount > 1_000_000_000:
                    await ctx.send(f"{ctx.author.mention} ⚠️ Số tiền cược phải là một số dương lớn hơn 0 và không vượt quá 1B!")
                    return
            except ValueError:
                await ctx.send(f"{ctx.author.mention} ❌ Vui lòng nhập số tiền hợp lệ hoặc 'all' để cược tất cả.")
                return

        if user_id not in users or users[user_id]["balance"] < bet_amount:
            await ctx.send(f"{ctx.author.mention} 💸 Bạn không có đủ tiền để đặt cược.")
            return

        # Trừ tiền cược ngay khi đặt cược
        users[user_id]["balance"] -= bet_amount

        # Xúc xắc
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice3 = random.randint(1, 6)
        total = dice1 + dice2 + dice3

        # Xác định kết quả
        if total in [3, 18]:
            result = "nổ hũ"
        elif 3 <= total <= 10:
            result = "xỉu"
        else:
            result = "tài"

        # Xác định chiến thắng
        win = choice == result or result == "nổ hũ"

        # Cập nhật số dư ngay lập tức
        if win:
            if result == "nổ hũ":
                prize = int(bet_amount * 5)
                users[user_id]["balance"] += prize
                message = f"{ctx.author.mention} 🎉 Nổ hũ! Bạn nhận được {self.format_currency(prize)} VND."
            else:
                prize = int(bet_amount * 2)
                users[user_id]["balance"] += prize
                message = f"{ctx.author.mention} 🥳 Bạn đã thắng! Bạn nhận được {self.format_currency(prize)} VND."
        else:
            message = f"{ctx.author.mention} 😢 Bạn đã thua! Bạn mất {self.format_currency(bet_amount)} VND."

        # Cập nhật thông tin người dùng
        self.save_users(users)

        # Hiển thị xúc xắc với emoji
        dice_emojis = f"{self.get_dice_emoji(dice1)} {self.get_dice_emoji(dice2)} {self.get_dice_emoji(dice3)}"

        # Tạo Embed để hiển thị kết quả
        embed = nextcord.Embed(
            title="🎲 Kết Quả Xúc Xắc 🎲",
            description=f"Xúc xắc: {dice_emojis} ({total} - {result.upper()})",
            color=0x00ff00  # Màu xanh lục
        )

        embed.add_field(name="Lựa chọn của bạn", value=choice.upper(), inline=True)
        embed.add_field(name="Kết quả", value=result.upper(), inline=True)
        embed.add_field(name="Thông báo", value=message, inline=False)
        embed.add_field(name="💰 Số dư hiện tại", value=f"{self.format_currency(users[user_id]['balance'])} VND", inline=False)

        # Gửi Embed kết quả
        await ctx.send(embed=embed)

        # Cập nhật cooldown
        self.cooldowns[user_id] = ctx.message.created_at.timestamp() + 5

def setup(bot):
    bot.add_cog(DiceGame(bot))
