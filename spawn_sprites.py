from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, GeomNode, Geom, GeomEnums, ModelRoot,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, GeomLines,
    BoundingVolume, BoundingBox, ComputeNode, ColorBlendAttrib, CardMaker,
    Shader, ShaderBuffer, Texture, SamplerState, ShaderAttrib, CullBinManager
)
import numpy as np

NUM_SPRITES = 256
# Merton codes indexing 2**10 cells per dimension
NUM_CELLS = ((2**10)*3)
resolution  = 100.

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
    rng = np.random.default_rng()

    ShowBase()
    
    base.set_background_color(0.,0.,0.,1.)

    bin_mgr = CullBinManager.get_global_ptr()
    bin_mgr.add_bin("hash_bin", CullBinManager.BT_fixed, 10)
    bin_mgr.add_bin("phys_bin", CullBinManager.BT_fixed, 20)
    bin_mgr.add_bin('copy_bin', CullBinManager.BT_fixed, 30)

    spr_struct_floats = 8 # pos, vel
    raw_ssbo_data = np.zeros(spr_struct_floats*NUM_SPRITES, dtype=np.float32)
    for sprite_idx in range(NUM_SPRITES):
        raw_ssbo_data[sprite_idx*spr_struct_floats] = rng.random() - .5
        raw_ssbo_data[sprite_idx*spr_struct_floats+1] = rng.random() - .5
        raw_ssbo_data[sprite_idx*spr_struct_floats+2] = rng.random() - .5

    ssbo_A = ShaderBuffer('sprites_A', raw_ssbo_data.tobytes(), GeomEnums.UHStatic) # TODO dynamic?
    ssbo_B = ShaderBuffer('sprites_B', raw_ssbo_data.tobytes(), GeomEnums.UHStatic)

    # TODO properly format struct with cell positions
    raw_cell_data = np.zeros(8*NUM_CELLS, dtype=np.float32)
    for cell in range(NUM_CELLS):
        raw_cell_data[cell*8] = cell+.5
        raw_cell_data[cell*8+1] = cell+.5
        raw_cell_data[cell*8+2] = cell+.5
    ssbo_cells = ShaderBuffer('cells', raw_cell_data.tobytes(), GeomEnums.UHStatic)

    vtx_format = GeomVertexFormat.get_empty()
    vtx_data = GeomVertexData('sprites', vtx_format, GeomEnums.UH_static)

    geom_tris = GeomTriangles(GeomEnums.UH_static)
    geom_tris.add_next_vertices(NUM_SPRITES * 3)

    tri_geom = Geom(vtx_data)
    tri_geom.add_primitive(geom_tris)
    tri_geom.set_bounds(BoundingBox((-1, -1, -1), (100, 100, 100)))

    tri_geom_node = GeomNode("tri_gnode")
    tri_geom_node.add_geom(tri_geom)

    sprite_tex = loader.load_texture("grid_sprite.png")
    sprite_tex.wrap_u = SamplerState.WM_clamp
    sprite_tex.wrap_v = SamplerState.WM_clamp

    spr_shader = Shader.load(Shader.SL_GLSL, "spawn_sprite.vert", "spawn_sprite.frag")
    spr_np = base.render.attach_new_node(tri_geom_node)
    spr_np.set_shader(spr_shader)
    spr_np.set_shader_input("num_sprites", NUM_SPRITES)
    spr_np.set_shader_input("vert_buff", ssbo_B)
    spr_np.set_texture(sprite_tex)
    spr_np.set_two_sided(True)
    spr_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    spr_np.set_depth_write(False)
    spr_np.node().set_bounds_type(BoundingVolume.BT_box)

    # layout of 4x4 invocations, blocs 4 dispatches wide
    INV_BLOCS = 4*4*4

    hash_node = ComputeNode("space_hash")
    hash_node.add_dispatch(NUM_SPRITES // INV_BLOCS, 4, 1)
    hash_np = base.render.attach_new_node(hash_node)
    hash_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "hash.comp"))
    hash_np.set_shader_input("sprite_buff", ssbo_A)
    hash_np.set_shader_input("cell_buff", ssbo_cells)
    hash_np.set_shader_input("num_sprites", NUM_SPRITES)
    hash_np.set_shader_input("res", resolution)
    hash_np.set_bin('hash_bin', 15)

    phys_comp = ComputeNode("compute")
    phys_comp.add_dispatch(NUM_SPRITES // INV_BLOCS, 4, 1)
    phys_np = base.render.attach_new_node(phys_comp)
    phys_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "spawn_sprite.comp"))
    phys_np.set_shader_input("sprite_buff_in", ssbo_A)
    phys_np.set_shader_input("sprite_buff_out", ssbo_B)
    phys_np.set_shader_input("cell_buff", ssbo_cells)
    phys_np.set_shader_input("num_sprites", NUM_SPRITES)
    phys_np.set_bin('phys_bin', 25)

    copy_node = ComputeNode("bcopy")
    copy_node.add_dispatch(NUM_SPRITES // INV_BLOCS, 4, 1)
    copy_np = base.render.attach_new_node(copy_node)
    copy_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "copy.comp"))
    copy_np.set_shader_input("sprite_buff_B", ssbo_B)
    copy_np.set_shader_input("sprite_buff_A", ssbo_A)
    phys_np.set_shader_input("cell_buff", ssbo_cells)
    copy_np.set_shader_input("num_sprites", NUM_SPRITES)
    copy_np.set_bin('copy_bin', 35)

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
        base.cam.set_pos(np.sin(task.frame/400.)*64.,
            -np.cos(task.frame/400.)*64.,
            np.cos(task.frame/800.)*16. + 8.)
        base.cam.look_at((0., 0., 0.))
        return task.cont

    base.taskMgr.add(rotate_cam, "rotate-camera")

    base.cam.set_pos(0., -64., 16.)
    base.cam.look_at(0., 0., 0.)

    base.run()