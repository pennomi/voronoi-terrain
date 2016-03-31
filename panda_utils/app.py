"""A generic Panda3D class that handles all windowing, lifecycle management,
and input management, then passes the relevant triggers to a game state class.

Chances are in the future that this will also provide the game state switcher.
"""
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d import core
#from pandac.PandaModules import loadPrcFileData
from game.terrain import build_terrain

# Window config
#loadPrcFileData("", "window-title Test Game")
#loadPrcFileData("", "win-size 1200 900")


class MainApp(ShowBase):
    def __init__(self):
        # Normal init
        super(MainApp, self).__init__()
        self.taskMgr.add(self.update, "update")
        base.setFrameRateMeter(True)

        # Game-specific init
        build_terrain()

        # Input
        #base.disableMouse()
        #self.accept('mouse1', self.state.handle_mouse)

        # TODO: Move this to the appropriate gamestate
        self.build_lighting()

    def build_lighting(self):
        # Fog
        exp_fog = core.Fog("scene-wide-fog")
        exp_fog.setColor(0.0, 0.0, 0.0)
        exp_fog.setExpDensity(0.004)
        self.render.setFog(exp_fog)
        self.setBackgroundColor(0, 0, 0)

        # Lights
        spotlight = core.Spotlight("spotlight")
        spotlight.setColor(core.Vec4(1, 1, 1, 1))
        spotlight.setLens(core.PerspectiveLens())
        spotlight.setShadowCaster(True, 4096, 4096)
        spotlightNode = self.render.attachNewNode(spotlight)
        spotlightNode.setPos(10, 60, 50)
        spotlightNode.lookAt(5, 10, 0)
        self.render.setLight(spotlightNode)

        ambient_light = core.AmbientLight("ambientLight")
        ambient_light.setColor(core.Vec4(.75, .75, .75, 1))
        self.render.setLight(self.render.attachNewNode(ambient_light))

        # Enable the shader generator for the receiving nodes
        #self.render.setShaderAuto()

    def update(self, task):
        dt = self.taskMgr.globalClock.getDt()

        # Update camera
        base.cam.setPos(0, 0, 100)
        base.cam.lookAt(0, 0, 0)

        return Task.cont
