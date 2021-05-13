## make imports
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
# from tkinter import Tk
# from tkinter import messagebox
# import time

# Tk().wm_withdraw()

speedDefiner = False

#automatically enter fulscreen view
window.fullscreen = True
window.color=color.black
Text.size *= 2

Button.color = color.azure
color.text_color = color.orange

app = Ursina()

## Load Textures
textures = {
    'grass_texture': load_texture('assets/images/grass_block.png'),
    'stone_texture': load_texture('assets/images/stone_block.png'),
    'brick_texture': load_texture('assets/images/brick_block.png'),
    'dirt_texture': load_texture('assets/images/dirt_block.png'),
    'sky_texture': load_texture('assets/images/skybox.png'),
    'arm_texture': load_texture('assets/images/arm_texture.png'),
    'punch_sound': Audio('assets/sounds/punch_sound',loop = False, autoplay = False)
}

# Setup First Person Player and disable exit button because we are using escape button to close game
block_pick = 'grass_texture'
player = FirstPersonController()

window.exit_button.enabled = False

# update per frame function
def update():
    global block_pick, app, speedDefiner

    # change hand animations
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    # toggle sprint 
    if held_keys['left control']:
        if speedDefiner == False:
            speedDefiner = True
            player.speed += 6

        elif speedDefiner == True:
            speedDefiner = False
            player.speed -= 6

    # block switcher
    if held_keys['1']: block_pick = 'grass_texture'
    if held_keys['2']: block_pick = 'stone_texture'
    if held_keys['3']: block_pick = 'brick_texture'
    if held_keys['4']: block_pick = 'dirt_texture'

    # sneak function (doesnt work at all yet)
    if held_keys['left shift']: player.set_position(Vec3(player.position.x, player.position.y - 0.25, player.position.z))

    block_icon.texture = textures[block_pick]

    # update coordinates
    cordsText.text = "X: {} || Y: {} || Z: {}".format(
                int(player.position.x),
                int(player.position.y),
                int(player.position.z)
            )

    if held_keys['escape']: sys.exit(0)

    # respawn/teleport to (0, y, 0) after falling in void
    if player.position.y < -10:
        # messagebox.showinfo('MemeCraft', 'You died by falling in the void! Press OK to respawn.')
        player.set_position(Vec3(0, 7, 0))

# voxel aka blocks object
class Voxel(Button):
    def __init__(self, position = (0,0,0), texture = textures['grass_texture']):
        super().__init__(
            parent = scene,
            position = position,
            model = 'assets/objects/block',
            origin_y = 0.5,
            texture = texture,
            color = color.color(0,0,random.uniform(0.9,1)),
            scale = 0.5)

    # function which reads keyboard/mouse input for the voxel
    def input(self,key):
        if self.hovered:
            # place new blocks
            if key == 'right mouse down':
                if (int(self.position.x) - int(player.position.x)) > 4:
                    return

                elif (int(self.position.z) - int(player.position.z)) > 4:
                    return
                
                textures['punch_sound'].play()
                Voxel(position = self.position + mouse.normal, texture = textures[block_pick])

            # break blocks
            if key == 'left mouse down':
                if (int(self.position.x) - int(player.position.x)) > 4:
                    return

                elif (int(self.position.z) - int(player.position.z)) > 4:
                    return

                textures['punch_sound'].play()
                destroy(self)

# sky object, looks bootiful :DDD
class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent = scene,
            model = 'sphere',
            texture = textures['sky_texture'],
            scale = 150,
            double_sided = True)

# hand object to make it look more like minecraft
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent = camera.ui,
            model = 'assets/objects/arm',
            texture = textures['arm_texture'],
            scale = 0.2,
            rotation = Vec3(150,-10,0),
            position = Vec2(0.4,-0.6))

    # hand working animation
    def active(self):
        self.position = Vec2(0.3,-0.5)

    # hand at rest animation
    def passive(self):
        self.position = Vec2(0.4,-0.6)

# object which displays current block in hand using a small icon
class CurrentBlockIcon(Entity):
    def __init__(self):
        super().__init__(
            parent = camera.ui,
            model = 'assets/objects/block',
            position = Vec2(-0.77,0.4),
            texture = textures[block_pick],
            scale = 0.050
        )

