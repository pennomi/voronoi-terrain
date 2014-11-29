from random import uniform
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, \
    GeomVertexWriter, GeomNode, GeomTristrips, GeomTrifans, GeomLines
from pyhull.voronoi import VoronoiTess
from noise import snoise2


class VoronoiTile:
    def __init__(self, point, vertices, map_width=1024, map_height=1024, base=0.0):
        self.point = point
        # TODO: Sort these clockwise (they still are 2D points)
# http://stackoverflow.com/questions/6989100/sort-points-in-clockwise-order
        # Might just need to reverse if the wrong way. I think they're already
        # ordered. Should be able to tell by checking the normal calculation.
        self.vertices = vertices

        # Ensure that stuff is working correctly
        if [-10.101, -10.101] in vertices:
            raise ValueError("Can't create this region.")

        # TODO: Constrain the bounds like this... though it's somewhat busted.
        # for i, v in enumerate(vertices):
        #     x, y = v
        #     x = max(min(x, map_width/2), -map_width/2)
        #     y = max(min(y, map_height/2), -map_height/2)
        #     vertices[i] = (x, y)

        for v in vertices:
            if not (-map_width/2 <= v[0] <= map_width/2 and
                    -map_height/2 <= v[1] <= map_height/2):
                raise ValueError("Can't create this region.")

        # Prepare the vertex format writers
        v_fmt = GeomVertexFormat.getV3n3c4()
        v_data = GeomVertexData('TerrainData', v_fmt, Geom.UHStatic)
        vertex = GeomVertexWriter(v_data, 'vertex')
        normal = GeomVertexWriter(v_data, 'normal')
        color = GeomVertexWriter(v_data, 'color')
        #texcoord = GeomVertexWriter(v_data, 'texcoord')

        # Create a primitive
        # TODO: Migrate to Tristrips.
        # TODO: Make walls, floors (and ceilings?)
        prim = GeomTrifans(Geom.UHStatic)

        DETAIL = 128
        HEIGHT_SCALE = 20
        vertices = [
            (v[0], v[1], snoise2(
                v[0]/DETAIL, v[1]/DETAIL, base=base,
                persistence=0.5, lacunarity=2.0,
                repeatx=map_width/4, repeaty=map_height/4,
                octaves=5) * HEIGHT_SCALE)
            for v in vertices]

        num_above = len(list(filter(lambda x: x[2] > 0, vertices)))
        num_below = len(list(filter(lambda x: x[2] <= 0, vertices)))

        # Calculate the color:
        #  * Green if land
        #  * Tan if coast
        #  * Blue if water
        # poly_color = (uniform(0, 1), uniform(0, 1), uniform(0, 1), 1, )
        if num_below and num_above:
            yellow = uniform(0.5, 1.0)
            poly_color = (yellow, yellow, 0.0, 0.0)
        elif num_below:
            poly_color = (0.0, 0.0, uniform(0.5, 1.0), 0.0)
        else:
            poly_color = (0.0, uniform(0.5, 1.0), 0.0, 0.0)

        for i, point in enumerate(vertices):
            vertex.addData3f(*point)
            normal.addData3f(0, 0, 1)
            color.addData4f(*poly_color)
            #texcoord.addData2f(1, 0)
            prim.addVertex(i)
        prim.addVertex(0)
        prim.closePrimitive()

        # Add to the scene graph
        geom = Geom(v_data)
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        nodePath = render.attachNewNode(node)
        nodePath.setTwoSided(True)


def add_plane(map_width, map_height):
    # Prepare the vertex format writers
    v_fmt = GeomVertexFormat.getV3n3c4()
    v_data = GeomVertexData('TerrainData', v_fmt, Geom.UHStatic)
    vertex = GeomVertexWriter(v_data, 'vertex')
    normal = GeomVertexWriter(v_data, 'normal')
    color = GeomVertexWriter(v_data, 'color')
    #texcoord = GeomVertexWriter(v_data, 'texcoord')

    # Create a primitive
    prim = GeomTrifans(Geom.UHStatic)
    poly_color = (uniform(0, 0.05), uniform(0, 0.5), uniform(0.5, 1), 0.5, )

    for i, point in enumerate([
            (-map_width/2, -map_height/2),
            (map_width/2, -map_height/2),
            (map_width/2, map_height/2),
            (-map_width/2, map_height/2), ]):
        x, y = point
        vertex.addData3f(x, y, 0)
        normal.addData3f(0, 0, 1)
        color.addData4f(*poly_color)
        #texcoord.addData2f(1, 0)
        prim.addVertex(i)
    prim.addVertex(0)
    prim.closePrimitive()

    # Add to the scene graph
    geom = Geom(v_data)
    geom.addPrimitive(prim)
    node = GeomNode('gnode')
    node.addGeom(geom)
    nodePath = render.attachNewNode(node)
    nodePath.setTwoSided(True)
    nodePath.setAlphaScale(0.5)


def build_terrain():
    BASE = uniform(0.0, 10.0)
    MAP_SIZE = (128, 128)
    NUM_POINTS = 1000

    pts = [(uniform(-MAP_SIZE[0]/2, MAP_SIZE[0]/2),
            uniform(-MAP_SIZE[1]/2, MAP_SIZE[1]/2)) for n in range(NUM_POINTS)]
    # TODO: Merge any points that are too close together here

    data = VoronoiTess(pts)
    count = 0
    tiles = []
    for i, r in enumerate(data.regions):
        try:
            t = VoronoiTile(data.points[i], [data.vertices[i] for i in r],
                            map_width=MAP_SIZE[0], map_height=MAP_SIZE[1],
                            base=BASE)
            tiles.append(t)
        except ValueError:
            continue

    add_plane(*MAP_SIZE)