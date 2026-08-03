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

# entry point: this is not to be run from elsewhere
if __name__ == "__main__":
    print("="*14 + " Point Cloud Animator " + "="*8)
    ShowBase()                                                          # base available from here
    base.disableMouse() 

    base.set_background_color(0.,0.,0.,1.)

    # define how many points we will generate
    num_points = 100

    # define the size of the scene
    width = 25.
    depth = 25.
    height = 20.
    scale = Vec3(width, depth, height)

    # define VBO
    vtx_format = GeomVertexFormat.getV3c4()
    vtx_data   = GeomVertexData('pts_vbo', vtx_format, Geom.UHStatic)
    vtx_data.set_num_rows(num_points)

    # fill VBO with initial data and create geometry primitives
    vtx_writer = GeomVertexWriter(vtx_data, "vertex")
    col_writer = GeomVertexWriter(vtx_data, "color")
    for quad in range(num_points):
        vtx_writer.add_data3(float(quad)/num_points, 0., 0.)
        col_writer.add_data4(1.,1.,1.,1.)

    # prepare SSBO of positions
    ssbo = ShaderBuffer("ssbo", np.array([Vec4(i,i,i,1.) for i in range(num_points)]).tobytes(), GeomEnums.UHDynamic)

    # create primitive for mesh
    prim = GeomPoints(Geom.UHStatic)
    prim.add_consecutive_vertices(0, num_points)
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

    # attach shaders to node
    attrib = ShaderAttrib.make()
    attrib = attrib.setShader(Shader.load(Shader.SL_GLSL,
                                    vertex="points.vert", 
                                    fragment="points.frag"))
    attrib = attrib.set_shader_input("scene_scale", scale)
    attrib = attrib.set_shader_input("num_points", num_points)
    attrib = attrib.set_shader_input("ssbo", ssbo)
    attrib = attrib.set_flag(ShaderAttrib.F_shader_point_size, True)
    root.set_attrib(attrib)

    # set Esc key as quit button
    base.accept("escape", base.userExit)

    # position camera
    base.cam.setPos(0.,-75.,15.)
    base.cam.setHpr(0.,-2.5,0.)
    enable_camera_controls()

    base.run()                      # taskMgr takes over from here
