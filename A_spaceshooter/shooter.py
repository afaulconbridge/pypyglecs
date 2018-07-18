import pyglet
import ecs

class RenderSystem(ecs.models.System):
    system_manager = None
    game_window = None
    def __init__(self, entity_manager, game_window):
        self.entity_manager = entity_manager
        self.batch = pyglet.graphics.Batch()
        self.game_window = game_window

    def update(self, dt):
        for entity, renderable in self.entity_manager.pairs_for_type(SpriteRenderable):
            locateable = self.entity_manager.component_for_entity(entity, Locateable)
            if self.game_window is not None:
                #move it to the right location
                renderable.sprite.x = game_window.height*locateable.x
                renderable.sprite.y = game_window.height*locateable.y
                #scale it in case of resizing of sprite or window
                renderable.sprite.scale = (game_window.width*renderable.proportion_size) / renderable.image.width
                #ensure it is in the correct batch
                renderable.sprite.batch = self.batch
                #no need to draw it here, PyGlet will handle that
            else:
                print("trying to update a non game_window")
        for entity, renderable in self.entity_manager.pairs_for_type(TextRenderable):
            locateable = self.entity_manager.component_for_entity(entity, Locateable)
            if self.game_window is not None:
                #resize
                target_font_size = (game_window.height*renderable.proportion_size)
                if renderable.font_size != target_font_size:
                    renderable.label = pyglet.text.Label("Hello, world", font_size = target_font_size,
                        anchor_x='center', anchor_y='center')
                    renderable.font_size = target_font_size

                if renderable.label != None:
                    #move it to the right location
                    renderable.label.x = game_window.height*locateable.x
                    renderable.label.y = game_window.height*locateable.y
                    #ensure it is in the correct batch
                    renderable.label.batch = self.batch
                    #no need to draw it here, PyGlet will handle that
            else:
                print("trying to update a non game_window")

    def draw(self):
        self.batch.draw()

class MoveSystem(ecs.models.System):
    system_manager = None
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager

    def update(self, dt):
        for entity, moveable in self.entity_manager.pairs_for_type(Moveable):
            locateable = self.entity_manager.component_for_entity(entity, Locateable)
            locateable.x += moveable.dx * dt
            locateable.y += moveable.dy * dt

class ControlSystem(ecs.models.System):
    system_manager = None
    def __init__(self, entity_manager, key_handler):
        self.entity_manager = entity_manager
        self.key_handler = key_handler

    def update(self, dt):
        for entity, controllable in self.entity_manager.pairs_for_type(KeyHandleable):
            keyhandleable = self.entity_manager.component_for_entity(entity, KeyHandleable)
            keyhandleable.callback(keyhandleable, entity, self.entity_manager, self.key_handler)

class Locateable(ecs.models.Component):
    def __init__(self, x, y):
        self.x = x;
        self.y = y;

class Moveable(ecs.models.Component):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

class KeyHandleable(ecs.models.Component):
    def __init__(self, callback):
        self.callback = callback

class SpriteRenderable(ecs.models.Component):
    def __init__(self,  filename, proportion_size):
        self.image = pyglet.resource.image(filename)
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.proportion_size = proportion_size
        self.sprite = pyglet.sprite.Sprite(img=self.image)

class TextRenderable(ecs.models.Component):
    def __init__(self,  content, proportion_size):
        self.content = content
        self.label = None
        self.proportion_size = proportion_size
        self.font_size = None

def create_player_ship_entity(entity_manager):
    entity = entity_manager.create_entity()
    entity_manager.add_component(entity, Locateable(0.05,0.5))
    entity_manager.add_component(entity, SpriteRenderable("playerShip1_blue.png", 0.05))
    entity_manager.add_component(entity, Moveable(0.0,0.0))
    def player_callback(self, entity, entity_manager, key_handler):
        moveable = entity_manager.component_for_entity(entity, Moveable)

        if key_handler[pyglet.window.key.LEFT]:
            moveable.dx = -0.2
        elif key_handler[pyglet.window.key.RIGHT]:
            moveable.dx =  0.2
        else:
            moveable.dx =  0.0

        if key_handler[pyglet.window.key.UP]:
            moveable.dy =  0.2
        elif key_handler[pyglet.window.key.DOWN]:
            moveable.dy = -0.2
        else:
            moveable.dy =  0.0
    entity_manager.add_component(entity, KeyHandleable(player_callback))
    return entity

def create_enemy_ship_entity(entity_manager):
    entity = entity_manager.create_entity()
    entity_manager.add_component(entity, Locateable(0.95,0.5))
    entity_manager.add_component(entity, SpriteRenderable("enemyBlack1.png", 0.05))
    entity_manager.add_component(entity, Moveable(-0.1, 0.0))
    return entity

def create_start_button(entity_manager):
    entity = entity_manager.create_entity()
    entity_manager.add_component(entity, Locateable(0.5,0.5))
    entity_manager.add_component(entity, SpriteRenderable("blue_sliderRight.png", 0.05))
    return entity

if __name__=="__main__":
    #pyglet.resource.path = ['./']
    #pyglet.resource.reindex()

    game_window = pyglet.window.Window(800,600)
    fps_display = pyglet.clock.ClockDisplay()
    key_handler = pyglet.window.key.KeyStateHandler()
    game_window.push_handlers(key_handler)

    entity_manager = ecs.managers.EntityManager()
    system_manager = ecs.managers.SystemManager(entity_manager)

    render_system = RenderSystem(entity_manager, game_window)
    system_manager.add_system(render_system)

    control_system = ControlSystem(entity_manager, key_handler)
    system_manager.add_system(control_system)

    system_manager.add_system(MoveSystem(entity_manager))

    @game_window.event
    def on_draw():
        game_window.clear()
        render_system.draw()
        fps_display.draw()

    pyglet.clock.schedule_interval(system_manager.update, 1/120.0)

    #create initial screen
    create_player_ship_entity(entity_manager)
    create_enemy_ship_entity(entity_manager)
    #create_start_button(entity_manager)

    pyglet.app.run()
