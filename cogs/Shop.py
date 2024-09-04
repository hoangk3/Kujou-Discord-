import json
import os
import random
import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta

class Shop(commands.Cog):
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

    def initialize_user_data(self, users):
        """Khởi tạo dữ liệu người dùng với các khóa cần thiết nếu chưa có."""
        for user_id in users:
            if "items" not in users[user_id]:
                users[user_id]["items"] = []  # Khởi tạo khóa items
            if "balance" not in users[user_id]:
                users[user_id]["balance"] = 0  # Khởi tạo số dư nếu chưa có

    @commands.command(name="shop")
    async def shop(self, ctx):
        """Hiển thị cửa hàng."""
        embed = nextcord.Embed(title="Cửa hàng", description="Danh sách các mặt hàng có sẵn để mua", color=0x00ff00)
        embed.set_image(url="https://i.pinimg.com/originals/ab/27/3e/ab273ef561d66b5443c9f6adbca443f6.gif")
        
        shop_items = [
            {"name": "Xe wave", "description": "Gây thiệt hại tiền mặt 10-25% cho đối thủ dùng 1 lần", "price": 550_000_000},
            {"name": "Phóng Lợn", "description": "Chọc vào người chơi khác khiến họ mất 5-15% số tiền đang có", "price": 30_000_000},
        ]

        for i, item in enumerate(shop_items, 1):
            embed.add_field(name=f"{i}. {item['name']}", value=f"{item['description']} - Giá: {self.format_currency(item['price'])} VND", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="get")
    async def get(self, ctx, item_number: int):
        """Mua item từ cửa hàng."""
        user_id = str(ctx.author.id)
        users = self.get_users()
        self.initialize_user_data(users)  # Khởi tạo dữ liệu người dùng

        items = {
            1: {"name": "Xe wave", "price": 550_000_000},
            2: {"name": "Phóng Lợn", "price": 30_000_000},
        }

        if item_number not in items:
            await ctx.send(f"{ctx.author.mention} Số thứ tự mặt hàng không hợp lệ.")
            return

        item = items[item_number]

        if users[user_id]["balance"] < item["price"]:
            await ctx.send(f"{ctx.author.mention} Bạn không đủ tiền để mua {item['name']}.")
            return
        
        users[user_id]["balance"] -= item["price"]
        users[user_id]["items"].append({"name": item["name"], "used": False})

        self.save_users(users)

        await ctx.send(f"{ctx.author.mention} Bạn đã mua {item['name']} thành công!")

    @commands.command(name="bag")
    async def bag(self, ctx):
        """Xem túi đồ."""
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users or not users[user_id].get("items"):
            await ctx.send(f"{ctx.author.mention} Túi đồ của bạn trống rỗng.")
            return

        items = users[user_id]["items"]
        embed = nextcord.Embed(title="Túi đồ của bạn", description="Danh sách các vật phẩm bạn đang sở hữu", color=0x00ff00)
        
        for i, item in enumerate(items, 1):
            embed.add_field(name=f"{i}. {item['name']}", value=f"ID: {i}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="use")
    async def use(self, ctx, item_number: int, target: nextcord.Member = None):
        """Sử dụng item trong túi đồ."""
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users or not users[user_id].get("items"):
            await ctx.send(f"{ctx.author.mention} Túi đồ của bạn trống rỗng.")
            return

        if item_number < 1 or item_number > len(users[user_id]["items"]):
            await ctx.send(f"{ctx.author.mention} Số thứ tự item không hợp lệ.")
            return

        item = users[user_id]["items"][item_number - 1]

        if item["used"]:
            await ctx.send(f"{ctx.author.mention} Bạn đã sử dụng {item['name']} rồi.")
            return

        if item["name"] == "Xe wave" and target:
            target_id = str(target.id)
            if target_id not in users:
                await ctx.send(f"{ctx.author.mention} Người dùng không tồn tại.")
                return
            
            damage_percentage = random.randint(10, 25)
            damage_amount = int(users[target_id]["balance"] * (damage_percentage / 100))
            users[target_id]["balance"] -= damage_amount
            message = f"Bạn đã sử dụng {item['name']} để gây thiệt hại {self.format_currency(damage_amount)} VND cho {target.mention}."

        elif item["name"] == "Phóng Lợn" and target:
            target_id = str(target.id)
            if target_id not in users:
                await ctx.send(f"{ctx.author.mention} Người dùng không tồn tại.")
                return
            
            damage_percentage = random.randint(5, 15)
            damage_amount = int(users[target_id]["balance"] * (damage_percentage / 100))
            users[target_id]["balance"] -= damage_amount
            message = f"Bạn đã sử dụng {item['name']} để chọc vào {target.mention}, khiến họ mất {self.format_currency(damage_amount)} VND."

        item["used"] = True
        self.save_users(users)
        await ctx.send(f"{ctx.author.mention} {message}")

def setup(bot):
    bot.add_cog(Shop(bot))
