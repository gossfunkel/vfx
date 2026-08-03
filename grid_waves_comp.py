from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, Shader, GeomNode, GeomPoints, 
    Geom, GeomEnums, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    GeomTriangles, BoundingVolume, ComputeNode, ColorBlendAttrib, CardMaker,
    ModelRoot, BoundingBox, ShaderBuffer, Texture, SamplerState, ShaderAttrib
)
import numpy as np

NUM_SPRITES = 16000

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

    raw_ssbo_data = np.zeros(4*NUM_SPRITES, dtype=np.float32)
    for idx in range(NUM_SPRITES):
        raw_ssbo_data[idx*4] = idx/160.                 # x
        raw_ssbo_data[idx*4+1] = idx%160.               # y
        #raw_ssbo_data[idx*4+2] =  .3 + .2 * np.sin(idx)    # z
        raw_ssbo_data[idx*4+2] = 0.                     # z
        raw_ssbo_data[idx*4+3] = 0.                     # potential
        #np.sin((idx%640) - (idx/640))*.1 # potential

    ssbo = ShaderBuffer('sprites', raw_ssbo_data.tobytes(), GeomEnums.UHStatic)

    vtx_format = GeomVertexFormat.get_empty()
    vtx_data = GeomVertexData('sprites', vtx_format, GeomEnums.UH_static)

    geom_tris = GeomTriangles(GeomEnums.UH_static)
    geom_tris.add_next_vertices(NUM_SPRITES * 3)

    geom = Geom(vtx_data)
    geom.add_primitive(geom_tris)
    geom.set_bounds(BoundingBox((-1, -1, -1), (100, 100, 100)))

    geom_node = GeomNode("gnode")
    geom_node.add_geom(geom)

    sprite_tex = loader.load_texture("grid_sprite.png")
    sprite_tex.wrap_u = SamplerState.WM_clamp
    sprite_tex.wrap_v = SamplerState.WM_clamp

    sprite_shader = Shader.load(Shader.SL_GLSL, "grid_sprites.vert", "grid_sprites.frag")
    sprite_np = base.render.attach_new_node(geom_node)
    sprite_np.set_shader(sprite_shader)
    sprite_np.set_shader_input("sprite_buff", ssbo)
    sprite_np.set_texture(sprite_tex)
    sprite_np.set_two_sided(True)
    sprite_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    sprite_np.set_depth_write(False)
    sprite_np.node().set_bounds_type(BoundingVolume.BT_box)

    compute_node = ComputeNode("compute")
    compute_node.add_dispatch(NUM_SPRITES // 16, NUM_SPRITES // 16, 1)
    compute_np = base.render.attach_new_node(compute_node)
    compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "grid_waves.comp"))
    compute_np.set_shader_input("sprite_buff", ssbo)
    compute_np.set_shader_input("num_sprites", NUM_SPRITES)

    filter_mgr = FilterManager(base.win, base.cam)
    #filter_mgr.resizeBuffers()
    #filter_mgr.windowEvent(base.win)
    screen_tex = Texture()
    screen_tex.setMagfilter(SamplerState.FT_nearest)
    screen_tex.setMinfilter(SamplerState.FT_nearest)
    #screen_tex.setMatchFramebufferFormat()
    screen_card = filter_mgr.renderSceneInto(colortex=screen_tex)
    screen_tex.set_format(Texture.F_srgb_alpha)
    screen_card.set_shader(Shader.load(Shader.SL_GLSL, vertex="quad.vert", fragment="screen_filter.frag"))
    screen_card.set_shader_input("screen_scale", base.win.properties.getSize())
    screen_card.set_shader_input("screen_tex", screen_tex)
    #screen_card.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_one , ColorBlendAttrib.O_one_minus_incoming_alpha))
    screen_card.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha , ColorBlendAttrib.O_one))

    base.win.set_clear_color_active(True)

    base.cam.set_pos(20., -10., 1.5)
    base.cam.set_hpr(0.,-5.,0.)
    #base.cam.look_at(sprite_np)

    base.accept("escape", base.userExit)

    base.run()