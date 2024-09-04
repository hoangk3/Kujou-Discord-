import random
import nextcord
from nextcord.ext import commands
import asyncio
import json
import os

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.users_file = "users.json"
        self.check_and_initialize_users()

    def create_deck(self):
        suits = ['♠️', '♥️', '♦️', '♣️']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]
        random.shuffle(deck)
        return deck

    def draw_card(self, hand):
        if not self.deck:
            self.deck = self.create_deck()  # Tạo lại bộ bài nếu hết
        card = self.deck.pop()
        hand.append(card)
        return card

    def calculate_hand_value(self, hand):
        value = 0
        aces = 0
        for card in hand:
            if card['rank'] in ['J', 'Q', 'K']:
                value += 10
            elif card['rank'] == 'A':
                value += 11
                aces += 1
            else:
                value += int(card['rank'])

        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value    

    def hand_to_string(self, hand):
        return ' '.join([f"{card['rank']}{card['suit']}" for card in hand])

    def format_currency(self, amount):
        return f"{amount:,} VND"

    def check_and_initialize_users(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def get_users(self):
        if not os.path.exists(self.users_file):
            return {}
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_users(self, users):
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

    @commands.command(name="bj")
    async def blackjack(self, ctx, bet: str):
        user_id = str(ctx.author.id)
        users = self.get_users()
        MAX_BET = 100000000000 # 10b  VND

        if user_id not in users:
            await ctx.send(f"{ctx.author.mention} Bạn chưa đăng ký. Sử dụng lệnh !daily để nhận tiền khởi đầu.")
            return

        if bet.lower() == "all":
            bet_amount = min(users[user_id]["balance"], MAX_BET)
        else:
            try:
                bet_amount = int(bet)
                if bet_amount <= 0:
                    await ctx.send(f"{ctx.author.mention} Số tiền cược phải lớn hơn 0.")
                    return
                if bet_amount > MAX_BET:
                    await ctx.send(f"{ctx.author.mention} Số tiền cược tối đa là {self.format_currency(MAX_BET)} VND.")
                    return
            except ValueError:
                await ctx.send(f"{ctx.author.mention} Vui lòng nhập số tiền hợp lệ hoặc 'all' để cược tất cả.")
                return

        if users[user_id]["balance"] < bet_amount:
            await ctx.send(f"{ctx.author.mention} Bạn không có đủ tiền để đặt cược.")
            return

        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.bet = bet_amount

        self.draw_card(self.player_hand)
        self.draw_card(self.player_hand)
        self.draw_card(self.dealer_hand)
        self.draw_card(self.dealer_hand)

        embed = nextcord.Embed(title="Blackjack", color=nextcord.Color.dark_green())
        embed.add_field(name="Your Hand", value=f"{self.hand_to_string(self.player_hand)}\nValue: {self.calculate_hand_value(self.player_hand)}", inline=False)
        embed.add_field(name="Dealer's Hand", value=f"{self.hand_to_string(self.dealer_hand[:1])} ??", inline=False)
        embed.set_footer(text=f"{ctx.author.name}, react with 🃏 to draw a card, 🛑 to hold your hand.")

        message = await ctx.send(embed=embed)
        await message.add_reaction('🃏')
        await message.add_reaction('🛑')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['🃏', '🛑']

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                if str(reaction.emoji) == '🃏':
                    card = self.draw_card(self.player_hand)
                    player_value = self.calculate_hand_value(self.player_hand)

                    embed = nextcord.Embed(title="Blackjack - Hit", color=nextcord.Color.blue())
                    embed.add_field(name="Your Hand", value=f"{self.hand_to_string(self.player_hand)}\nValue: {player_value}", inline=False)

                    if player_value > 21:
                        embed.add_field(name="Result", value="You busted! Dealer wins.", inline=False)
                        self.player_hand = []
                        users[user_id]["balance"] -= self.bet
                        self.save_users(users)
                        await self.update_message(message, embed)
                        await ctx.send(f"{ctx.author.mention} Bạn đã thua. Số dư hiện tại của bạn là {self.format_currency(users[user_id]['balance'])} VND.")
                        break
                    else:
                        embed.add_field(name="Dealer's Hand", value=f"{self.hand_to_string(self.dealer_hand[:1])} ??", inline=False)
                        embed.set_footer(text=f"{ctx.author.name}, react with 🃏 to draw another card, 🛑 to hold your hand.")
                        await self.update_message(message, embed)

                elif str(reaction.emoji) == '🛑':
                    player_value = self.calculate_hand_value(self.player_hand)
                    dealer_value = self.calculate_hand_value(self.dealer_hand)

                    while dealer_value < 17:
                        self.draw_card(self.dealer_hand)
                        dealer_value = self.calculate_hand_value(self.dealer_hand)

                    embed = nextcord.Embed(title="Blackjack - Stand", color=nextcord.Color.purple())
                    embed.add_field(name="Your Hand", value=f"{self.hand_to_string(self.player_hand)}\nValue: {player_value}", inline=False)
                    embed.add_field(name="Dealer's Hand", value=f"{self.hand_to_string(self.dealer_hand)}\nValue: {dealer_value}", inline=False)

                    if dealer_value > 21 or player_value > dealer_value:
                        embed.add_field(name="Result", value="You win!", inline=False)
                        users[user_id]["balance"] += self.bet
                    elif player_value < dealer_value:
                        embed.add_field(name="Result", value="Dealer wins!", inline=False)
                        users[user_id]["balance"] -= self.bet
                    else:
                        embed.add_field(name="Result", value="It's a tie!", inline=False)

                    self.save_users(users)
                    await self.update_message(message, embed)
                    await ctx.send(f"{ctx.author.mention} Số dư hiện tại của bạn là {self.format_currency(users[user_id]['balance'])} VND.")
                    break

            except nextcord.errors.NotFound:
                break
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention} Timed out. Please start a new game.")
                break

    async def update_message(self, message, embed):
        await message.edit(embed=embed)
        await message.clear_reactions()
        await message.add_reaction('🃏')  # Hit
        await message.add_reaction('🛑')  # Stand

def setup(bot):
    bot.add_cog(Blackjack(bot))
