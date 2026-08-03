from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, Shader, GeomNode, GeomPoints, CullBinManager,
    Geom, GeomEnums, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    GeomTriangles, BoundingVolume, ComputeNode, ColorBlendAttrib, CardMaker,
    ModelRoot, BoundingBox, ShaderBuffer, Texture, SamplerState, ShaderAttrib
)
import numpy as np

# must be multiple of 4
NUM_SPRITES = 1024

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

    bin_mgr: CullBinManager = CullBinManager.get_global_ptr()
    bin_mgr.add_bin("motion_bin", CullBinManager.BT_fixed, 1)

    base.set_background_color(0.,0.,0.,1.)
    sprite_floats = 5*4 # 5x vec3 (4x 32b floats)
    ROW_WIDTH = 16
    # 20 floats per spritze:
    # nbr0   | nbr1   | nbr2   | xxxx |
    # pos_0x | pos_0y | pos_0z | xxxx |
    # pos_1x | pos_1y | pos_1z | xxxx |
    # velx   | vely   | velz   | xxxx |
    # forcex | forcey | forcez | xxxx |
    raw_ssbo_data = np.zeros(sprite_floats*NUM_SPRITES, dtype=np.float32)
    for set in range(NUM_SPRITES//4):
        set_start = sprite_floats*4*set # idx of start of bloc of four sprites
        for sprite in range(4):
            spr_start = sprite_floats*sprite + set_start # idx of start of sprite struct
            raw_ssbo_data[spr_start+4] = 6.*(set%ROW_WIDTH) + (sprite//2)*3. # xpos
            if (sprite == 0):
                raw_ssbo_data[spr_start+5] = 18.*(set//ROW_WIDTH)       # ypos
                raw_ssbo_data[spr_start] = set_start + 1.               # neighbours
                raw_ssbo_data[spr_start+1] = ((set_start-(ROW_WIDTH-1))%NUM_SPRITES)*4. + 2.
                raw_ssbo_data[spr_start+2] = ((set_start-ROW_WIDTH)%NUM_SPRITES)*4. + 2.
            elif (sprite == 1): 
                raw_ssbo_data[spr_start+5] = 18.*(set//ROW_WIDTH) + 5.  #ypos
                raw_ssbo_data[spr_start+14] = .5                        #zvel
                raw_ssbo_data[spr_start] = np.float32(set_start)        # neighbours
                raw_ssbo_data[spr_start+1] = ((set-1)%(NUM_SPRITES//4))*4. + 2.
                raw_ssbo_data[spr_start+2] = set_start + 2.
            elif (sprite == 2): 
                raw_ssbo_data[spr_start+5] = 18.*(set//ROW_WIDTH) + 9.  #ypos
                raw_ssbo_data[spr_start+14] = -.5                       #zvel
                raw_ssbo_data[spr_start] = set_start + 3.               # neighbours
                raw_ssbo_data[spr_start+1] = set_start + 1.
                raw_ssbo_data[spr_start+2] = ((set-1)%(NUM_SPRITES//4))*4. + 1.
            elif (sprite == 3): 
                raw_ssbo_data[spr_start+5] = 18.*(set//ROW_WIDTH) + 14. #ypos
                raw_ssbo_data[spr_start] = set_start + 2.               # neighbours
                raw_ssbo_data[spr_start+1] = ((set+ROW_WIDTH)%(NUM_SPRITES//4))*4. + 2.
                raw_ssbo_data[spr_start+2] = ((set+ROW_WIDTH+1)%(NUM_SPRITES//4))*4. + 2.

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

    sprite_shader = Shader.load(Shader.SL_GLSL, "hex_sprites.vert", "hexgrid.frag")
    sprite_np = base.render.attach_new_node(geom_node)
    sprite_np.set_shader(sprite_shader)
    sprite_np.set_shader_input("sprite_buff", ssbo)
    sprite_np.set_texture(sprite_tex)
    sprite_np.set_two_sided(True)
    sprite_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    sprite_np.set_depth_write(False)
    sprite_np.node().set_bounds_type(BoundingVolume.BT_box)

    # pass 1: estimate the instantaneous force on sprite and estimate motion of sprite across timestep
    comp_p1_node = ComputeNode("comp_pass_1")
    comp_p1_node.add_dispatch(NUM_SPRITES // 16, 16, 1)
    comp_p1_np = base.render.attach_new_node(comp_p1_node)
    comp_p1_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "hex_pass_1.comp"))
    comp_p1_np.set_shader_input("sprite_buff", ssbo)
    comp_p1_np.set_shader_input("num_sprites", NUM_SPRITES)
    comp_p1_np.set_bin("motion_bin", 10)

    # pass 2: re-estimate force at end of timestep with new position estimates, integrate velocity change across timestep and re-integrate motion of sprite
    comp_p2_node = ComputeNode("comp_pass_2")
    comp_p2_node.add_dispatch(NUM_SPRITES // 16, 16, 1)
    compute_np = base.render.attach_new_node(comp_p2_node)
    compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "hex_pass_2.comp"))
    compute_np.set_shader_input("sprite_buff", ssbo)
    compute_np.set_shader_input("num_sprites", NUM_SPRITES)
    comp_p1_np.set_bin("motion_bin", 15)

    # pass 3: calculate force at end of step based on new sprite positions and integrate velocity change and motion of sprite
    comp_p2_node = ComputeNode("comp_pass_3")
    comp_p2_node.add_dispatch(NUM_SPRITES // 16, 16, 1)
    compute_np = base.render.attach_new_node(comp_p2_node)
    compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "hex_pass_3.comp"))
    compute_np.set_shader_input("sprite_buff", ssbo)
    compute_np.set_shader_input("num_sprites", NUM_SPRITES)
    comp_p1_np.set_bin("motion_bin", 20)

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

    base.cam.set_pos(67.5, -50., 1.5)
    base.cam.set_hpr(5.,-5.,0.)
    #base.cam.look_at(sprite_np)

    base.accept("escape", base.userExit)

    base.run()