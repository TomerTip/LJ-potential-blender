import bpy

MS = 10**-3  # milliseconds
TICK = 1/60

class Body:
    def __init__(self, name, size, x, y, z):
        self.size = size
        self.name = name
        self.velocity = 0

        if self.name in bpy.data.objects:
            # If it exists, remove it
            bpy.data.objects[self.name].select_set(True)
            bpy.ops.object.delete()
            # If it doesn't exist, create a new shape primitive
        
        self.create_primitive(size, (x, y, size + z))

        self.obj = bpy.data.objects.get(self.name)

    def create_primitive(self, size, location):
        raise NotImplementedError("create_primitive method not implemented")

    def move_location(self, x=0, y=0, z=0):
        self.obj.location.x += x
        self.obj.location.y += y
        self.obj.location.z += z


class Cube(Body):
    def create_primitive(self, size, location):
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        bpy.context.object.name = self.name

class Sphere(Body):
    def create_primitive(self, size, location):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size/2, location=location)
        bpy.context.object.name = self.name


def gravity():
    GRAVITY = -9.8  # m/sec^2

    for object in OBJECTS:
        loc = object.obj.location
    # g= dv/dt
    # dx = v * dt
    # dx = g * dt^2

    # Collision with floor
        if loc.z - (object.size // 2) > 0:
            object.velocity += GRAVITY * TICK
            dz = object.velocity * TICK
            object.move_location(z=dz)

    return TICK # Seconds
# Example usage
OBJECTS = []
CUBE = Cube("my_cube", size=2, x=0, y=5, z=10)
SPHERE = Sphere("my_sphere", size=3, x=0, y=0, z=10)
OBJECTS.append(CUBE)
OBJECTS.append(SPHERE)


bpy.app.timers.register(gravity)
