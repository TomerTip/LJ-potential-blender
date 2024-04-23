import bpy
import math
import matplotlib
matplotlib.use('Qt5Agg')  # Set the backend to Agg
import matplotlib.pyplot as plt
import matplotlib.animation as animation

MS = 10**-3  # milliseconds
TICK = 1/60

class Body:
    def __init__(self, name, size, mass, x, y, z):
        self.size = size
        self.name = name
        self.velocity = 0
        self.mass = mass
        self.is_colisioned = False

        if self.name in bpy.data.objects:
            bpy.data.objects[self.name].select_set(True)
            bpy.ops.object.delete()
        
        self.create_primitive(size, (x, y, z))

        self.obj = bpy.data.objects.get(self.name)

    def create_primitive(self, size, location):
        raise NotImplementedError("create_primitive method not implemented")

    def move_location(self, x=0, y=0, z=0):
        self.obj.location.x += x
        self.obj.location.y += y
        self.obj.location.z += z

    def get_location(self):
        x = self.obj.location.x
        y = self.obj.location.y
        z = self.obj.location.z
        return (x, y, z)


class Cube(Body):
    def create_primitive(self, size, location):
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        bpy.context.object.name = self.name

class Sphere(Body):
    @property
    def radius(self):
        return self.size // 2
    
    def create_primitive(self, size, location):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size//2, location=location)
        bpy.context.object.name = self.name

def distance(vec1, vec2):
    x1, y1, z1 = vec1
    x2, y2, z2 = vec2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance

def get_particles_distance(p1: Body, p2: Body):
    return distance(p1.get_location(), p2.get_location())

def lennard_jones_potential(r, a, e):
    # https://chem.libretexts.org/Bookshelves/Physical_and_Theoretical_Chemistry_Textbook_Maps/Supplemental_Modules_(Physical_and_Theoretical_Chemistry)/Physical_Properties_of_Matter/Atomic_and_Molecular_Properties/Intermolecular_Forces/Specific_Interactions/Lennard-Jones_Potential
    potential =  4*e*((a/r)**12 - (a/r)**6) # eV per particle
    return potential

def intermolecular_force(r, a, e):
    force = (24*e/a)*(2*(a/r)**13 - (a/r)**7) # Newtons    
    return force

def particles(p1, p2, e=0.065):
    # Lennard-Jones potential:
    a = p1.radius * 2
    r = get_particles_distance(p1, p2)
    # e = 0.065 # (eV) bond energy of liquid Argon particles
    force = intermolecular_force(r, a, e)
    potential = lennard_jones_potential(r, a, e)
    graph_force(force, r)
    graph_potential(potential, r)

    # F = ma => a=F/m
    acc = force / p1.mass
    # a = dv/dt
    p1.velocity += acc * TICK
    dy = p1.velocity * TICK
    p1.move_location(y=dy)
    p2.move_location(y=-dy)

    return TICK

def collision(p1, p2):
    p1_loc = p1.get_location()
    p2_loc = p2.get_location()
    if distance(p1_loc, p2_loc) <= 2 * p1.radius:
        p1.is_colisioned = True
        p2.is_colisioned = True

    return TICK

def gravity():
    GRAVITY = -9.8  # m/sec^2

    for object in OBJECTS:
        loc = object.obj.location
        # g = dv/dt
        # dx = v * dt
        # dx = g * dt^2

        # Collision with floor
        if loc.z - (object.size // 2) > 0:
            object.velocity += GRAVITY * TICK
            dz = object.velocity * TICK
            object.move_location(z=dz)

    return TICK # Seconds


def apply_velocity(body, x=0, y=0, z=0):
    if not body.is_colisioned:
        body.move_location(x, y, z)

    return TICK # Seconds


def graph_potential(potential, r):
    potential_r_values.append(r)
    potential_U_values.append(potential)

def graph_force(force, r):
    force_r_values.append(r)
    force_F_values.append(force)

def force_graph_update(i):
    # Clear previous plot and plot new data
    plt.clf()
    plt.plot(force_r_values, force_F_values)
    plt.xlabel('r(Å)')
    plt.ylabel('F(r)(10^-10 N)')
    plt.title('F(r) - Force of repulsion and attraction')
    plt.grid(True)

# Function to update the plot with new data
def potential_graph_update(i):
    # Clear previous plot and plot new data
    plt.clf()
    plt.plot(potential_r_values, potential_U_values)
    plt.xlabel('r(Å)')
    plt.ylabel('U(r)(eV)')
    plt.title('U(r) - Potential Energy')
    plt.grid(True)


def blender_cleanup():
    for obj in bpy.data.objects:
        obj.select_set(True)
        bpy.ops.object.delete()

# blender_cleanup()
OBJECTS = []
P1 = Sphere("p1", size=2, mass=0.5, x=0, y=2, z=1)
P2 = Sphere("p2", size=2, mass=0.5, x=0, y=-2, z=1)
OBJECTS.append(P1)
OBJECTS.append(P2)


bpy.app.timers.register(lambda: particles(P1, P2, e=2))
# bpy.app.timers.register(gravity)
# bpy.app.timers.register(lambda: collision(P1, P2))
# bpy.app.timers.register(lambda: apply_velocity(P1, y=-0.01))
# bpy.app.timers.register(lambda: apply_velocity(P2, y=0.01))

# Initialize lists to store r and F(r) values
force_F_values = []
force_r_values = []
potential_U_values = []
potential_r_values = []
particle_i = 0

# # Enable interactive mode for non-blocking plotting
plt.ion()

 # 0 - non, 1 - force, 2 - potential
graph_menu = 0

if graph_menu == 1:
    # Create a figure
    force_fig = plt.figure(1)
    force_ani = animation.FuncAnimation(force_fig, force_graph_update, interval=100)  # Update plot every 100 milliseconds
    force_fig.show(block=False)
elif graph_menu == 2:
    # Animate the plot
    potential_fig = plt.figure(2)
    potential_ani = animation.FuncAnimation(potential_fig, potential_graph_update, interval=10)  # Update plot every 100 milliseconds
    potential_fig.show()