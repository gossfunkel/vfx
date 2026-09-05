from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, GeomNode, Geom, GeomEnums, ModelRoot,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, GeomLines,
    BoundingVolume, BoundingBox, ComputeNode, ColorBlendAttrib, CardMaker,
    Shader, ShaderBuffer, Texture, SamplerState, ShaderAttrib
)
import numpy as np

NUM_SPRITES = 16
DIM_LEN = 5
NUM_CELLS = DIM_LEN**3
sprite_floats = 8

CONFIG = """
win-size 1920 1040
gl-version 4 3
gl-debug true
gl-debug-buffers true
gl-force-glsl-version 430 // required for ssbo format
framebuffer-srgb true
"""
load_prc_file_data('', CONFIG)

@dataclass
class TreeNode():
    children: List[TreeNode]
    num_members: int = 0
    members: List[int]
    centre: Vec3
    radius: float

    def __init__(self, centre, rad):
        self.centre = centre
        self.radius = rad

    def add_sprite(self, idx: int, pos: Vec3):
        if (len(self.children) > 0):
            if (pos.x > self.centre.x):
                if (pos.y > self.centre.y):
                    if (pos.z > self.centre.z):
                        self.children[7].addSprite(idx, pos)
                    else:
                        self.children[3].addSprite(idx, pos)
                else:
                    if (pos.z > self.centre.z):
                        self.children[5].addSprite(idx, pos)
                    else:
                        self.children[1].addSprite(idx, pos)
            else:
                if (pos.y > self.centre.y):
                    if (pos.z > self.centre.z):
                        self.children[6].addSprite(idx, pos)
                    else:
                        self.children[2].addSprite(idx, pos)
                else:
                    if (pos.z > self.centre.z):
                        self.children[4].addSprite(idx, pos)
                    else:
                        self.children[0].addSprite(idx, pos)
        else:
            if ((self.centre - pos) > (self.radius/2.)):
                self.split()
                self.addSprite(idx, pos)
            else:
                self.members[self.num_members] = idx
                self.num_members += 1

    def split(self):
        child_radius = self.radius / 2.
        for child in range(8):
            self.children[child] = TreeNode(self.centre + Vec3(((child%2)*2 - 1) * child_radius,
                                                                ((child//2)*2 - 1) * child_radius,
                                                                ((child//4)*2 - 1) * child_radius), 
                                            child_radius)

    def to_string(self, outstr):
        outstr += f"|{self.num_members} "
        for memb in self.members:
            outstr += f"{memb} "
        if (len(self.children) > 0):
            outstr += ":1 "
            for child in self.children:
                child.to_string(outstr)
        else:
            outstr += ":0 "

base_tree = TreeNode(Vec3(DIM_LEN/2.,DIM_LEN/2.,DIM_LEN/2.), DIM_LEN/2.)

def rebuildTree(task, cell_ssbo, sprite_ssbo):
    root = base_tree
    for idx in range(NUM_SPRITES):
        root.add_sprite(idx, Vec3(sprite_ssbo[idx*sprite_floats:idx*sprite_floats+2]))
    cell_ssbo = root.to_string().tobytes()

if __name__ == "__main__":
    ShowBase()
    base.set_background_color(0.,0.,0.,1.)
    
    raw_sprite_data = np.zeros(sprite_floats*NUM_SPRITES, dtype=np.float32)
    for idx in range(NUM_SPRITES):
        raw_sprite_data[idx*sprite_floats] = (idx // 4) % 2 + .5          # x
        raw_sprite_data[idx*sprite_floats+1] = idx % 4 + .5               # y
        raw_sprite_data[idx*sprite_floats+2] = idx // 2 + .5              # z
        raw_sprite_data[idx*sprite_floats+3] = 1.                         # mass
        raw_sprite_data[idx*sprite_floats+7] = .5                         # size

    sprite_ssbo = ShaderBuffer('sprite_buff', raw_sprite_data.tobytes(), GeomEnums.UHStatic)

    cell_floats = 12
    raw_cell_data = np.zeros(cell_floats*NUM_SPRITES, dtype=np.float32)
    for idx in range(NUM_CELLS):
        raw_cell_data[idx*cell_floats] = idx // DIM_LEN*DIM_LEN
    cell_ssbo = ShaderBuffer('cell_buff', raw_cell_data.tobytes(), GeomEnums.UHStatic)

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

    pt_shader = Shader.load(Shader.SL_GLSL, "grav.vert", "grav.frag")
    pt_np = base.render.attach_new_node(tri_geom_node)
    pt_np.set_shader(pt_shader)
    pt_np.set_shader_input("num_sprites", NUM_SPRITES)
    pt_np.set_shader_input("vert_buff", ssbo)
    pt_np.set_texture(sprite_tex)
    pt_np.set_two_sided(True)
    pt_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    pt_np.set_depth_write(False)
    pt_np.node().set_bounds_type(BoundingVolume.BT_box)

    map_cnode = ComputeNode("map")
    map_cnode.add_dispatch(NUM_SPRITES // 16, 4, 1)
    map_comp_np = base.render.attach_new_node(map_cnode)
    map_comp_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "map.comp"))
    map_comp_np.set_shader_input("sprite_buff", sprite_ssbo)
    map_comp_np.set_shader_input("cell_buff", cell_ssbo)

    phys_cnode = ComputeNode("phys")
    phys_cnode.add_dispatch(NUM_CELLS // 4, NUM_CELLS // 4, 1)
    phys_comp_np = base.render.attach_new_node(phys_cnode)
    phys_comp_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "grav.comp"))
    phys_comp_np.set_shader_input("sprite_buff", sprite_ssbo)
    phys_comp_np.set_shader_input("cell_buff", cell_ssbo)

    move_cnode = ComputeNode("move")
    move_cnode.add_dispatch(NUM_SPRITES // 16, 4, 1)
    move_comp_np = base.render.attach_new_node(move_cnode)
    move_comp_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "move.comp"))
    move_comp_np.set_shader_input("sprite_buff", sprite_ssbo)
    move_comp_np.set_shader_input("cell_buff", cell_ssbo)

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
    
    # def rotate_cam(task):
    #     base.cam.set_pos(np.sin(task.frame/400.)*(NUM_SPRITES/2.) + (NUM_SPRITES/4.),
    #         -np.cos(task.frame/400.)*(NUM_SPRITES/2.) + (NUM_SPRITES/4.),
    #         np.cos(task.frame/800.)*row_len + 1.)
    #     base.cam.look_at((row_len/2., NUM_SPRITES/4.,row_len/2.))
    #     return task.cont

    # base.taskMgr.add(rotate_cam, "rotate-camera")

    base.cam.set_pos(2., -5., 1.)
    base.cam.look_at(2., 2., 2.)

    base.run()