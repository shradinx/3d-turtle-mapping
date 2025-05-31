# Interactive 3D Mapping &mdash; ComputerCraft Turtle Environment

This program displays a 3D application aimed at connecting to a ComputerCraft turtle via a local websocket server and giving the user the ability to map out and interact with the environment around the turtle.

![Example of turtle mapping its environment](src/resources/img/example.png)

## Libraries Used:
- [Ursina - Game Engine written in Python](https://github.com/pokepetter/ursina)
  - [Documentation](https://www.ursinaengine.org/documentation.html)
  - [API Reference](https://www.ursinaengine.org/api_reference.html)
- [Websockets](https://pypi.org/project/websockets/)

## Requirements
- Python 3.12 (recommended) (may work on older versions however have not tested)
- Minecraft: Java Edition w/ ComputerCraft mod
- HTTP enabled in ComputerCraft config
- Any ComputerCraft turtle

## How to Run:
1. Install the pip requirements in `requirements.txt` by running `pip install -r requirements.txt`
2. Run the `main.py` script to start the 3D application and websocket server.
3. Connect your in-game ComputerCraft turtle to the server using one of two methods linked below and run the script.
   1. *(Recommended)* Command for pastebin: `pastebin get 39M0XxZp` (Optional `websocket.lua` can be appened if you want to change the script name when downloading from pastebin)
   2. Download the `websocket.lua` script found in the `src/turtle` directory, and upload it to your turtle using your file upload of choice.
4. Done! Your turtle is now connected to the websocket server and you can control it via the keyboard/mouse and action buttons.

## Notes
- Make sure your turtle has fuel prior to connecting it to the websocket server, as turtles require fuel to move around.
- The block breaking actions will only work if there is a pickaxe equipped on either side of the turtle.

## Controls
- W, S = Move Forward/Backward
- A, D = Turn Left/Right
- Space, Left Shift = Move Up/Down
- Left Click = Break mapped blocks in front/above/below turtle

## Action Buttons:
There are a number of buttons to help you perform tasks such as inspecting and breaking blocks around you.
- Inspect (Front/Up/Down) = Inspect the block in front, above, or below the turtle and map it in the 3D environment
- Dig (Front/Up/Down) = Break the block in front, above, or below the turtle, removing the block from the 3D environment and breaking the block in-game.
- Place (Front/Up/Down) = Places the currently selected block from the turtle's inventory in-game, also adding it to the 3D environment.

## Known Issues:
- Connecting multiple turtles/clients
- Disconnect issues between client/server

## Planned Features:
- Multiple client support with easy turtle switching
- Refueling from the 3D application
- Ability to place signs with text
- Automatic block inspection when moving

## Credits
[Ottomated](https://www.youtube.com/@ottomated) - Original Idea/Concept (using TypeScript)
 - [Minecraft, but I hacked into the OfflineTV server...](https://www.youtube.com/watch?v=pwKRbsDbxqc)
 - [Turtle Gambit GitHub Repository](https://github.com/ottomated/turtle-gambit)
