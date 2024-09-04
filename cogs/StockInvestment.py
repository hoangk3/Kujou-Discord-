import random
import nextcord
from nextcord.ext import commands, tasks
import json
import os

class StockInvestment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stocks = {
            "Puppy88 - nhà cái hàng đầu châu âu": 350000,
            "Cty cổ phần số học 6h30": 680000,
            "Cty Thương Mại và Đầu Tư crypto": 840000,
            "Cty cổ phần TNHH MTV Vạn Thịnh Phát": 400000,
            "Cty cổ phần thế giới di động": 400000,
            "Tập Đoàn Công Nghệ Space X": 480000
        
        }
        self.previous_prices = self.stocks.copy()
        self.stock_market.start()  # task loop
        self.banner_url = "https://i.pinimg.com/originals/ab/27/3e/ab273ef561d66b5443c9f6adbca443f6.gif"  # Thay bằng URL của banner của bạn

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
        """Định dạng số tiền để hiển thị và làm tròn số."""
        return "{:,}".format(round(amount))

    @tasks.loop(minutes=1)
    async def stock_market(self):
        """Mô phỏng sự thay đổi giá cổ phiếu mỗi phút."""
        for stock in self.stocks:
            change = random.uniform(-0.05, 0.05)  # Giá thay đổi từ -50% đến +50%
            self.stocks[stock] = round(self.stocks[stock] * (1 + change))

    @commands.command(name="list")
    async def list_stocks(self, ctx):
        """Hiển thị danh sách cổ phiếu đã mua của người dùng."""
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users or "stocks" not in users[user_id]:
            await ctx.send(f"{ctx.author.mention} Bạn không có cổ phiếu nào trong danh mục đầu tư.")
            return

        portfolio = users[user_id]["stocks"]
        if not portfolio:
            await ctx.send(f"{ctx.author.mention} Bạn không có cổ phiếu nào trong danh mục đầu tư.")
            return
        
        embed = nextcord.Embed(title="Danh Mục Đầu Tư Của Bạn", color=nextcord.Color.green())
        for idx, (stock, data) in enumerate(portfolio.items(), 1):
            amount, buy_price = data
            embed.add_field(name=f"{idx}. {stock}", value=f"Số lượng: {amount} cổ phiếu\nGiá mua: {self.format_currency(buy_price)} VND", inline=False)
        
        embed.set_footer(text="Cập nhật giá sau mỗi phút")
        embed.set_image(url="https://i.pinimg.com/originals/ab/27/3e/ab273ef561d66b5443c9f6adbca443f6.gif")  # Thay bằng URL của banner lớn của bạn
        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy_stock(self, ctx, stock_number: int, amount: int):
        """Mua cổ phiếu."""
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention} Số lượng cổ phiếu phải là số dương.")
            return

        user_id = str(ctx.author.id)
        stock_list = list(self.stocks.keys())
        
        if stock_number < 1 or stock_number > len(stock_list):
            await ctx.send(f"{ctx.author.mention} Số thứ tự cổ phiếu không hợp lệ.")
            return

        stock = stock_list[stock_number - 1]
        stock_price = round(self.stocks[stock] * amount)

        users = self.get_users()

        if user_id not in users or users[user_id]["balance"] < stock_price:
            await ctx.send(f"{ctx.author.mention} Bạn không có đủ tiền để mua cổ phiếu này.")
            return

        users[user_id]["balance"] -= stock_price
        if "stocks" not in users[user_id]:
            users[user_id]["stocks"] = {}
        if stock in users[user_id]["stocks"]:
            current_amount, _ = users[user_id]["stocks"][stock]
            users[user_id]["stocks"][stock] = (current_amount + amount, round(self.stocks[stock]))
        else:
            users[user_id]["stocks"][stock] = (amount, round(self.stocks[stock]))

        self.save_users(users)
        await ctx.send(f"{ctx.author.mention} Bạn đã mua {amount} cổ phiếu {stock} với giá {self.format_currency(stock_price)} VND.")

    @commands.command(name="sell")
    async def sell_stock(self, ctx, stock_number: int, amount: int):
        """Bán cổ phiếu."""
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention} Số lượng cổ phiếu phải là số dương.")
            return

        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users or "stocks" not in users[user_id]:
            await ctx.send(f"{ctx.author.mention} Bạn không có cổ phiếu nào trong danh mục đầu tư.")
            return
        
        portfolio = users[user_id]["stocks"]
        if not portfolio or stock_number < 1 or stock_number > len(portfolio):
            await ctx.send(f"{ctx.author.mention} Số thứ tự cổ phiếu không hợp lệ.")
            return

        stock = list(portfolio.keys())[stock_number - 1]
        if amount > portfolio[stock][0]:
            await ctx.send(f"{ctx.author.mention} Bạn không có đủ cổ phiếu để bán.")
            return

        # Tính toán lãi hoặc lỗ
        buy_price = portfolio[stock][1]
        sell_price = self.stocks[stock]
        profit_or_loss = round((sell_price - buy_price) * amount)
        
        stock_sale_price = round(sell_price * amount)
        users[user_id]["balance"] += stock_sale_price
        users[user_id]["stocks"][stock] = (portfolio[stock][0] - amount, buy_price)
        if users[user_id]["stocks"][stock][0] == 0:
            del users[user_id]["stocks"][stock]

        self.save_users(users)
        if profit_or_loss >= 0: 
            await ctx.send(f"{ctx.author.mention} Bạn đã bán {amount} cổ phiếu {stock} với giá {self.format_currency(stock_sale_price)} VND. Bạn đã lãi {self.format_currency(profit_or_loss)} VND.")
        else:
            await ctx.send(f"{ctx.author.mention} Bạn đã bán {amount} cổ phiếu {stock} với giá {self.format_currency(stock_sale_price)} VND. Bạn đã lỗ {self.format_currency(-profit_or_loss)} VND.")

    @commands.command(name="tt")
    async def show_stocks(self, ctx):
        """Hiển thị giá cổ phiếu hiện tại."""
        embed = nextcord.Embed(title="Giá Cổ Phiếu Hiện Tại", color=nextcord.Color.blue())
        for idx, (stock, price) in enumerate(self.stocks.items(), 1):
            previous_price = self.previous_prices[stock]
            emoji = "📈" if price > previous_price else "📉"
            embed.add_field(name=f"{idx}. {stock}", value=f"Giá: {self.format_currency(price)} VND {emoji}", inline=False)

        embed.set_footer(text="Cập nhật giá sau mỗi phút")
        embed.set_image(url="https://i.pinimg.com/originals/ab/27/3e/ab273ef561d66b5443c9f6adbca443f6.gif")  # Thay bằng URL của banner lớn của bạn
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(StockInvestment(bot))
