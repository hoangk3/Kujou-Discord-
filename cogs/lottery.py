import json
import random
from datetime import datetime, timedelta
from nextcord.ext import commands, tasks
import nextcord

class Lottery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = 'users.json'
        self.lottery_channel_id = 1280518390942793859  # Thay thế bằng ID kênh cố định của bạn
        self.ticket_prices = [25000000, 50000000, 75000000, 100000000, 10000000, 15000000]  # Giá vé từ 25-100 triệu VND
        self.tickets = []
        self.winning_ticket = None
        self.start_new_round()

    def get_users(self):
        with open(self.file_path, 'r') as f:
            return json.load(f)
    
    def save_users(self, users):
        with open(self.file_path, 'w') as f:
            json.dump(users, f, indent=4)

    def start_new_round(self):
        self.tickets = [{"id": i + 1, "price": random.choice(self.ticket_prices), "buyer": None} for i in range(10)]
        self.winning_ticket = None
        self.lottery_task.start()

    def format_currency(self, amount): 
        return "{:,}".format(amount)

    @tasks.loop(minutes=30)
    async def lottery_task(self):
        self.winning_ticket = random.choice([ticket for ticket in self.tickets if ticket["buyer"]])
        if self.winning_ticket:
            users = self.get_users()
            buyer_id = self.winning_ticket["buyer"]
            users[buyer_id]["balance"] += self.winning_ticket["price"] * 4
            self.save_users(users)

            channel = self.bot.get_channel(self.lottery_channel_id)
            embed = nextcord.Embed(title="Kết quả xổ số", description=f"Tờ vé số trúng giải: #{self.winning_ticket['id']}\nNgười thắng: <@{buyer_id}>\nPhần thưởng: {self.format_currency(self.winning_ticket['price'] * 4)} VND", color=0xFFD700)
            await channel.send(embed=embed)
        self.start_new_round()

    @commands.command(name="ticket")
    async def view_tickets(self, ctx):
        embed = nextcord.Embed(title="Vé số đang được bán", color=0x00FF00)
        for ticket in self.tickets:
            status = f"Đã mua bởi <@{ticket['buyer']}>" if ticket["buyer"] else "Chưa bán"
            embed.add_field(name=f"Vé số #{ticket['id']}", value=f"Giá: {self.format_currency(ticket['price'])} VND\n{status}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="bticket")
    async def buy_ticket(self, ctx, ticket_id: int):
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users:
            users[user_id] = {"balance": 0}

        if any(ticket["buyer"] == user_id for ticket in self.tickets):
            await ctx.send("Bạn chỉ được mua tối đa 1 vé mỗi phiên.")
            return

        ticket = next((t for t in self.tickets if t["id"] == ticket_id), None)

        if not ticket:
            await ctx.send("Mã vé không hợp lệ.")
            return

        if ticket["buyer"]:
            await ctx.send("Vé này đã được mua.")
            return

        if users[user_id]["balance"] < ticket["price"]:
            await ctx.send("Bạn không có đủ tiền để mua vé.")
            return

        users[user_id]["balance"] -= ticket["price"]
        ticket["buyer"] = user_id
        self.save_users(users)

        await ctx.send(f"Bạn đã mua vé #{ticket_id} với giá {self.format_currency(ticket['price'])} VND.")

    def cog_unload(self):
        self.lottery_task.cancel()

def setup(bot):
    bot.add_cog(Lottery(bot))
