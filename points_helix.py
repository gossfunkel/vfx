from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, GeomNode, Geom, GeomEnums, ModelRoot,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, GeomLines,
    BoundingVolume, BoundingBox, ComputeNode, ColorBlendAttrib, CardMaker,
    Shader, ShaderBuffer, Texture, SamplerState, ShaderAttrib
)
import numpy as np

NUM_SPRITES = 512

CONFIG = """
win-size 1920 1040
gl-version 4 3
gl-debug true
gl-debug-buffers true
gl-force-glsl-version 430 // required for ssbo format
framebuffer-srgb true
"""
load_prc_file_data('', CONFIG)

if __name__ == "__main__":
    ShowBase()
    base.set_background_color(0.,0.,0.,1.)

    row_len = 16

    raw_ssbo_data = np.zeros(4*NUM_SPRITES, dtype=np.float32)
    for idx in range(NUM_SPRITES):
        raw_ssbo_data[idx*4] = row_len                 # x
        raw_ssbo_data[idx*4+1] = idx%(NUM_SPRITES//2)               # y
        raw_ssbo_data[idx*4+2] = row_len                     # z

    ssbo = ShaderBuffer('sprites', raw_ssbo_data.tobytes(), GeomEnums.UHStatic)

    vtx_format = GeomVertexFormat.get_empty()
    vtx_data = GeomVertexData('sprites', vtx_format, GeomEnums.UH_static)

    geom_tris = GeomTriangles(GeomEnums.UH_static)
    geom_tris.add_next_vertices(NUM_SPRITES * 3)

    geom_lines = GeomLines(GeomEnums.UH_static)
    for idx in range(NUM_SPRITES//2):
        geom_lines.add_vertex(idx)
        geom_lines.add_vertex(NUM_SPRITES//2 + idx)

    tri_geom = Geom(vtx_data)
    tri_geom.add_primitive(geom_tris)
    tri_geom.set_bounds(BoundingBox((-1, -1, -1), (100, 100, 100)))

    tri_geom_node = GeomNode("tri_gnode")
    tri_geom_node.add_geom(tri_geom)

    line_geom = Geom(vtx_data)
    line_geom.add_primitive(geom_lines)
    line_geom.set_bounds(BoundingBox((-1, -1, -1), (100, 100, 100)))

    line_geom_node = GeomNode("line_gnode")
    line_geom_node.add_geom(line_geom)

    sprite_tex = loader.load_texture("grid_sprite.png")
    sprite_tex.wrap_u = SamplerState.WM_clamp
    sprite_tex.wrap_v = SamplerState.WM_clamp

    pt_shader = Shader.load(Shader.SL_GLSL, "points_helix.vert", "points_helix.frag")
    pt_np = base.render.attach_new_node(tri_geom_node)
    pt_np.set_shader(pt_shader)
    pt_np.set_shader_input("num_sprites", NUM_SPRITES)
    pt_np.set_shader_input("vert_buff", ssbo)
    pt_np.set_texture(sprite_tex)
    pt_np.set_two_sided(True)
    pt_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    pt_np.set_depth_write(False)
    pt_np.node().set_bounds_type(BoundingVolume.BT_box)

    line_shader = Shader.load(Shader.SL_GLSL, "lines_helix.vert", "lines_helix.frag")
    line_np = base.render.attach_new_node(line_geom_node)
    line_np.set_shader(line_shader)
    line_np.set_shader_input("vert_buff", ssbo)
    line_np.set_two_sided(True)
    line_np.set_depth_write(False)
    line_np.node().set_bounds_type(BoundingVolume.BT_box)

    # compute_node = ComputeNode("compute")
    # compute_node.add_dispatch(NUM_VERTS // 64, 4, 1)
    # compute_np = base.render.attach_new_node(compute_node)
    # compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "mesh.comp"))
    # compute_np.set_shader_input("vert_buff", ssbo)
    # compute_np.set_shader_input("num_verts", NUM_VERTS)

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
        base.cam.set_pos(np.sin(task.frame/200.)*(NUM_SPRITES/2.) + (NUM_SPRITES/2.),
            -np.cos(task.frame/200.)*(NUM_SPRITES/2.) + (NUM_SPRITES/2.),
            np.cos(task.frame/800.)*row_len + 1.)
        base.cam.look_at((row_len/2., NUM_SPRITES/4.,row_len/2.))
        return task.cont

    base.taskMgr.add(rotate_cam, "rotate-camera")

    base.cam.set_pos(row_len/2., -32., row_len/2. + 1.)
    base.cam.look_at(row_len/2., 0., row_len/2.)

    base.run()