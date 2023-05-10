# pooper-adventures
can pooper's adventures  
very much a work in progress lol  
will (hopefully) be my first big project  

## Controls
- W/up arrow: jump
- A/left arrow: move left
- D/right arrow: move right
- S/down arrow/shift: crouch
- space to shoot

## Editor Guide
pass a file path as the first command-line argument to import a level into the editor.  
ex: `python3 editor.py levels/1.json`

Controls:

- H/L to decrease/increase width
- J/K to decrease/increase height
- up arrow to double width and height
- down arrow to half width and height

arrow keys are recommended over H/L/J/K because using the latter doesn't work very well with the grid system

Control Panel:
- Click on each icon to add different types of sprites
- Click on the trash can to enter "delete mode" (sprites you click on will be deleted)
- Click on the download icon to save a level to the `/levels` folder (it will look for the first available level number to use)
- Click on the 2 arrows icon to change the orientation of enemies (this only affects enemy sprites)

note that you can only place 1 player and 1 objective for obvious reasons (you can't delete a player or objective with "delete mode" either, because you can just re-place them)

## Advanced (CLI Options)

this game offers some cli options for those who likes the cli so much
they are used to alter the behaviour of the game in a way that is usually only useful for debugging
here are the only ones we have so far

u can also check der source code if u want to see what they do behind the scenes

- `--enable-level-skipping`: lets u skip levels with keypress. used fer dev purposes only, do not use to cheat!!!
- `--not-resizable`: make the window hard to that u cant resize it. useful for some tiling wms (like i3wm).
