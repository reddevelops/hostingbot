import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

# Replace with your bot token
TOKEN = "YOUR_BOT_TOKEN"

# Channel IDs (replace with your actual channel IDs)
POSTING_CHANNEL_ID = 1348364958080962673  # Channel where users submit posts
APPROVAL_CHANNEL_ID = 1349474492023443596  # Channel where mods approve posts
HIRING_CHANNEL_ID = 1349474929015390348  # Channel for approved hiring posts
FOR_HIRE_CHANNEL_ID = 1349475085362135111  # Channel for approved for-hire posts
SELLING_CHANNEL_ID = 1349475524107436137  # Channel for approved selling posts

# Store user posts temporarily
user_posts = {}

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")
    await bot.tree.sync()  # Sync slash commands

# Slash command: /post
@bot.tree.command(name="post", description="Submit a post for approval")
@app_commands.describe(job_type="The type of job post")
@app_commands.choices(job_type=[
    app_commands.Choice(name="Hiring", value="hiring"),
    app_commands.Choice(name="For Hire", value="for_hire"),
    app_commands.Choice(name="Selling", value="selling"),
])
async def post(interaction: discord.Interaction, job_type: app_commands.Choice[str]):
    # Check if the command is used in the correct channel
    if interaction.channel_id != POSTING_CHANNEL_ID:
        return await interaction.response.send_message(
            "You can only use this command in the posting channel!", ephemeral=True
        )

    # Create an embed for the post
    embed = discord.Embed(
        description=f"{interaction.user.name} - Once this has been accepted, it should automatically be posted.\n*Not set*",  # User's name and reminder
        color=discord.Color.blue(),  # Use a professional blue color
    )
    embed.add_field(
        name="Payment",
        value="Robux: *Not set*\nMoney: *Not set*\nOther: *Not set*",
        inline=False,
    )
    embed.set_footer(text="Use the buttons below to edit and submit your post.")

    # Create buttons
    edit_description_button = Button(style=discord.ButtonStyle.primary, label="Edit Description", custom_id="edit_description")
    edit_payment_button = Button(style=discord.ButtonStyle.primary, label="Edit Payment", custom_id="edit_payment")
    submit_button = Button(style=discord.ButtonStyle.green, label="Submit", custom_id="submit_post")

    # Create a view to hold the buttons
    view = View()
    view.add_item(edit_description_button)
    view.add_item(edit_payment_button)
    view.add_item(submit_button)

    # Send the embed with buttons
    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True,  # Only the user can see this message
    )

    # Store the post data temporarily
    user_posts[interaction.user.id] = {
        "job_type": job_type.value,  # Use job_type.value instead of job_type.name
        "description": "*Not set*",
        "payment": {
            "Robux": "*Not set*",
            "Money": "*Not set*",
            "Other": "*Not set*",
        },
        "message": await interaction.original_response(),  # Store the original message
    }

    # Modal for editing the description
    class DescriptionModal(Modal, title="Edit Description"):
        description_input = TextInput(
            label="Description",
            style=discord.TextStyle.long,
            placeholder="Enter the job description...",
            required=True,
        )

        async def on_submit(self, interaction: discord.Interaction):
            post_data = user_posts[interaction.user.id]
            post_data["description"] = self.description_input.value

            # Update the embed with the new description
            embed = discord.Embed(
                description=f"{interaction.user.name} - Once this has been accepted, it should automatically be posted.\n{post_data['description']}",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Payment",
                value=f"Robux: {post_data['payment']['Robux']}\nMoney: {post_data['payment']['Money']}\nOther: {post_data['payment']['Other']}",
                inline=False,
            )
            embed.set_footer(text="Use the buttons below to edit and submit your post.")

            # Edit the original message with the updated embed
            await post_data["message"].edit(embed=embed, view=view)
            await interaction.response.send_message(
                "Description updated successfully!", ephemeral=True
            )

    # Modal for editing the payment
    class PaymentModal(Modal, title="Edit Payment"):
        robux_input = TextInput(
            label="How much in Robux?",
            placeholder="Enter the Robux amount...",
            required=True,
        )
        money_input = TextInput(
            label="How much in Currency? ($, £, €)",
            placeholder="Enter the currency amount...",
            required=False,
        )
        other_input = TextInput(
            label="What other currencies?",
            placeholder="Enter other payment details...",
            required=False,
        )

        async def on_submit(self, interaction: discord.Interaction):
            post_data = user_posts[interaction.user.id]
            post_data["payment"]["Robux"] = self.robux_input.value
            post_data["payment"]["Money"] = self.money_input.value or "*Not set*"
            post_data["payment"]["Other"] = self.other_input.value or "*Not set*"

            # Update the embed with the new payment details
            embed = discord.Embed(
                description=f"{interaction.user.name} - Once this has been accepted, it should automatically be posted.\n{post_data['description']}",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Payment",
                value=f"Robux: {post_data['payment']['Robux']}\nMoney: {post_data['payment']['Money']}\nOther: {post_data['payment']['Other']}",
                inline=False,
            )
            embed.set_footer(text="Use the buttons below to edit and submit your post.")

            # Edit the original message with the updated embed
            await post_data["message"].edit(embed=embed, view=view)
            await interaction.response.send_message(
                "Payment details updated successfully!", ephemeral=True
            )

    # Handle button interactions
    async def button_callback(interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in user_posts:
            return await interaction.response.send_message(
                "Your post data is no longer available. Please start over.",
                ephemeral=True,
            )

        if interaction.data["custom_id"] == "edit_description":
            # Show the description modal
            modal = DescriptionModal()
            await interaction.response.send_modal(modal)

        elif interaction.data["custom_id"] == "edit_payment":
            # Show the payment modal
            modal = PaymentModal()
            await interaction.response.send_modal(modal)

        elif interaction.data["custom_id"] == "submit_post":
            # Create the final embed
            post_data = user_posts[user_id]
            embed = discord.Embed(
                description=f"{interaction.user.name} - Once this has been accepted, it should automatically be posted.\n{post_data['description']}",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Payment",
                value=f"Robux: {post_data['payment']['Robux']}\nMoney: {post_data['payment']['Money']}\nOther: {post_data['payment']['Other']}",
                inline=False,
            )
            embed.set_footer(text="Awaiting approval...")

            # Send the post to the approval channel
            approval_channel = bot.get_channel(APPROVAL_CHANNEL_ID)
            if approval_channel:
                await approval_channel.send(embed=embed)
                await interaction.response.send_message(
                    "Your post has been submitted for approval!", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "Approval channel not found. Please contact a moderator.", ephemeral=True
                )

            # Clear the user's post data
            del user_posts[user_id]

    # Assign the callback to the buttons
    edit_description_button.callback = button_callback
    edit_payment_button.callback = button_callback
    submit_button.callback = button_callback

# Command: Approve a post
@bot.tree.command(name="approve", description="Approve a post")
@app_commands.describe(message_id="The ID of the message to approve")
async def approve(interaction: discord.Interaction, message_id: str):
    # Check if the user is an admin
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(
            "You do not have permission to approve posts!", ephemeral=True
        )

    # Fetch the message from the approval channel
    approval_channel = bot.get_channel(APPROVAL_CHANNEL_ID)
    if not approval_channel:
        return await interaction.response.send_message(
            "Approval channel not found.", ephemeral=True
        )

    try:
        message = await approval_channel.fetch_message(int(message_id))
    except discord.NotFound:
        return await interaction.response.send_message(
            "Message not found. Please check the message ID.", ephemeral=True
        )

    # Get the embed from the message
    if not message.embeds:
        return await interaction.response.send_message(
            "No embed found in the message.", ephemeral=True
        )

    embed = message.embeds[0]

    # Determine the destination channel based on the job type
    job_type = user_posts.get(interaction.user.id, {}).get("job_type", "")
    if job_type == "hiring":
        destination_channel = bot.get_channel(HIRING_CHANNEL_ID)
    elif job_type == "for_hire":
        destination_channel = bot.get_channel(FOR_HIRE_CHANNEL_ID)
    elif job_type == "selling":
        destination_channel = bot.get_channel(SELLING_CHANNEL_ID)
    else:
        return await interaction.response.send_message(
            "Invalid job type.", ephemeral=True
        )

    if not destination_channel:
        return await interaction.response.send_message(
            "Destination channel not found.", ephemeral=True
        )

    # Send the approved post to the destination channel
    await destination_channel.send(embed=embed)
    await message.delete()  # Delete the post from the approval channel
    await interaction.response.send_message(
        f"Post approved and moved to {destination_channel.mention}!", ephemeral=True
    )

# Command: Disapprove a post
@bot.tree.command(name="disapprove", description="Disapprove a post")
@app_commands.describe(message_id="The ID of the message to disapprove")
async def disapprove(interaction: discord.Interaction, message_id: str):
    # Check if the user is an admin
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(
            "You do not have permission to disapprove posts!", ephemeral=True
        )

    # Fetch the message from the approval channel
    approval_channel = bot.get_channel(APPROVAL_CHANNEL_ID)
    if not approval_channel:
        return await interaction.response.send_message(
            "Approval channel not found.", ephemeral=True
        )

    try:
        message = await approval_channel.fetch_message(int(message_id))
    except discord.NotFound:
        return await interaction.response.send_message(
            "Message not found. Please check the message ID.", ephemeral=True
        )

    # Delete the post from the approval channel
    await message.delete()
    await interaction.response.send_message(
        "Post disapproved and deleted.", ephemeral=True
    )

# Run the bot
bot.run(TOKEN)