# world generation
for x in range(10):
    for z in range(10):
        # generate first layer as stone block
        Voxel(position = (x,0,z), texture=textures['stone_texture'])
        Voxel(position = (x*(-1),0,z*(-1)), texture=textures['stone_texture'])
        Voxel(position = (x*(-1),0,z), texture=textures['stone_texture'])
        Voxel(position = (x,0,z*(-1)), texture=textures['stone_texture'])

        for y in range(4):
            # generate the rest as dirt
            Voxel(position = (x,y + 1,z), texture=textures['dirt_texture'])
            Voxel(position = (x*(-1),y+1,z*(-1)), texture=textures['dirt_texture'])
            Voxel(position = (x,y+1,z*(-1)), texture=textures['dirt_texture'])
            Voxel(position = (x*(-1),y+1,z), texture=textures['dirt_texture'])

        # generate the topmost layer as grass blocks
        Voxel(position = (x,5,z), texture=textures['grass_texture'])
        Voxel(position = (x*(-1),5,z*(-1)), texture=textures['grass_texture'])
        Voxel(position = (x*(-1),5,z), texture=textures['grass_texture'])
        Voxel(position = (x,5,z*(-1)), texture=textures['grass_texture'])

# create a sky
sky = Sky()
# create a player hand on hud
hand = Hand()
# create block indicator icon
block_icon = CurrentBlockIcon()

# coordinates displayer
class CoordinatesCounter(Text):
    def __init__(self):
        super().__init__(
            x = 0.64,
            y = 0.5,
            text = "X: {} || Y: {} || Z: {}".format(
                int(player.position.x),
                int(player.position.y),
                int(player.position.z)
            )
        )

# this function creates trees on the surface. first ever object :D (makes stone and brick trees rn, leaf and log texture will be added later)
def genTree(position):
    for i in range(3):
        Voxel(
            position = (position, i + 6, position),
            texture = textures['brick_texture']
        )

    for x in range(3):
        for z in range(3):
            Voxel(position = (x + (position - 1), 9, z + (position - 1)), texture=textures['stone_texture'])

    Voxel(position = (position, 10, position), texture=textures['stone_texture'])

# generate random amount of trees on random coordinates
treeGenAmt = random.randint(2, 4)

for i in range(treeGenAmt):
    genTree(random.randint(-9, 9))
        
# enable coordinate displayer
cordsText = CoordinatesCounter()
# teleport player to ground so that thet player isnt stuck in ground
player.set_position((0.0, 5.0, 0.0))

#inventory
class Inventory(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent = camera.ui,
            model = Quad(radius=.015),
            texture = 'white_cube',
            texture_scale = (5,8),
            scale = (.5, .8),
            origin = (-.5, .5),
            position = (-.3,.4),
            color = color.color(0,0,.1,.9),
            )

        for key, value in kwargs.items():
            setattr(self, key, value)


    def find_free_spot(self):
        for y in range(8):
            for x in range(5):
                grid_positions = [(int(e.x*self.texture_scale[0]), int(e.y*self.texture_scale[1])) for e in self.children]
                print(grid_positions)

                if not (x,-y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y


    def append(self, item, x=0, y=0):
        print('add item:', item)

        if len(self.children) >= 5*8:
            print('inventory full')
            error_message = Text('<red>Inventory is full!', origin=(0,-1.5), x=-.5, scale=2)
            destroy(error_message, delay=1)
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent = self,
            model = 'quad',
            texture = item,
            color = color.white,
            scale_x = 1/self.texture_scale[0],
            scale_y = 1/self.texture_scale[1],
            origin = (-.5,.5),
            x = x * 1/self.texture_scale[0],
            y = -y * 1/self.texture_scale[1],
            z = -.5,
            )
        name = item.replace('_', ' ').title()

        if random.random() < .25:
            icon.color = color.gold
            name = '<orange>Rare ' + name

        icon.tooltip = Tooltip(name)
        icon.tooltip.background.color = color.color(0,0,0,.8)


        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01   # ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x/2)) * 5) / 5
            icon.y = int((icon.y - (icon.scale_y/2)) * 8) / 8
            icon.z += .01

            # if outside, return to original position
            if icon.x < 0 or icon.x >= 1 or icon.y > 0 or icon.y <= -1:
                icon.position = (icon.org_pos)
                return

            # if the spot is taken, swap positions
            for c in self.children:
                if c == icon:
                    continue

                if c.x == icon.x and c.y == icon.y:
                    print('swap positions')
                    c.position = icon.org_pos


        icon.drag = drag
        icon.drop = drop




if __name__ == '__main__':
    app = Ursina()
    inventory = Inventory()

    def add_item():
        inventory.append(random.choice(('bag', 'bow_arrow', 'gem', 'orb', 'sword')))

    add_item()
    add_item()
    add_item_button = Button(
        scale = (.1,.1),
        x = -.5,
        color = color.lime.tint(-.25),
        text = '+',
        tooltip = Tooltip('Add random item'),
        on_click = add_item
        )
    bg = Entity(parent=camera.ui, model='quad', texture='shore', scale_x=camera.aspect_ratio, z=1)
    Cursor(texture='cursor', scale=.1)
    mouse.visible = False

# start the game
app.run()
