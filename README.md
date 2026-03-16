# Monopoly‑game‑Python

*Monopoly‑style board game implemented in Python using Pygame with AI opponents and modular architecture.*

About: 
This project is a Python implementation of the classic board game Monopoly. The game simulates many elements of the original board game, allowing players to move around the board with dice rolls, buy properties, collect rent, and compete to bankrupt their opponents. 
Monopoly is a turn‑based game where the main goal is to accumulate wealth and eliminate other players by smart investment and property management.

How to Play: 
The objective of the game is to become the richest player while forcing others into bankruptcy. Start with a fixed amount of money, then take turns rolling two dice and moving your token around the board. 
On your turn: 
1) Roll the dice and move accordingly.
2) If you land on an unowned property, you may buy it.
3) If the property is already owned by another player, you must pay rent.
4) Certain special spaces (like Chance, Community Chest, or Jail) trigger unique effects.
5) Make strategic decisions: buy properties, form monopolies, and manage your cash wisely.
6) Keep playing until only one player remains solvent — the winner!

Features: 
Modular game structure with multiple Python modules (board.py, player.py, dice.py), basic AI opponents to play against, uses Pygame for graphics and interaction, dice rolling and board movement logic, ownership and finances handled per player, menu and gameplay flow managed via main.py and menu.py.

Game Screenshot:
<img width="939" height="784" alt="monopoly" src="https://github.com/user-attachments/assets/cc35a377-2f3b-48d0-a58d-72f23290c151" />



What’s Included: 
main.py - The main entry point of the game
board.py - Board setup and fields
dice.py - Dice rolling logic
player.py - Player data and behavior
ai_strategy.py - AI decision making
menu.py - Main menu and UI flow
test_game.py - Tests for game logic
images/ - Game graphics assets
sounds/ - Game sound assets

License:
All photos and music are from publicly available sources. This project is for academic purposes only and I do not make any money from it.
