from random import uniform
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, \
    GeomVertexWriter, GeomNode, GeomTristrips
from pyhull.voronoi import VoronoiTess
from noise import pnoise2


class VoronoiTile:
    def __init__(self, point, vertices, map_width=30, map_height=30):
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
        # TODO: Fix the Tristrips problem.
        # TODO: Make walls, floors (and ceilings?)
        prim = GeomTristrips(Geom.UHStatic)
        poly_color = (uniform(0, 1), uniform(0, 1), uniform(0, 1), 1, )

        for i, point in enumerate(vertices):
            vertex.addData3f(point[0], point[1], pnoise2(point[0]/10, point[1]/10, octaves=5) * 3)
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


def build_terrain():
    MAP_SIZE = (60, 60)

    pts = [(uniform(-MAP_SIZE[0]/2, MAP_SIZE[0]/2),
            uniform(-MAP_SIZE[1]/2, MAP_SIZE[1]/2)) for n in range(1000)]
    # TODO: Merge any points that are too close together here

    data = VoronoiTess(pts)
    count = 0
    tiles = []
    for i, r in enumerate(data.regions):
        try:
            t = VoronoiTile(data.points[i], [data.vertices[i] for i in r],
                            map_width=MAP_SIZE[0], map_height=MAP_SIZE[1])
            tiles.append(t)
        except ValueError:
            continue