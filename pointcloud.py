from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, Vec4, Shader, GeomNode, GeomPoints, 
    Geom, GeomEnums, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    ModelRoot, BoundingBox, ShaderBuffer,
    TransparencyAttrib, TexGenAttrib, ShaderAttrib, ColorBlendAttrib
)
from cam_control import enable_camera_controls
import scipy.io.wavfile as sp
import numpy as np
import sounddevice as sd

CONFIG = """
win-size 1200 800
gl-version 4 3
load-display pandagl
gl-force-glsl-version 430
gl-debug true
gl-debug-buffers true
gl-support-spirv false
// \\// big boss debugger
//notify-level-glgsg debug
hardware-points true
hardware-point-sprites true
singular-points true
framebuffer-srgb true
hardware-animated-vertices true
"""
load_prc_file_data('', CONFIG)

NUM_PTS = 100
NUM_STATES = 3

# entry point: this is not to be run from elsewhere
if __name__ == "__main__":
    print("="*14 + " Point Cloud Animator " + "="*8)
    ShowBase()                                                          # base available from here
    base.disableMouse() 

    base.set_background_color(0.,0.,0.,1.)

    # define the size of the scene
    width = 25.
    depth = 25.
    height = 20.
    scale = Vec3(width, depth, height)

    raw_ssbo_data = np.zeros(4*NUM_PTS, dtype=np.float32)

    # define VBO
    vtx_format = GeomVertexFormat.getV3c4()
    vtx_data   = GeomVertexData('pts_vbo', vtx_format, Geom.UHStatic)
    vtx_data.set_num_rows(NUM_PTS)

    # fill VBO with initial data and create geometry primitives
    vtx_writer = GeomVertexWriter(vtx_data, "vertex")
    col_writer = GeomVertexWriter(vtx_data, "color")
    for pt in range(NUM_PTS):
        x = float(pt)/width
        y = float(pt)%depth
        z = float(pt)/height
        raw_ssbo_data[pt*4] = x
        raw_ssbo_data[pt*4 + 1] = y
        raw_ssbo_data[pt*4 + 2] = z
        vtx_writer.add_data3(x, y, z)
        col_writer.add_data4(1.,1.,1.,1.)

    # prepare SSBO of positions
    ssbo = ShaderBuffer("ssbo", raw_ssbo_data.tobytes(), GeomEnums.UHDynamic)

    # create primitive for mesh
    prim = GeomPoints(Geom.UHStatic)
    prim.add_consecutive_vertices(0, NUM_PTS)
    prim.close_primitive()

    # create mesh
    geom = Geom(vtx_data)
    geom.add_primitive(prim)
    geom.set_bounds(BoundingBox((-1.,-1.,-1.), (width+1.,depth+1.,height+1.)))
    node = GeomNode('pts_geomnode')
    node.add_geom(geom)

    # assemble node structure
    root = ModelRoot('pts_root')
    root.add_child(node)
    nodepath = NodePath(root)
    nodepath.reparent_to(base.render)

    # set up additive blending (thanks rdb!)
    nodepath.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    nodepath.set_depth_write(False)

    base.shader_state = 0

    # attach shaders to node
    attrib = ShaderAttrib.make()
    attrib = attrib.setShader(Shader.load(Shader.SL_GLSL,
                                    vertex="points.vert", 
                                    fragment="points.frag"))
    attrib = attrib.set_shader_input("scene_scale", scale)
    attrib = attrib.set_shader_input("NUM_PTS", NUM_PTS)
    attrib = attrib.set_shader_input("ssbo", ssbo)
    attrib = attrib.set_shader_input("state", base.shader_state)
    attrib = attrib.set_flag(ShaderAttrib.F_shader_point_size, True)
    root.set_attrib(attrib)

    def incState():
        attrib = root.get_attrib(ShaderAttrib)
        base.shader_state = (base.shader_state + 1)%NUM_STATES
        print("Incrementing state to " + str(base.shader_state))
        attrib = attrib.set_shader_input("state", base.shader_state)
        root.set_attrib(attrib)

    def setState(st):
        attrib = root.get_attrib(ShaderAttrib)
        base.shader_state = (st)%NUM_STATES
        print("Setting state to " + str(base.shader_state))
        attrib = attrib.set_shader_input("state", base.shader_state)
        root.set_attrib(attrib)

    def pauseState():
        attrib = root.get_attrib(ShaderAttrib)
        base.shader_state = 0
        print("Setting state to 0 (paused)")
        attrib = attrib.set_shader_input("state", base.shader_state)
        root.set_attrib(attrib)

    base.accept("escape", base.userExit)

    base.accept("space", incState)
    base.accept('p', pauseState)
    base.accept('1', setState, [1])
    base.accept('2', setState, [2])

    # position camera
    base.cam.setPos(0.,-75.,15.)
    base.cam.setHpr(0.,-2.5,0.)
    #enable_camera_controls()

    base.run()                      # taskMgr takes over from here
