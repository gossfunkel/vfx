from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, Shader, GeomNode, GeomPoints, 
    Geom, GeomEnums, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    ModelRoot, BoundingBox, ShaderBuffer, Texture, SamplerState,
    TransparencyAttrib, TexGenAttrib, ShaderAttrib, ColorBlendAttrib
)
from cam_control import enable_camera_controls
import numpy as np

NUM_PTS = 10000
WIDTH = NUM_PTS/100
DEPTH = 1
HEIGHT = NUM_PTS/WIDTH
SIM_SCALE = Vec3(WIDTH, DEPTH, HEIGHT)

CONFIG = """
win-size 1600 1000
gl-version 4 3
load-display pandagl
gl-debug true
gl-debug-buffers true
gl-force-glsl-version 430 // required for ssbo format
hardware-points true
hardware-point-sprites true
singular-points true
framebuffer-srgb true
hardware-animated-vertices true
"""
load_prc_file_data('', CONFIG)

def toggle_view():
    base.cam_view = (base.cam_view + 1) % 3
    match base.cam_view:
        case 0:
            base.cam.setPos(50.,-150.,50.)
            base.cam.setHpr(0., 0., 0.)
        case 1:
            base.cam.setPos(0.,-10.,0.)
            base.cam.setHpr(-45., 60., 60.)
        case 2:
            base.cam.setPos(50.,-2.,0.)
            base.cam.setHpr(0., 85., 0.)

if __name__ == "__main__":
    ShowBase()

    base.disableMouse() 

    base.set_background_color(0.,0.,0.,1.)

    #y_positions = np.sin(np.linspace(0,1,NUM_PTS), dtype=np.float32)
    y_positions = np.zeros(NUM_PTS, dtype=np.float32)
    y_positions[5000] = .1
    print(f'Y position data: {y_positions}')
    #ssbo_data = np.vstack((y_positions, -y_positions)).reshape((NUM_PTS*2,), order='F')
    ssbo_data = np.concatenate((y_positions, np.zeros(NUM_PTS, dtype=np.float32)))
    #ssbo_data = np.vstack((y_positions, np.zeros(NUM_PTS, dtype=np.float32))).reshape((NUM_PTS*2,), order='F')
    #ssbo_data = np.zeros(NUM_PTS*2, dtype=np.float32)
    #for item in range(len(y_positions)):
    #    ssbo_data[item*2] = y_positions[item]
    ssbo = ShaderBuffer("ssbo", ssbo_data.tobytes(), GeomEnums.UHDynamic)

    # vertex buffer object (VBO) initialisation
    vtx_format = GeomVertexFormat.getV3c4()
    vtx_data   = GeomVertexData('pts_vbo', vtx_format, Geom.UHStatic)
    vtx_data.set_num_rows(NUM_PTS)

    # fill VBO with initial data and create geometry primitives
    vtx_writer = GeomVertexWriter(vtx_data, "vertex")
    col_writer = GeomVertexWriter(vtx_data, "color")
    for quad in range(NUM_PTS):
        vtx_writer.add_data3(float(quad/WIDTH), y_positions[quad], float(quad%HEIGHT))
        col_writer.add_data4(1.,1.,1.,1.)

    # create primitive for mesh
    prim = GeomPoints(Geom.UHStatic)
    prim.add_consecutive_vertices(0, NUM_PTS)
    prim.close_primitive()

    # create mesh
    geom = Geom(vtx_data)
    geom.add_primitive(prim)
    geom.set_bounds(BoundingBox((-1.,-2.,-1.), (WIDTH+1.,DEPTH+2.,HEIGHT+1.)))
    node = GeomNode('pts_geomnode')
    node.add_geom(geom)

    # assemble node structure
    root = ModelRoot('pts_root')
    root.add_child(node)
    nodepath = NodePath(root)
    nodepath.reparent_to(base.render)

    # attach shaders to node
    attrib = ShaderAttrib.make()
    attrib = attrib.setShader(Shader.load(Shader.SL_GLSL,
                                    vertex="grid_waves.vert", 
                                    fragment="grid_waves.frag"))
    attrib = attrib.set_shader_input("sim_scale", SIM_SCALE)
    attrib = attrib.set_shader_input("NUM_PTS", NUM_PTS)
    attrib = attrib.set_shader_input("ssbo", ssbo)
    attrib = attrib.set_flag(ShaderAttrib.F_shader_point_size, True)
    root.set_attrib(attrib)

    # set Esc key as quit button
    base.accept("escape", base.userExit)

    # position camera
    base.cam.setPos(50.,-150.,50.)
    base.cam.setHpr(0., 0., 0.)
    base.cam_view = 0
    base.accept("v", toggle_view)
    
    enable_camera_controls()

    base.run()
