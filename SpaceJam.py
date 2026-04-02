from direct.showbase.ShowBase import ShowBase

from panda3d.core import Vec3
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from panda3d.core import SamplerState

import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
import Player as playerClasses

from panda3d.core import TextNode

# Universe Color Keys
# Blue = 1
# Green = 2
# Purple = 3
# Red = 4

# Push "V" to toggle between first and third person
# Hold "R" to speed up
# Hold "G" for precise aimming

class SpJm(ShowBase):

    def __init__(self):

        ShowBase.__init__(self)

        # Toggles if you see the Debug Axis Arrows 
        # (or I guess lines of circles in this case)
        renderDebugAxis = False

        # Toggles being in first or third person
        self.viewMode = True

        self.cTrav = CollisionTraverser()
        self.cTrav.traverse(self.render)

        # Creates game objects
        self.SetScene()

        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.Hero.collisionNode, self.Hero.modelNode)
        self.cTrav.addCollider(self.Hero.collisionNode, self.pusher)

        self.cTrav.showCollisions(self.render)

        # If true, create the Debug Axis Arrows        
        if renderDebugAxis == True:
            # Calls drawDebugAxis and sets DebugAxis to the created objects 
            self.DebugAxis = self.drawDebugAxis()

        # Sets amount of drones to create per planet
        fullCycle = 60

        # Creates drones
        for j in range(fullCycle):
            nickName = self.droneNumberUpdate()
            self.drawCloudDefense(self.SpaceStation1, nickName, 1250)
        for j in range(fullCycle):
            nickName = self.droneNumberUpdate()
            self.drawBaseballSeams(self.Planet1, nickName, j, fullCycle, 2)
        for j in range(fullCycle):
            nickName = self.droneNumberUpdate()
            self.drawCircleX(self.Planet4, nickName, j, fullCycle, 3)
        for j in range(fullCycle):       
            nickName = self.droneNumberUpdate()
            self.drawCircleY(self.Planet5, nickName, j, fullCycle, 1)
        for j in range(fullCycle):           
            nickName = self.droneNumberUpdate()
            self.drawCircleZ(self.Planet6, nickName, j, fullCycle, 3)

        self.menuSetCamera()

        self.accept('enter', self.initPart2)

    def initPart2(self):

        self.titleTextNode.detachNode()
        self.startTextNode.detachNode()
        self.cornerTextNode.detachNode()

        # Sets up camera
        self.heroSetCamera()
        print(self.Hero.modelNode.getPos())
  
        # Sets the input keys 1, 2, 3, 4 to change the universe skybox
        self.accept("1", self.UniverseBlue)
        self.accept("2", self.UniverseGreen)
        self.accept("3", self.UniversePurple)
        self.accept("4", self.UniverseRed)

        # Sets input for changing viewmode
        self.accept('v', self.changeView)

        # Runs function to set player input keys
        self.Hero.setKeyBindings()
        self.Hero.EnableHUD()

    def menuSetCamera(self):
        """ Prepares Camera for use on the Menu """
        self.disableMouse()
        self.camera.reparentTo(self.Menu.modelNode)
        self.Menu.modelNode.setHpr(-90, 0, -90)
        self.Menu.modelNode.setFluidPos(self.Menu.modelNode.getPos() + Vec3(-340, 0, 900))
        self.camera.setH(self.camera, 65)

        titleText = TextNode("Title")
        titleText.setText("ABRASIVE!!!!!!!!!!!!!\n!!!!!!!!!!")
        self.titleTextNode = self.render2d.attach_new_node(titleText)
        self.titleTextNode.set_scale(0.125)
        self.titleTextNode.set_pos(-1, 0, 0.9)

        startText = TextNode("Start")
        startText.setText('!"!"!"ENTER!"!"!"!"!\nComme\nnces!')
        startText.set_align(TextNode.A_center)
        self.startTextNode = self.render2d.attach_new_node(startText)
        self.startTextNode.set_scale(0.04)

        cornerText = TextNode("Corner")
        cornerText.setText(  'S\n' \
                            ' PJ\n' \
                            '  AAP\n' \
                            '   CMR\n' \
                            '    E  O\n' \
                            '        T\n' \
                            '         OOOOOOOOOOOOOOOOO\n' \
                            '          OOOOOOOOOOOOOOOOO\n'
                            '       OOOOOOOOOOOOOOOOO\n')
        self.cornerTextNode = self.render2d.attach_new_node(cornerText)
        self.cornerTextNode.set_scale(0.04)
        self.cornerTextNode.set_pos(0.8, 0, -0.675)

    def heroSetCamera(self):
        """ Prepares Camera for use on the Player """
        self.disableMouse()
        self.camera.reparentTo(self.Hero.modelNode)
        self.camera.setFluidPos(0.325, 0, -0.35)
        self.camera.setHpr(0, 270, 0)

    def droneNumberUpdate(self):
        """# Makes sure each planet's drone has unique IDS"""
        spaceJamClasses.Drone.droneCount += 1
        return "Drone" + str(spaceJamClasses.Drone.droneCount)

    def SetScene(self):
        """Creates all game objects for the scene"""

        self.Menu = spaceJamClasses.Object(self.loader, "Assets/Spaceships/Dumbledore.x", 
                                              self.render, "Menu", "Assets/Planets/Planet6.png", 
                                              (-1415.74, -225.423, -672.359), 25)

        # Creates Skybox / Universe
        self.Universe = spaceJamClasses.Universe(self.loader, "Assets/Universe/Universe.x", self.render, 
                                 "Universe", "Assets/Universe/UniverseBlue.png", (0, 0, 0), 15000)

        # Creates Planets 1-6
        self.Planet1 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", 
                                              self.render, "Planet1", "Assets/Planets/Planet1.png", 
                                              (5000, 0, 0), 350)
        self.Planet2 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", 
                                              self.render, "Planet2", "Assets/Planets/Planet2.png", 
                                              (0, 5000, 0), 450)
        self.Planet3 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", 
                                              self.render, "Planet3", "Assets/Planets/Planet3.png", 
                                              (0, 0, 5000), 250)
        self.Planet4 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", 
                                              self.render, "Planet4", "Assets/Planets/Planet4.png", 
                                              (-5000, 0, 0), 550)
        self.Planet5 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", 
                                              self.render, "Planet5", "Assets/Planets/Planet5.png", 
                                              (0, -5000, 0), 150)
        self.Planet6 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", 
                                              self.render, "Planet6", "Assets/Planets/Planet6.png", 
                                              (0, 0, -5000), 650)

        # Creates Space Station
        self.SpaceStation1 = spaceJamClasses.SpaceStation(self.loader, 
                                                        "Assets/Space Station/spaceStation.x", 
                                                        self.render, "Space Station", 
                                                        "Assets/Space Station/SpaceStation1_Dif2.png", 
                                                        (0, 0, 0), 75)
        # Creates Spaceship/Player
        self.Hero = playerClasses.Spaceship(self.loader, self.taskMgr, self.accept,
                                                        "Assets/Spaceships/Dumbledore.x", 
                                                        self.render, "Hero", 
                                                        "Assets/Spaceships/spacejet_C.png", 
                                                        (-1050, -212, -700), 75, self.cTrav)
        
    def changeView(self):
        """ Sets camera to be first person or third person """
        if(self.viewMode):
            self.viewMode = False
            self.camera.setFluidPos(0.325, 0, 10)
        else:
            self.viewMode = True
            self.camera.setFluidPos(0.325, 0, -0.35)

    def drawDebugAxis(self):
        """ Creates Debug Axis Lines/Guide """
        # Creates "da" array, adds first debug circle to origin
        da = [self.debugCircle((0, 0, 0), (1.0, 1.0, 1.0, 1.0), "DebugCenterAxis"), [], [], []]

        # Defines "axis" at 250
        axis = 250
        
        # Creates colored spheres in each positive axis, the color reparenting each axis
        # Red = X
        # Yellow = Y
        # Blue = Z
        for i in range(7):
            da[1].append(self.debugCircle((axis, 0, 0), (1.0, 0.0, 0.0, 1.0), f"DebugXAxis{i}"))
            da[2].append(self.debugCircle((0, axis, 0), (1.0, 1.0, 0.0, 1.0), f"DebugYAxis{i}"))
            da[3].append(self.debugCircle((0, 0, axis), (0.0, 0.0, 1.0, 1.0), f"DebugZAxis{i}"))
            axis += 250
        
        # Returns 'da' array
        return da

    def debugCircle(self, pos, color, name):
        """ Creates a Circle Object for 'drawDebugAxis', Returns Result. 
        \n Pos = Position (x, y, z)
        \n Color = Color (RGBA)
        \n Name = Object Name """
        dc = spaceJamClasses.Object(self.loader, "Assets/Planets/protoPlanet.x", self.render, 
                               name, "Assets/UI/ReticleIV.jpg", pos, 75)
        dc.modelNode.setColorScale(color)
        return dc

    def drawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        """ Creates a Baseball Seam Drone Formation """
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        self.droneify(unitVec, centralObject, droneName, radius)

    def drawCloudDefense(self, centralObject, droneName, scale):
        """ Creates a Cloud Frone Formation """
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * scale + centralObject.modelNode.getPos()

        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render,
                              droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 10)

    def drawCircleX(self, centralObject, droneName, step, numSeams, radius = 1):
        """ Creates a circular drone formation along the X axis """
        unitVec = defensePaths.Circle(step, numSeams, 'X')
        self.droneify(unitVec, centralObject, droneName, radius)

    def drawCircleY(self, centralObject, droneName, step, numSeams, radius = 1):
        """ Creates a circular drone formation along the Y axis """
        unitVec = defensePaths.Circle(step, numSeams, 'Y')
        self.droneify(unitVec, centralObject, droneName, radius)
    
    def drawCircleZ(self, centralObject, droneName, step, numSeams, radius = 1):
        """ Creates a circular drone formation along the Z axis """
        unitVec = defensePaths.Circle(step, numSeams, 'Z')
        self.droneify(unitVec, centralObject, droneName, radius)

    def droneify(self, unitV, cenO, dn, rad):
        """ Creates drones for some formation functions
        \n unitV = unitVec
        \n cenO = Central Object
        \n dn = droneName
        \n rad = radius """
        unitV.normalize()
        position = unitV * rad * 250 + cenO.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render,
                              dn, "Assets/DroneDefender/octotoad1_auv.png", position, 5)
        
    def UniverseColor(self, color):
        """Sets Universe Color/Texture
        \n Color: Color Name (string) 
        \n \t Example: ''Blue'' """
        # Loads universe texture from Assets folder based on provided color
        tex = self.loader.loadTexture(f"Assets/Universe/Universe{color}.png")
        # Disables texture filtering (for that low-res look!)
        tex.setMagfilter(SamplerState.FT_nearest)
        # Sets object Texture to tex
        self.Universe.modelNode.setTexture(tex, 1)

    # Functions that call "UniverseColor" to change the Universe's texture 
    def UniverseBlue(self):
        self.UniverseColor("Blue")
    def UniverseGreen(self):
        self.UniverseColor("Green")
    def UniversePurple(self):
        self.UniverseColor("Purple")
    def UniverseRed(self):
        self.UniverseColor("Red")

# Sets app to SpJm, runs SpJm
app = SpJm()
app.run()
