Py Osu!Auto
===================

**DISCLAIMER:** This bot is made for educational purposes only. I do not recommend using it on your account, log off before doing so.  

__This bot only works and ALWAYS WILL only work with RELAX MOD toggled on, to discourage cheaters.__


# What is "Osu!"? <h1>
Better than me explaining is you checking it with your own eyes. See it [here](https://osu.ppy.sh/home).

But if you want the quick answer:
Osu! is a rhythm game where your objective is to click circles, sliders, and spinners to the beat of the song at the most precise timing possible.
The "beatmaps" are what players... You know... Play? They are made by the community itself so the replayability is infinite!

If the game only had circles and spinners, creating this bot would be the easiest thing ever, but since sliders are a thing my life was ruined while
doing it.
Sliders involve some pretty complicated calculations to find their paths and duration (Bezier curves, circumferences, etc)

# Requirements <h1>
* Python 3
* keyboard module

I made it on Windows but I'm pretty sure it works on Linux too, please let me know about it if you are a Linux user.

# Limitations <h1>
As you can see on the "Issues" tab, this bot is not perfect.

1. It is not FULLY automated. (What do you mean?? Isn't it a BOT?!?) Yes, it'll play almost any map perfectly, but you still need to load the .osu file and start it MANUALLY, read the "How to use" section for more information.
2. This bot does not do Aspire maps perfectly. Ye... Sorry about that one
3. Too fast sliders glitch the bot. And by "Too fast" I mean REALLY DAMN FAST. Other than those It works fine.
4. The bot only works if your game is on Fullscreen or Windowed fullscreen. Windowed won't work because it will calculate the coordinates wrong.

# How to use <h1>
1. Assuming you already have the requirements and the scripts on the same directory, all you need to do is run the main.py script, then:
2. Press "L" to choose a .osu file. (Navigate to your Osu! directory, then Songs folder)
3. After it prompts it loaded successfully, press "P" to start the bot. Note: You need to start the bot along with the first hitObject of the map, with the best sync possible.
4. You can press "D" or "H" or "R" at any moment to toggle DT or HT or HR, respectively.
5. You can press "S" while the bot is playing to force it to stop and regain the cursor control.
6. By default, the bot calculates the coordinates of the hitObjects by using your monitor's resolution as parameter. If you happen to be playing with a different resolution than your monitor's active one, press "Q" and manually type your in-game resolution.
7. You can press "O" to change the offset (in ms, default is 5). Offset is the time the bot takes before start playing after the user hits P. It's good because, as humans, it's really hard to hit the first hitObject with 100% precision, so set it to what you think works best for you.
8. To avoid the bot start playing when you don't want to, press the "Pause Break" key. It'll stop the bot from taking ANY prompt, until you press it again.
