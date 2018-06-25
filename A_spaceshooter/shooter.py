import pyglet
import ecs

class RenderSystem(ecs.models.System):
    system_manager = None
    game_window = None
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager
        self.batch = pyglet.graphics.Batch()

    def update(self, dt):
        for entity, renderable in self.entity_manager.pairs_for_type(Renderable):
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
        for entity, controllable in self.entity_manager.pairs_for_type(Controllable):
            moveable = self.entity_manager.component_for_entity(entity, Moveable)

            if self.key_handler[pyglet.window.key.LEFT]:
                moveable.dx = -0.2
            elif self.key_handler[pyglet.window.key.RIGHT]:
                moveable.dx =  0.2
            else:
                moveable.dx =  0.0

            if self.key_handler[pyglet.window.key.UP]:
                moveable.dy =  0.2
            elif self.key_handler[pyglet.window.key.DOWN]:
                moveable.dy = -0.2
            else:
                moveable.dy =  0.0

class Locateable(ecs.models.Component):
    def __init__(self, x, y):
        self.x = x;
        self.y = y;

class Moveable(ecs.models.Component):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

class Controllable(ecs.models.Component):
    def __init__(self):
        pass

class Renderable(ecs.models.Component):
    def __init__(self,  filename, proportion_size):
        self.image = pyglet.resource.image(filename)
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.proportion_size = proportion_size
        self.sprite = pyglet.sprite.Sprite(img=self.image)


class Screen():
    def __init__(self):
        self.entity_manager = ecs.managers.EntityManager()
        self.system_manager = ecs.managers.SystemManager(self.entity_manager)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.render_system = RenderSystem(self.entity_manager)
        self.system_manager.add_system(self.render_system)

class ScreenManager():
    screen = None

    def __init__(self, game_window):
        self.game_window = game_window

    def draw(self):
        if self.screen is not None:
            self.screen.render_system.game_window = self.game_window
            self.screen.render_system.draw()

    def update(self, dt):
        if self.screen is not None:
            self.screen.render_system.game_window = self.game_window
            self.screen.system_manager.update(dt)


def create_player_ship_entity(entity_manager):
    entity = entity_manager.create_entity()
    entity_manager.add_component(entity, Locateable(0.05,0.5))
    entity_manager.add_component(entity, Renderable("playerShip1_blue.png", 0.05))
    entity_manager.add_component(entity, Moveable(0.0,0.0))
    entity_manager.add_component(entity, Controllable())
    return entity

def create_enemy_ship_entity(entity_manager):
    entity = entity_manager.create_entity()
    entity_manager.add_component(entity, Locateable(0.95,0.5))
    entity_manager.add_component(entity, Renderable("enemyBlack1.png", 0.05))
    entity_manager.add_component(entity, Moveable(-0.1, 0.0))
    return entity

def create_game_screen():
    screen = Screen()
    screen.system_manager.add_system(ControlSystem(screen.entity_manager, screen.key_handler))
    screen.system_manager.add_system(MoveSystem(screen.entity_manager))

    create_player_ship_entity(screen.entity_manager)
    create_enemy_ship_entity(screen.entity_manager)

    return screen

if __name__=="__main__":
    #pyglet.resource.path = ['./']
    #pyglet.resource.reindex()

    game_window = pyglet.window.Window(800,600)
    fps_display = pyglet.clock.ClockDisplay()

    screen_manager = ScreenManager(game_window)
    game_screen = create_game_screen()
    screen_manager.screen = game_screen

    #TODO only do this when a screen is "activated"
    game_window.push_handlers(game_screen.key_handler)

    @game_window.event
    def on_draw():
        game_window.clear()
        screen_manager.draw()
        fps_display.draw()

    pyglet.clock.schedule_interval(screen_manager.update, 1/120.0)
    pyglet.app.run()
