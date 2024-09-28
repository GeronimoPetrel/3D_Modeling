import wx
from wx.glcanvas import GLCanvas
from OpenGL.GL import *
from OpenGL.GLU import *
import keyboard
import math

# Initialize rotation variables
rotation_x_angle, rotation_y_angle, rotation_z_angle = 1, 0, 0
rotate_figure = False
current_axis = 'x'  # To track which axis is currently being rotated
rotate_direction = 1
figure = 0


class OpenGLCanvas(GLCanvas):
    def __init__(self, parent):
        attrib_list = [wx.glcanvas.WX_GL_RGBA, wx.glcanvas.WX_GL_DOUBLEBUFFER, wx.glcanvas.WX_GL_DEPTH_SIZE, 16, 0]
        GLCanvas.__init__(self, parent, -1, attribList=attrib_list)
        self.context = wx.glcanvas.GLContext(self)

        # Bind events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

        # Timer to continuously redraw the scene
        self.timer = wx.Timer(self)
        self.timer.Start(10)  # Set to 10 ms for a smooth update

        self.init = False  # To handle OpenGL initialization

    def InitGL(self):
        """One-time GL setup."""
        glEnable(GL_DEPTH_TEST)  # Enable depth testing
        glClearColor(0.1, 0.1, 0.1, 1.0)  # Set a gray background

        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.GetSize().width / self.GetSize().height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)  # Move back to see the object

        self.init = True

    def OnPaint(self, event):
        self.SetCurrent(self.context)

        if not self.init:
            self.InitGL()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.select_figure()
        self.SwapBuffers()

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.IsShown():
            self.SetCurrent(self.context)
            glViewport(0, 0, size.width, size.height)
        event.Skip()

    def OnTimer(self, event):
        global rotate_figure, current_axis
        '''
        # Check if 'A' is pressed to enable cube rotation
        if keyboard.is_pressed('a'):
            rotate_figure = True
        else:
            rotate_figure = False
        '''

        # Select the axis of rotation based on key presses
        if keyboard.is_pressed('x'):
            current_axis = 'x'
        elif keyboard.is_pressed('y'):
            current_axis = 'y'
        elif keyboard.is_pressed('z'):
            current_axis = 'z'

        self.Refresh(False)  # Trigger a repaint
        
    

    def draw_pyramid(self):

        self.rotation_function()

        # Define vertices for the pyramid
        vertices = [
            # Base
            -1.0, -1.0, -1.0,  # Vertex 0
            1.0, -1.0, -1.0,  # Vertex 1
            1.0, -1.0,  1.0,  # Vertex 2
            -1.0, -1.0,  1.0,  # Vertex 3
            0.0,  1.0,  0.0   # Apex (Vertex 4)
        ]

        # Define the edges of the pyramid
        edges = [
            # Base edges
            (0, 1), (1, 2), (2, 3), (3, 0),
            # Side edges
            (0, 4), (1, 4), (2, 4), (3, 4)
        ]

        # Draw the pyramid
        glBegin(GL_LINES)
        glColor3f(1, 1, 1)  # White color
        for edge in edges:
            for vertex in edge:
                glVertex3f(vertices[vertex * 3], vertices[vertex * 3 + 1], vertices[vertex * 3 + 2])


        glEnd()
        

    def draw_sphere(self):

        self.rotation_function()

        # Define the sphere parameters
        radius = 1.0
        slices = 32
        stacks = 16
        
        # Create a new quadric object
        quadric = gluNewQuadric()
        
        # Set the draw style
        gluQuadricDrawStyle(quadric, GL_LINE)  # Use GL_LINE for a wireframe sphere
        
        # Draw the sphere
        gluSphere(quadric, radius, slices, stacks)
        
        # Clean up
        gluDeleteQuadric(quadric)

    def draw_cylinder(self):

        self.rotation_function()

        radius = 1.0
        height = 2.0
        slices = 32

        # Define vertices for the cylinder
        vertices = []
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            vertices.extend([x, -height / 2, z])  # Bottom circle
            vertices.extend([x, height / 2, z])   # Top circle

        # Define edges of the cylinder
        edges = []
        for i in range(slices):
            # Bottom circle edges
            edges.append((i * 2, ((i + 1) % slices) * 2))
            # Top circle edges
            edges.append((i * 2 + 1, ((i + 1) % slices) * 2 + 1))
            # Vertical edges
            edges.append((i * 2, i * 2 + 1))

        # Draw the cylinder
        glBegin(GL_LINES)
        glColor3f(1, 1, 1)  # White color
        for edge in edges:
            for vertex in edge:
                glVertex3f(vertices[vertex * 3], vertices[vertex * 3 + 1], vertices[vertex * 3 + 2])
        glEnd()

    def rotation_function(self):

        global rotation_x_angle, rotate_direction, rotation_y_angle, rotation_z_angle, rotate_figure, current_axis

        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5)  # Move back to see the object

        # Apply the cumulative rotation based on the stored angles
        glRotatef(rotation_x_angle, 1, 0, 0)
        glRotatef(rotation_y_angle, 0, 1, 0)
        glRotatef(rotation_z_angle, 0, 0, 1)

        # Update the current axis's rotation angle when 'A' is pressed
        if rotate_figure and current_axis == 'x':
            rotation_x_angle += (rotate_direction)
        elif rotate_figure and current_axis == 'y':
            rotation_y_angle += (rotate_direction)
        elif rotate_figure and current_axis == 'z':
            rotation_z_angle += (rotate_direction)
        
        if abs(rotate_direction) != 1:
            rotate_figure = False # determines if continous rotation is desired

    def draw_cube(self):

        self.rotation_function()

        # Define vertices and edges of the cube
        vertices = [
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],  # Front face
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]  # Back face
        ]
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        # Draw the cube
        glBegin(GL_LINES)
        glColor3f(1, 1, 1)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

    def select_figure(self):
        
        global figure

        if keyboard.is_pressed('1'):
            figure = 1
            
        elif keyboard.is_pressed('2'): 
            figure = 2
        
        elif keyboard.is_pressed('3'):
            figure = 3
        
        elif keyboard.is_pressed('5'):
            figure = 5

        elif keyboard.is_pressed('0'): 
            figure = 0

        if figure == 1:
            self.draw_pyramid()
            
        elif figure == 2:
            self.draw_cube()

        elif figure == 3:
            self.draw_sphere()
        
        elif figure == 5:
            self.draw_cylinder()


class MyFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "wxPython with OpenGL", size=(800, 600))

        # Create main panel for layout management
        main_panel = wx.Panel(self)

        # Create the OpenGL canvas
        self.canvas = OpenGLCanvas(main_panel)

        # Create nine buttons for the first panel
        button1 = wx.Button(main_panel, label="Button 1")
        button2 = wx.Button(main_panel, label="Button 2")
        button3 = wx.Button(main_panel, label="Button 3")
        button4 = wx.Button(main_panel, label="Button 4")
        
        # Buttons <<, <, >, >> will have smaller size
        button5 = wx.Button(main_panel, label=">>")
        button6 = wx.Button(main_panel, label="<<")
        button8 = wx.Button(main_panel, label=">")
        button7 = wx.Button(main_panel, label="<")
        button9 = wx.Button(main_panel, label="Button 9")

        # Set smaller size for buttons <<, <, >, >>
        small_button_size = (30, 30)  # Set a smaller size for these buttons
        button5.SetMinSize(small_button_size)
        button6.SetMinSize(small_button_size)
        button7.SetMinSize(small_button_size)
        button8.SetMinSize(small_button_size)

        # Bind button events for the first panel
        button1.Bind(wx.EVT_BUTTON, self.on_button1_click)
        button2.Bind(wx.EVT_BUTTON, self.on_button2_click)
        button3.Bind(wx.EVT_BUTTON, self.on_button3_click)
        button4.Bind(wx.EVT_BUTTON, self.on_button4_click)
        button5.Bind(wx.EVT_BUTTON, self.on_button5_click)
        button6.Bind(wx.EVT_BUTTON, self.on_button6_click)
        button7.Bind(wx.EVT_BUTTON, self.on_button7_click)
        button8.Bind(wx.EVT_BUTTON, self.on_button8_click)
        button9.Bind(wx.EVT_BUTTON, self.on_button9_click)

        # Create a vertical box sizer for buttons 1-9
        vbox_buttons_1_to_9 = wx.BoxSizer(wx.VERTICAL)
        vbox_buttons_1_to_9.Add(button1, 0, wx.EXPAND | wx.ALL, 10)
        vbox_buttons_1_to_9.Add(button2, 0, wx.EXPAND | wx.ALL, 10)
        vbox_buttons_1_to_9.Add(button3, 0, wx.EXPAND | wx.ALL, 10)
        vbox_buttons_1_to_9.Add(button4, 0, wx.EXPAND | wx.ALL, 10)

        # Horizontal box for button 7 and 8
        hbox_buttons_5_8 = wx.BoxSizer(wx.HORIZONTAL)
        hbox_buttons_5_8.Add(button6, 0, wx.ALL, 5)  # Smaller button <<
        hbox_buttons_5_8.Add(button7, 0, wx.ALL, 5)  # Smaller button <
        hbox_buttons_5_8.Add(button8, 0, wx.ALL, 5)  # Smaller button >
        hbox_buttons_5_8.Add(button5, 0, wx.ALL, 5)  # Smaller button >>
        
        vbox_buttons_1_to_9.Add(hbox_buttons_5_8, 0, wx.EXPAND | wx.ALL, 10)

        # Add Button 9
        vbox_buttons_1_to_9.Add(button9, 0, wx.EXPAND | wx.ALL, 10)

        # Create a second panel for buttons A, B, and C
        self.panel_ABC = wx.Panel(main_panel)
        buttonA = wx.Button(self.panel_ABC, label="x")
        buttonB = wx.Button(self.panel_ABC, label="y")
        buttonC = wx.Button(self.panel_ABC, label="z")

        buttonA.SetMinSize(small_button_size)
        buttonB.SetMinSize(small_button_size)
        buttonC.SetMinSize(small_button_size)

        self.panel_ABC.Hide()
        self.panel_ABC.Show()

        # Bind events for buttons A, B, and C
        buttonA.Bind(wx.EVT_BUTTON, self.on_buttonA_click)
        buttonB.Bind(wx.EVT_BUTTON, self.on_buttonB_click)
        buttonC.Bind(wx.EVT_BUTTON, self.on_buttonC_click)

        # Create a vertical box sizer for buttons A, B, and C
        vbox_buttons_ABC = wx.BoxSizer(wx.VERTICAL)
        vbox_buttons_ABC.Add(buttonA, 0, wx.EXPAND | wx.ALL, 10)
        vbox_buttons_ABC.Add(buttonB, 0, wx.EXPAND | wx.ALL, 10)
        vbox_buttons_ABC.Add(buttonC, 0, wx.EXPAND | wx.ALL, 10)
        self.panel_ABC.SetSizer(vbox_buttons_ABC)

        # Create the main horizontal box sizer for the entire layout
        hbox_main = wx.BoxSizer(wx.HORIZONTAL)
        hbox_main.Add(self.canvas, 1, wx.EXPAND)  # Add OpenGL canvas
        hbox_main.Add(vbox_buttons_1_to_9, 0, wx.EXPAND)  # Add buttons 1-9
        hbox_main.Add(self.panel_ABC, 0, wx.EXPAND)  # Add panel for buttons A, B, and C

        # Set the main panel's sizer to manage the layout
        main_panel.SetSizer(hbox_main)


    def on_button1_click(self, event):
        wx.MessageBox("Button 1 clicked", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_button2_click(self, event):
        wx.MessageBox("Button 2 clicked", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_button3_click(self, event):
        wx.MessageBox("Button 3 clicked", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_button4_click(self, event):
        wx.MessageBox("Button 4 clicked", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_button5_click(self, event):
        
        global rotate_figure, current_axis, rotate_direction

        rotate_direction = 1
        
        rotate_figure = True

        self.Refresh(False)  # Trigger a repaint

    def on_button6_click(self, event):
        
        global rotate_figure, current_axis, rotate_direction

        rotate_direction = -1
        
        rotate_figure = True

        self.Refresh(False)  # Trigger a repaint

    def on_button7_click(self, event):
        
        global rotate_figure, current_axis, rotate_direction

        rotate_direction = -2
        
        rotate_figure = True

        self.Refresh(False)  # Trigger a repaint

    def on_button8_click(self, event):

        global rotate_figure, current_axis, rotate_direction

        rotate_direction = 2

        # Check if 'A' is pressed to enable cube rotation
        
        rotate_figure = True

        self.Refresh(False)  # Trigger a repaint
        
        #wx.MessageBox("Button 8 clicked", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_button9_click(self, event):
        # When Button 9 is clicked, show the hidden panel with buttons A, B, and C
        self.panel_ABC.Show()
        self.Layout()  # Recalculate layout to account for the new panel


    def on_buttonA_click(self, event):
        global current_axis 
        current_axis= 'x'

    def on_buttonB_click(self, event):
        global current_axis 
        current_axis= 'y'

    def on_buttonC_click(self, event):
        global current_axis 
        current_axis= 'z'



class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        frame.Show(True)
        return True


if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
