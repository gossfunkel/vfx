from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, Vec4, Shader, GeomNode, GeomPoints, 
    Geom, GeomEnums, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    ModelRoot, BoundingBox, ShaderBuffer, BoundingVolume, ComputeNode
)
import numpy as np

CONFIG = """
win-size 1920 1040
gl-version 4 3
load-display pandagl
gl-force-glsl-version 430
gl-debug true
show-frame-rate-meter true
//gl-debug-buffers true
//gl-support-spirv false
// \\// big boss debugger
//notify-level-glgsg debug
hardware-points true
hardware-point-sprites true
singular-points true
framebuffer-srgb true
hardware-animated-vertices true
"""
load_prc_file_data('', CONFIG)

NUM_PTS = 2000

# entry point: this is not to be run from elsewhere
if __name__ == "__main__":
    print("="*14 + " Solar " + "="*8)
    ShowBase()                                                          # base available from here
    base.disableMouse() 

    base.set_background_color(0.,0.,0.,1.)

    # define the size of the scene
    width = 25.
    depth = 25.
    height = 20.
    scale = Vec3(width, depth, height)

    raw_ssbo_data = np.zeros(8*NUM_PTS, dtype=np.float32)

    # define VBO
    vtx_format = GeomVertexFormat.getV3c4()
    vtx_data   = GeomVertexData('pts_vbo', vtx_format, Geom.UHStatic)
    vtx_data.set_num_rows(NUM_PTS)

    # fill VBO with initial data and create geometry primitives
    vtx_writer = GeomVertexWriter(vtx_data, "vertex")
    col_writer = GeomVertexWriter(vtx_data, "color")
    for pt in range(NUM_PTS):
        x = float(pt%10)*2.5 + width/2.
        y = float(pt%100)/4 + depth/2.
        z = float(pt/NUM_PTS)*height + height/2.
        raw_ssbo_data[pt*8] = x
        raw_ssbo_data[pt*8 + 1] = y
        raw_ssbo_data[pt*8 + 2] = z
        vtx_writer.add_data3(x, y, z)
        col_writer.add_data4(1.,pt/1000.,1. - pt/1000.,1.)

    pt_ssbo = ShaderBuffer("pt_ssbo", raw_ssbo_data.tobytes(), GeomEnums.UHDynamic)
    vel_ssbo = ShaderBuffer("vel_ssbo", np.zeros(4*NUM_PTS*NUM_PTS, dtype=np.float32).tobytes(), GeomEnums.UHDynamic)

    # create primitive for mesh
    prim = GeomPoints(Geom.UHStatic)
    prim.add_consecutive_vertices(0, NUM_PTS)
    prim.close_primitive()

    # create mesh
    geom = Geom(vtx_data)
    geom.add_primitive(prim)
    #geom.set_bounds(BoundingBox((-1.*width,-1.*depth,-1.*height), (width+1.,depth+1.,height+1.)))
    geom.set_bounds(BoundingBox((-4.*width,-4.*depth,-4.*height), (width*4. + 1.,depth*4. + 1.,height*4. + 1.)))
    node = GeomNode('pts_geomnode')
    node.add_geom(geom)

    solar_shader = Shader.load(Shader.SL_GLSL, "solar.vert", "solar.frag")
    solar_np = base.render.attach_new_node(node)
    solar_np.set_shader(solar_shader)
    solar_np.set_shader_input("pt_buff", pt_ssbo)
    #solar_np.set_shader_input("vel_buff", vel_ssbo)
    solar_np.set_shader_input("num_pts", NUM_PTS)
    solar_np.set_two_sided(True)
    #solar_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    solar_np.set_depth_write(True)
    #solar_np.set_depth_offset(1)
    solar_np.node().set_bounds_type(BoundingVolume.BT_box)

    num_invoc = (NUM_PTS**2 + NUM_PTS)//2
    compute_node = ComputeNode("compute")
    # n**2 computes to do each calculation in parallel
    compute_node.add_dispatch(NUM_PTS//4, NUM_PTS//4, 1)
    compute_np = base.render.attach_new_node(compute_node)
    compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "solar.comp"))
    compute_np.set_shader_input("pt_buff", pt_ssbo)
    compute_np.set_shader_input("vel_buff", vel_ssbo)
    compute_np.set_shader_input("num_pts", NUM_PTS)

    sum_node = ComputeNode("sum_comp")
    # n**2 computes to do each calculation in parallel
    sum_node.add_dispatch(NUM_PTS//16, 1, 1)
    sum_np = base.render.attach_new_node(sum_node)
    sum_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "sum_solar.comp"))
    sum_np.set_shader_input("pt_buff", pt_ssbo)
    sum_np.set_shader_input("vel_buff", vel_ssbo)
    sum_np.set_shader_input("num_pts", NUM_PTS)
    
    base.accept("escape", base.userExit)
    
    def rotate_cam(task):
        base.cam.set_pos(np.sin(task.frame/5000.)*width*2 + width/2.,
            -np.cos(task.frame/5000.)*depth*2 + depth/2.,
            #np.cos(task.frame/2000.) + height/2.)
            height)
        base.cam.look_at(scale)
        return task.cont

    base.taskMgr.add(rotate_cam, "rotate-camera")

    base.cam.setPos(width,-30.,height)
    base.cam.look_at(scale)
    #base.cam.setHpr(0.,-.5,0.)

    base.run()