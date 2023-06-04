# pooper-adventures
Pooper Adventures

## Plot

You are Can Pooper, a Pooper who lives in Canada. One day, you woke up to find that you're hungry, and that your fridge is empty. So, you decide to venture south into a mystical land called Poopland, rumored to be full of burgers. Unfortunately, there are angry Poopers trying to kill you with their guns, since they don't like outsiders venturing into their land. Luckily though, you brought your own handgun with you...

## Controls
- W/up arrow: jump
- A/left arrow: move left
- D/right arrow: move right
- S/down arrow/shift: crouch
- space to shoot

## Run

```
$ git clone https://github.com/carpetmaker3162/pooper-adventures
$ cd pooper-adventures
$ python3 main.py
```

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

## Credit

credit to earthtraveller1 for the soundtrack and some other stuff I forgot
