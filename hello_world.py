import bpy
import math

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
            # If it exists, remove it
            bpy.data.objects[self.name].select_set(True)
            bpy.ops.object.delete()
            # If it doesn't exist, create a new shape primitive
        
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
    return 4*e*((a/r)**12 - (a/r)**6) # eV per particle

def intermolecular_force(r, a, e):
    return (24*e/a)*(2*(a/r)**13 - (a/r)**7) # Newtons


def particles(p1, p2):
    # Lennard-Jones potential:
    a = p1.radius * 2
    r = get_particles_distance(p1, p2)
    e = 0.065 # (eV) bond energy of liquid Argon particles
    force = intermolecular_force(r, a, e)
    # F = ma => a=F/m
    acc = force / p1.mass
    # a = dv/dt
    p1.velocity += acc * TICK
    dy = p1.velocity * TICK
    p1.move_location(y=dy)

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


# Example usage
OBJECTS = []
P1 = Sphere("p1", size=2, mass=1, x=0, y=3, z=1)
P2 = Sphere("p2", size=2, mass=1, x=0, y=0, z=1)
OBJECTS.append(P1)
OBJECTS.append(P2)


bpy.app.timers.register(gravity)
bpy.app.timers.register(lambda: particles(P1, P2))
bpy.app.timers.register(lambda: collision(P1, P2))
# bpy.app.timers.register(lambda: apply_velocity(P1, y=-0.01))
# bpy.app.timers.register(lambda: apply_velocity(P2, y=0.01))
