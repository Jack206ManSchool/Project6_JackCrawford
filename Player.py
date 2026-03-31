from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Object, Missile
from panda3d.core import SamplerState

from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from panda3d.core import AntialiasAttrib

from panda3d.core import CollisionHandlerEvent
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
# Regex module import for string editing.
import re

from panda3d.core import CollisionTraverser

class Spaceship(SphereCollideObject):

    # Initialises Spaceship/Hero Class
    def __init__(self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], 
                 modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, 
                 scaleVec: float, traverser: CollisionTraverser):

        super().__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 1)

        self.taskManager = taskMgr
        self.accept = accept
        self.loader = loader
        # Turns modelNode into a list so I can pass by reference
        self.a = [self.modelNode]
        
        Object.selflessInit(loader, nodeName, texPath, posVec, scaleVec, self.a)

        self.shipThrustSpeed = 5
        self.shipTurnRate = 0.5

        # Runs function to set player input keys
        self.setKeyBindings()

        self.reloadTime = .25
        self.missileDistance = 4000 # Until the missile explodes.
        self.missileBay = 1 # Only one missile in the missile bay to be launched.

        self.cntExplode = 0
        self.explodeIntervals = {}

        self.taskManager.add(self.CheckIntervals, 'checkMissiles', 34)

        self.traverser = traverser

        self.handler = CollisionHandlerEvent()

        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)

        self.EnableHUD()

    def setKeyBindings(self):
        """ All of our keybindings for our ship's movement """

        # Forward movement
        self.accept('space', self.Thrust, [1])
        self.accept('space-up', self.Thrust, [0])

        self.accept('r', self.thrustRate, [1])
        self.accept('r-up', self.thrustRate, [0])

        self.accept('g', self.turnRate, [1])
        self.accept('g-up', self.turnRate, [0])

        # Left-Right turning
        self.accept('a', self.leftTurn, [1])
        self.accept('a-up', self.leftTurn, [0])
        self.accept('d', self.rightTurn, [1])
        self.accept('d-up', self.rightTurn, [0])

        # Left-Right rotation
        self.accept('q', self.leftRot, [1])
        self.accept('q-up', self.leftRot, [0])
        self.accept('e', self.rightRot, [1])
        self.accept('e-up', self.rightRot, [0])

        # Up-Down turning
        self.accept('w', self.upTurn, [1])
        self.accept('w-up', self.upTurn, [0])
        self.accept('s', self.downTurn, [1])
        self.accept('s-up', self.downTurn, [0])

        self.accept('f', self.Fire)

    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            # The direction the spaceship is facing.
            aim = self.a[0].getParent().getRelativeVector(self.modelNode, Vec3.down())
            # Normalizing the vector makes it consistantly consistant
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = "Missile" + str(Missile.missileCount)
            # Spawn the missile in front of the nose of the ship
            posVec = self.modelNode.getPos() + inFront
            currentMissile = Missile(self.loader, "Assets/Phaser/phaser.egg", 
                                     self.a[0].getParent(), 
                                     tag, posVec, 4.0)
            
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)
            
            # Take Note:
            # "fluid = 1" will make the collision be checked between the last interval
            # and this interval to make sure there's nothing in-between both checks
            # that wasn't hit
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, 
                                                        startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
        else:
            # if we aren't reloading, start reloading
            if not self.taskManager.hasTaskNamed('reload'):
                print("Initializing reload...")
                # Call the reload method on no delay
                self.taskManager.doMethodLater(0, self.Reload, 'reload')
                return Task.cont

    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        print("fromNode: " + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)
        intoPosition = Vec3(entry.getSurfacePoint(self.modelNode.getParent()))

        tempVar = fromNode.split("_")
        print("tempVar: " + str(tempVar))
        shooter = tempVar[0]
        print("Shooter: " + str(shooter))
        tempVar = intoNode.split('-')
        print("TempVar1: " + str(tempVar))
        tempVar = intoNode.split('_')
        print("TempVar2: " + str(tempVar))
        victim = tempVar[0]
        print("Victim: " + str(victim))

        pattern = r"[0-9]"
        strippedString = re.sub(pattern, '', victim)

        if(strippedString == "Drone" or strippedString == "Planet" or 
           strippedString =="Space Station"):
            print(victim, 'hit at', intoPosition)
            self.ObjectDestroy(victim, intoPosition)

        print(shooter + ' is DONE.')
        Missile.Intervals[shooter].finish()

    def ObjectDestroy(self, hitID, hitPosition):
        self.SetParticles()
        # Unity also has a find method
        nodeID = self.modelNode.getParent().find(hitID)
        nodeID.detachNode()

        # Start the explosion
        self.explodeNode.setPos(hitPosition)
        self.Explode()

    def Explode(self):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration = 4.0)
        self.explodeIntervals[tag].start()

    def ExplodeLight(self, t):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()
        
        elif t == 0:
            self.explodeEffect.start(self.explodeNode)
    
    def SetParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect("Assets/ParticleEffects/Explosions/basic_xpld_efx.ptf")
        self.explodeEffect.loadConfig("Assets/Particles/basic_xpld_efx.ptf")
        self.explodeEffect.setScale(20)
        self.explodeNode = self.modelNode.getParent().attachNewNode("ExplosionEffect")

    def CheckIntervals(self, task):
        for I in Missile.Intervals:
            # IsPlaying returns true or false to see if the missile has gotten to the
            # end of it's path.
            if not Missile.Intervals[I].isPlaying():
                # If its path is done, we get rid of everything to do with that missile.
                Missile.cNodes[I].detachNode()
                Missile.fireModels[I].detachNode()
                del Missile.Intervals[I]
                del Missile.fireModels[I]
                del Missile.cNodes[I]
                del Missile.collisionSolids[I]
                print(I + ' has reached the end of its fire solution.')
                # Take Note:
                # We break because when things are deleted from a dictionary, we have to refactor
                # the dictionary so we can use it. This is because when we delete things, 
                # there's a gap at that point.
                break
        return Task.cont

    def Reload(self, task):
        if task.time > self.reloadTime:
            print("Added to missile bay.")
            self.missileBay += 1
        if(self.missileBay > 1):
            self.missileBay = 1
            print("Reload complete.")
            return Task.done
        elif task.time <= self.reloadTime:
            print("Reload proceeding...")
            return Task.cont

    def EnableHUD(self):
        """ Draws the HUD onto the screen """
        self.Hud = OnscreenImage(image = "Assets/Hud/CrosshairLowResThick.png", pos = Vec3(0, 0, 0), scale = 0.125)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)
        self.Hud = self.Hud.getTexture()
        self.Hud.setMagfilter(SamplerState.FT_nearest)

    def Thrust(self, keyDown):
        """ Adds tasks that moves the ship forward """
        if keyDown:
            self.taskManager.add(self.ApplyThrust, "forward-thrust")
        else:
            self.taskManager.remove("forward-thrust")

    def ApplyThrust(self, task):
        """ Moves the ship forward """

        trajectory = self.returnDown()

        self.modelNode.setFluidPos((self.modelNode.getPos() + trajectory * self.shipThrustSpeed))

        return Task.cont

    def thrustRate(self, keyDown):
        """ Adds tasks that change the ship speed """
        if keyDown:
            self.shipThrustSpeed = 20
        else:
            self.shipThrustSpeed = 5

    def turnRate(self, keyDown):
        """ Adds tasks that change the ships rotation """
        if keyDown:
            self.shipTurnRate = 0.20
        else:
            self.shipTurnRate = 0.5

    def leftTurn(self, keyDown):
        """ Adds tasks that turn the ship left """
        if keyDown:
            self.taskManager.add(self.applyLeftTurn, 'left-turn')
        else:
            self.taskManager.remove('left-turn')

    def applyLeftTurn(self, keyDown):
        """ Turns the ship left """
        rate = self.shipTurnRate
        self.modelNode.setR(self.modelNode, rate)
        return Task.cont

    def rightTurn(self, keyDown):
        """ Adds tasks that turn the ship right """
        if keyDown:
            self.taskManager.add(self.applyRightTurn, 'right-turn')
        else:
            self.taskManager.remove('right-turn')

    def applyRightTurn(self, keyDown):
        """ Turns the ship right """
        rate = -self.shipTurnRate
        self.modelNode.setR(self.modelNode, rate)
        return Task.cont

    # Functions for getting the ship's relative vectors
    def returnForward(self):
        ut = self.modelNode.getParent().getRelativeVector(self.modelNode, Vec3.forward())
        ut.normalize()
        return ut
    def returnBackward(self):
        dt = self.modelNode.getParent().getRelativeVector(self.modelNode, Vec3.backward())
        dt.normalize()
        return dt
    def returnUp(self):
        ut = self.modelNode.getParent().getRelativeVector(self.modelNode, Vec3.up())
        ut.normalize()
        return ut
    def returnDown(self):
        dt = self.modelNode.getParent().getRelativeVector(self.modelNode, Vec3.down())
        dt.normalize()
        return dt
    def returnLeft(self):
        lt = self.modelNode.getParent().getRelativeVector(self.modelNode, Vec3.left())
        lt.normalize()
        return lt
    def returnRight(self):
        rt = self.modelNode.getParent().getRelativeVector(self.modelNode, Vec3.right())
        rt.normalize()
        return rt

    def upTurn(self, keyDown):
        """ Adds tasks that turn the ship up """
        if keyDown:
            self.taskManager.add(self.applyUpTurn, 'up-turn')
        else:
            self.taskManager.remove('up-turn')

    def applyUpTurn(self, keyDown):
        """ Turns the ship upward """
        rate = self.shipTurnRate
        self.modelNode.setP(self.modelNode, rate)
        return Task.cont

    def downTurn(self, keyDown):
        """ Adds tasks that turn the ship down """
        if keyDown:
            self.taskManager.add(self.applyDownTurn, 'down-turn')
        else:
            self.taskManager.remove('down-turn')

    def applyDownTurn(self, keyDown):
        """ Turns the ship downward """
        rate = -self.shipTurnRate
        self.modelNode.setP(self.modelNode, rate)
        return Task.cont 
    
    def leftRot(self, keyDown):
        """ Adds tasks that rotate the ship left """
        if keyDown:
            self.taskManager.add(self.applyLeftRot, 'left-Rot')
        else:
            self.taskManager.remove('left-Rot')

    def applyLeftRot(self, keyDown):
        """ Rotates the ship left """
        rate = self.shipTurnRate
        self.modelNode.setH(self.modelNode, rate)
        return Task.cont

    def rightRot(self, keyDown):
        """ Adds tasks that rotate the ship right """
        if keyDown:
            self.taskManager.add(self.applyRightRot, 'right-Rot')
        else:
            self.taskManager.remove('right-Rot')

    def applyRightRot(self, keyDown):
        """ Rotates the ship right """
        rate = -self.shipTurnRate
        self.modelNode.setH(self.modelNode, rate)
        return Task.cont