from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, Shader, TexGenAttrib,
    Geom, GeomEnums, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    GeomNode, GeomTriangles, TextureStage, ModelRoot, BoundingBox
)

CONFIG = """
win-size 1200 800
gl-version 4 3
gl-debug true
gl-debug-buffers true
hardware-points true
hardware-point-sprites true
singular-points true
framebuffer-srgb true
hardware-animated-vertices true
"""
load_prc_file_data('', CONFIG)

# entry point: this is not to be run from elsewhere
if __name__ == "__main__":
    ShowBase()                      # base available from here

    base.set_background_color(.01,0.,0.,1.)

    # define how many points we will generate
    num_points = 20000

    # define the size of the scene
    width = 25
    depth = 100
    height = 25

    # define VBO
    vtx_format = GeomVertexFormat.getV3c4()
    vtx_data   = GeomVertexData('pts_vbo', vtx_format, Geom.UHStatic)
    vtx_data.set_num_rows(num_points)

    # fill VBO with initial data and create geometry primitives
    vtx_writer = GeomVertexWriter(vtx_data, "vertex")
    col_writer = GeomVertexWriter(vtx_data, "color")
    prim = GeomTriangles(Geom.UHStatic)
    for quad in range(num_points):
        vtx_writer.add_data3((float(quad)*width)/num_points,     0., 0.)
        vtx_writer.add_data3((float(quad)*width)/num_points,     0., -.04)
        vtx_writer.add_data3((float(quad)*width)/num_points+.04, 0., 0.)
        vtx_writer.add_data3((float(quad)*width)/num_points+.04, 0., -.04)
        col_writer.add_data4(.8,0.,1.,1.)
        prim.add_vertices(quad*4,     quad*4 + 1, quad*4 + 2)
        prim.add_vertices(quad*4 + 2, quad*4 + 1, quad*4 + 3)
    prim.close_primitive()

    # create mesh
    geom = Geom(vtx_data)
    geom.add_primitive(prim)
    geom.set_bounds(BoundingBox((-1.,-1.,-1.), (width,depth,height)))
    node = GeomNode('pts_geomnode')
    node.add_geom(geom)

    # assemble node structure
    root = ModelRoot('pts_root')
    root.add_child(node)
    nodepath = NodePath(root)
    nodepath.reparent_to(base.render)
    # nodepath = base.render.attach_new_node(node)

    # give points perspective scale
    #nodepath.set_render_mode_thickness(10.)
    #nodepath.set_render_mode_perspective(True, 0)

    # generate texcoords for the sprites
    # ts = TextureStage('ts_pts')
    # ts.setMode(TextureStage.MModulate)
    # nodepath.set_tex_gen(ts, TexGenAttrib.M_point_sprite)
    #nodepath.set_tex_gen(TextureStage.get_default(), TexGenAttrib.M_eye_cube_map)

    # attach shaders to node
    nodepath.set_shader(Shader.load(Shader.SL_GLSL,
                                    vertex="tripoints.vert", 
                                    fragment="tripoints.frag"))

    # set Esc key as quit button
    base.accept("escape", base.userExit)

    # position camera
    base.cam.setPos(12.5,-32,4)
    base.cam.setHpr(0,-7,0)
    #base.cam.look_at(nodepath)

    base.run()                      # taskMgr takes over from here

