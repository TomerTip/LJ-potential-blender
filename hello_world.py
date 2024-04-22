import bpy

MS = 10**-3  # miliseconds
TICK = 1/60

class Body:
    ...

class Cube(Body):
    def __init__(self, name, size, x, y, z) -> None:
        self.size = size
        self.name = name
        self.velocity = 0

        if self.name in bpy.data.objects:
            # If it exists, get the object
            obj = bpy.data.objects[self.name]
            # Reset its location to (0, 0, 0)
            obj.location = (x, y, size + z)
        else:
            # If it doesn't exist, create a new cube primitive
            bpy.ops.mesh.primitive_cube_add(size=self.size, location=(x, y, size + z))
            # Rename the object to "Cube"
            bpy.context.object.name = self.name

        self.obj = bpy.data.objects.get(name)
        self.obj_location = self.obj.location

    def move_location(self, x=0, y=0, z=0):
        self.obj_location.x += x
        self.obj_location.y += y
        self.obj_location.z += z


def gravity():
    GRAVITY = -9.8  # m/sec^2
    loc = CUBE.obj_location
    # g= dv/dt
    # dx = v * dt
    # dx = g * dt^2

    # Collision with floor
    if loc.z - (CUBE.size // 2) > 0:
        CUBE.velocity += GRAVITY * TICK
        dz = CUBE.velocity * TICK
        CUBE.move_location(z=dz)


    return TICK # Seconds

CUBE = Cube("my_cube", size=2, x=0, y=0, z=1000)

bpy.app.timers.register(gravity)
