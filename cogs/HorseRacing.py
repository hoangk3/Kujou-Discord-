import json
import os
import random
import nextcord
from nextcord.ext import commands

class HorseRacing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="race")
    async def horse_racing(self, ctx, bet: str):
        """Lệnh chơi game đua ngựa."""
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users:
            await ctx.send(f"{ctx.author.mention} Bạn chưa đăng ký. Sử dụng lệnh !daily để nhận tiền khởi đầu.")
            return

        if bet.lower() == "all":
            bet_amount = min(users.get(user_id, {}).get("balance", 0), 10000000)
        else:
            try:
                bet_amount = int(bet)
                if bet_amount <= 0:
                    await ctx.send(f"{ctx.author.mention} Số tiền cược phải là một số dương lớn hơn 0!")
                    return
                bet_amount = min(bet_amount, 10000000)  
            except ValueError:
                await ctx.send(f"{ctx.author.mention} Vui lòng nhập số tiền hợp lệ hoặc 'all' để cược tất cả.")
                return

        if users[user_id]["balance"] < bet_amount:
            await ctx.send(f"{ctx.author.mention} Bạn không có đủ tiền để đặt cược.")
            return

        horses = ["🐎", "🏇", "🐴", "🐢"]  
        random.shuffle(horses)

        winning_horse = random.choice(horses)
        user_choice = random.choice(horses)

        if winning_horse == user_choice:
            prize = bet_amount * 10
            users[user_id]["balance"] += prize
            result_message = f"Chúc mừng {ctx.author.mention}! Ngựa của bạn đã thắng! Bạn nhận được {self.format_currency(prize)} VND."
        else:
            users[user_id]["balance"] -= bet_amount
            result_message = f"Rất tiếc {ctx.author.mention}, ngựa của bạn đã thua. Bạn mất {self.format_currency(bet_amount)} VND."

        self.save_users(users)

        race_result = f"Đua ngựa:\n{''.join(horses)}\nNgựa của bạn: {user_choice}\nNgựa thắng: {winning_horse}\n"

        embed = nextcord.Embed(title="Kết quả đua ngựa", description=race_result, color=nextcord.Color.green())
        embed.add_field(name="Kết quả", value=result_message, inline=False)
        embed.set_footer(text=f"Số dư hiện tại của bạn là {self.format_currency(users[user_id]['balance'])} VND.")

        await ctx.send(embed=embed)
      
def setup(bot):
    bot.add_cog(HorseRacing(bot))
