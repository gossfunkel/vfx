from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, GeomNode, Geom, GeomEnums, ModelRoot,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, 
    BoundingVolume, BoundingBox, ComputeNode, ColorBlendAttrib, CardMaker,
    Shader, ShaderBuffer, Texture, SamplerState, ShaderAttrib
)
import numpy as np

NUM_VERTS = 8192

CONFIG = """
win-size 1920 1040
gl-version 4 3
load-display pandagl
gl-debug true
gl-debug-buffers true
gl-force-glsl-version 430 // required for ssbo format
framebuffer-srgb true
hardware-animated-vertices true
"""
load_prc_file_data('', CONFIG)

if __name__ == "__main__":
    ShowBase()
    base.set_background_color(0.,0.,0.,1.)

    row_len = 64

    raw_ssbo_data = np.zeros(4*NUM_VERTS, dtype=np.float32)
    for idx in range(NUM_VERTS):
        raw_ssbo_data[idx*4] = idx%row_len                 # x
        raw_ssbo_data[idx*4+1] = idx/row_len               # y
        #raw_ssbo_data[idx*4+2] =  .3 + .2 * np.sin(idx)    # z
        raw_ssbo_data[idx*4+2] = 0.                     # z

    ssbo = ShaderBuffer('sprites', raw_ssbo_data.tobytes(), GeomEnums.UHStatic)

    vtx_format = GeomVertexFormat.get_empty()
    vtx_data = GeomVertexData('sprites', vtx_format, GeomEnums.UH_static)

    geom_tris = GeomTriangles(GeomEnums.UH_static)
    for quad in range(NUM_VERTS-(NUM_VERTS//row_len)-(row_len-1)):
        quadstart = (quad%(row_len-1)) + (quad // (row_len-1))*row_len
        quadstart_row2 = quadstart + row_len
        geom_tris.add_vertex(quadstart)
        geom_tris.add_vertex(quadstart_row2)
        geom_tris.add_vertex(quadstart + 1)
        geom_tris.add_vertex(quadstart + 1)
        geom_tris.add_vertex(quadstart_row2)
        geom_tris.add_vertex(quadstart_row2 + 1)

    geom = Geom(vtx_data)
    geom.add_primitive(geom_tris)
    geom.set_bounds(BoundingBox((-1, -1, -1), (100, 100, 100)))

    geom_node = GeomNode("gnode")
    geom_node.add_geom(geom)

    mesh_shader = Shader.load(Shader.SL_GLSL, "mesh.vert", "mesh.frag")
    mesh_np = base.render.attach_new_node(geom_node)
    mesh_np.set_shader(mesh_shader)
    mesh_np.set_shader_input("vert_buff", ssbo)
    mesh_np.set_two_sided(True)
    mesh_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    mesh_np.set_depth_write(False)
    mesh_np.node().set_bounds_type(BoundingVolume.BT_box)

    compute_node = ComputeNode("compute")
    compute_node.add_dispatch(NUM_VERTS // 64, 4, 1)
    compute_np = base.render.attach_new_node(compute_node)
    compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "mesh.comp"))
    compute_np.set_shader_input("vert_buff", ssbo)
    compute_np.set_shader_input("num_verts", NUM_VERTS)

    # filter_mgr = FilterManager(base.win, base.cam)
    # #filter_mgr.resizeBuffers()
    # #filter_mgr.windowEvent(base.win)
    # screen_tex = Texture()
    # screen_tex.setMagfilter(SamplerState.FT_nearest)
    # screen_tex.setMinfilter(SamplerState.FT_nearest)
    # #screen_tex.setMatchFramebufferFormat()
    # screen_card = filter_mgr.renderSceneInto(colortex=screen_tex)
    # screen_tex.set_format(Texture.F_srgb_alpha)
    # screen_card.set_shader(Shader.load(Shader.SL_GLSL, vertex="quad.vert", fragment="screen_filter.frag"))
    # screen_card.set_shader_input("screen_scale", base.win.properties.getSize())
    # screen_card.set_shader_input("screen_tex", screen_tex)
    # #screen_card.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_one , ColorBlendAttrib.O_one_minus_incoming_alpha))
    # screen_card.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha , ColorBlendAttrib.O_one))
    #base.win.set_clear_color_active(True)
    
    base.accept("escape", base.userExit)
    
    def rotate_cam(task):
        base.cam.set_pos(np.sin(2.*np.pi/3.+task.frame/200.)*(row_len/2.) + (row_len/2.),
            -np.cos(2.*np.pi/3.+task.frame/400.)*((NUM_VERTS//row_len)//2.) + 40.,np.cos(task.frame/800.)*3. + 2.)
        base.cam.look_at((row_len/2., (NUM_VERTS//row_len)//2., 0.))
        return task.cont

    #base.taskMgr.add(rotate_cam, "rotate-camera")

    base.cam.set_pos(row_len/2., -8., 1.)
    base.cam.look_at(row_len/2., (NUM_VERTS//row_len)//2., 0.)

    base.run()