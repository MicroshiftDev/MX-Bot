# 🤖 Open Source Discord Bot

A fully-featured, open-source Discord bot built with Python and [discord.py](https://discordpy.readthedocs.io/).  
Easily customizable, ready to translate from Polish to your language, and designed to support a wide variety of community needs.

---

## 🛠️ Technologies

- **Python**
- **discord.py**

---

## ✨ Features

- 🎚️ Leveling system with ranks
- 🎁 Giveaway creator and reroll
- 🐾 Fun commands (`/cat`, `/dog`, `/flip`, `/ship`, `/roll`)
- 🎟️ Tickets system with panels
- 🧰 Moderation tools (ban, mute, kick, etc.)
- 📊 Server and user info utilities

---

## 🧩 Commands Overview

### 📢 Administration & Moderation

| Command | Description |
|--------|-------------|
| `!ogloszenie <title> [image] [buttons]` | Creates an ad embed with optional image and buttons |
| `!ban [time in hours]` | Temporarily bans a user |
| `!kick` | Kicks a user from the server |
| `!clear` | Clears a number of recent messages |
| `!mute [time] [reason]` | Temporarily mutes a user |
| `!unmute` | Unmutes a previously muted user |
| `!unban` | Unbans a user |
| `!send_panel` | Sends the ticket panel to a channel |

---

### 🎉 Giveaways

| Command | Description |
|--------|-------------|
| `!konkurs [time in hours]` | Creates a giveaway |
| `!konkurs-reroll` | Rerolls a new winner for the giveaway |

---

### 🐱 Fun & Random

| Command | Description |
|--------|-------------|
| `!kot` | Sends a random cat image |
| `!pies` | Sends a random dog image |
| `!flip` | Flips a coin |
| `!roll {number}` | Rolls a number between 1 and `{number}` |
| `!ship @user1 @user2` | Checks compatibility between two users |
| `/hello` | Bot responds with "Hello!" |

---

### 📈 Levels

| Command | Description |
|--------|-------------|
| `!level` | Displays your current level and XP |
| `!top` | Shows top 10 users by XP |
| `!nagroda` | Claim extra XP every 24 hours |

---

### 🧾 Info

| Command | Description |
|--------|-------------|
| `!ping` | Shows bot latency |
| `!info` | Displays bot statistics |
| `!rangi` | Shows rank roles and XP thresholds |
| `!data` | Displays current date |
| `!server` | Shows server info |

---

## 🌍 Localization

All default messages are in **Polish**, but you can freely translate and customize them to your language by editing the source code.

---

## 📬 Ticket System

Set up the ticket system with `!send_panel`.  
Users can click 🎟️ **Open a Ticket** to start a private conversation with your team.

---

## 🧑‍💻 Contributions

Feel free to fork, improve, and submit pull requests!  
This bot is community-friendly and designed to be **easy to modify**.
