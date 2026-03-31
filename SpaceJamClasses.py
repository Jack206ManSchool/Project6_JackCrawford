from direct.showbase.ShowBase import ShowBase
from direct.showbase.Loader import Loader
from direct.task import Task
from panda3d.core import SamplerState
from panda3d.core import Vec3
from panda3d.core import NodePath

from panda3d.core import *

from CollideObjectBase import *

class Object(ShowBase):

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, 
                texPath: str, posVec: Vec3, scaleVec: float, rotVec = (0, 0, 0)):

        # Creates object and gives it a model.
        self.modelNode = loader.loadModel(modelPath)
        # Adds object to renderer
        self.modelNode.reparentTo(parentNode)
        # Sets Object Position
        self.modelNode.setPos(posVec)
        # Sets Object Rotation (Optional)
        self.modelNode.setHpr(rotVec)
        # Sets Object Scale
        self.modelNode.setScale(scaleVec)
        # Set Node Name
        self.modelNode.setName(nodeName)

        # Loads texture from Assets folder
        tex = loader.loadTexture(texPath)
        # Disables texture filtering (for that low-res look!)
        tex.setMagfilter(SamplerState.FT_nearest)
        # Sets object Texture to objTex
        self.modelNode.setTexture(tex, 1)

    def selflessInit(loader: Loader, nodeName: str, 
        texPath: str, posVec: Vec3, scaleVec: float, modelNode):
        """ Re-adds some object refactoring after changing objects to collision classes"""
        modelNode[0].setPos(posVec)
        modelNode[0].setScale(scaleVec)
        modelNode[0].setName(nodeName)

        tex = loader.loadTexture(texPath)
        tex.setMagfilter(SamplerState.FT_nearest)
        modelNode[0].setTexture(tex, 1)

class Drone(SphereCollideObject):
    """Drone Object"""

    droneCount = 0

    # Initialises Drone Class
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, 
        texPath: str, posVec: Vec3, scaleVec: float):

        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.5)
        
        # Turns modelNode into a list so I can pass by reference
        a = [self.modelNode]

        Object.selflessInit(loader, nodeName, texPath, posVec, scaleVec, a)

class Missile(SphereCollideObject):

    fireModels = {}
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0

    # Initialises Missiles
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, 
        posVec: Vec3, scaleVec: float):

        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.0)
        
        # Turns modelNode into a list so I can pass by reference
        a = [self.modelNode]
        Object.selflessInit(loader, nodeName, "Assets/Phaser/phaserII.jpg", posVec, scaleVec, a)

        Missile.missileCount += 1

        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode

        # Retrieve the solids for our collisionNode.
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        self.cNodes[nodeName].show()

        print("Fire torpedo #" + str(Missile.missileCount))







class Planet(SphereCollideObject):
    """Planet Object"""

    # Initialises Planet Class
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, 
        texPath: str, posVec: Vec3, scaleVec: float):

        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1.1)
        
        # Turns modelNode into a list so I can pass by reference
        a = [self.modelNode]
        
        Object.selflessInit(loader, nodeName, texPath, posVec, scaleVec, a)

class Universe(InverseSphereCollideObject):
    """Universe Object"""

    # Initialises Universe Class
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, 
        texPath: str, posVec: Vec3, scaleVec: float):
        super(Universe, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 0.9)
        
        # Turns modelNode into a list so I can pass by reference
        a = [self.modelNode]
        
        Object.selflessInit(loader, nodeName, texPath, posVec, scaleVec, a)

class SpaceStation(CapsuleCollidableObject):
    """Space Station Object"""

    # Initialises Space Station Class
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, 
        texPath: str, posVec: Vec3, scaleVec: float):

        super(SpaceStation, self).__init__(loader, modelPath, parentNode, nodeName, 
                                           1, -1, 5, 1, -1, -5, 10)

        # Turns modelNode into a list so I can pass by reference
        a = [self.modelNode]
        
        Object.selflessInit(loader, nodeName, texPath, posVec, scaleVec, a)
