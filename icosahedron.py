from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, GeomNode, Geom, GeomEnums, ModelRoot,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, 
    BoundingVolume, BoundingBox, ComputeNode, ColorBlendAttrib, 
    Shader, ShaderBuffer, Texture, SamplerState, ShaderAttrib
)
import numpy as np

TAU = 6.2831853

CONFIG = """
win-size 1920 1040
gl-version 4 3
load-display pandagl
gl-debug true
gl-debug-buffers true
gl-force-glsl-version 430 // required for ssbo format
framebuffer-srgb true
hardware-animated-vertices true
basic-shaders-only false
"""
load_prc_file_data('', CONFIG)

if __name__ == "__main__":
    ShowBase()
    base.set_background_color(0.,0.,0.,1.)

    num_verts = 12
    raw_ssbo_data = np.zeros(4*num_verts, dtype=np.float32)

    φ = (1. + np.sqrt(5.))/2.
    for combination in range(3):
        for vtx in range(4):
            raw_ssbo_data[vtx*4 + combination*17] = (1. - 2*(vtx//2))
            raw_ssbo_data[vtx*4 + combination*16 + ((combination+1)%3)] = (1. - 2*(vtx%2)) * φ

    ssbo = ShaderBuffer('ssbo_sprites', raw_ssbo_data.tobytes(), GeomEnums.UHStatic)

    vtx_format = GeomVertexFormat.get_empty()
    vtx_data = GeomVertexData('vbo_sprites', vtx_format, GeomEnums.UH_static)

    #num_tris = (num_sectors-2)*2*(num_stacks-2) + num_stacks*2
    geom_tris = GeomTriangles(GeomEnums.UH_static)
    for vtx_set in range(3):
        next_set = (vtx_set+1)%3
        prev_set = (vtx_set+2)%3
        geom_tris.add_vertex(vtx_set*4)
        geom_tris.add_vertex(next_set*4 + 1)
        geom_tris.add_vertex(next_set*4)
        geom_tris.add_vertex(vtx_set*4)
        geom_tris.add_vertex(vtx_set*4+1)
        geom_tris.add_vertex(prev_set*4)
        geom_tris.add_vertex(vtx_set*4)
        geom_tris.add_vertex(prev_set*4+2)
        geom_tris.add_vertex(vtx_set*4+1)
        geom_tris.add_vertex(vtx_set*4+1)
        geom_tris.add_vertex(next_set*4+2)
        geom_tris.add_vertex(next_set*4+3)
        # geom_tris.add_vertex((((vtx_set+1)*4)%num_verts)+2)
        # geom_tris.add_vertex((((vtx_set+1)*4)%num_verts)+3)
    geom_tris.close_primitive()

    geom = Geom(vtx_data)
    geom.add_primitive(geom_tris)
    geom.set_bounds(BoundingBox((-1, -1, -1), (100, 100, 100)))

    geom_node = GeomNode("gnode")
    geom_node.add_geom(geom)

    mesh_shader = Shader.load(Shader.SL_GLSL, "icosahedron.vert", "icosahedron.frag")
    mesh_np = base.render.attach_new_node(geom_node)
    mesh_np.set_shader(mesh_shader)
    mesh_np.set_shader_input("vert_buff", ssbo)
    mesh_np.set_shader_input("num_verts", num_verts)
    mesh_np.set_two_sided(True)
    mesh_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    mesh_np.set_depth_write(False)
    #mesh_np.set_depth_offset(3)
    mesh_np.node().set_bounds_type(BoundingVolume.BT_box)

    compute_node = ComputeNode("compute")
    compute_node.add_dispatch(1, 1, 1)
    compute_np = base.render.attach_new_node(compute_node)
    compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "icosahedron.comp"))
    compute_np.set_shader_input("vert_buff", ssbo)
    compute_np.set_shader_input("num_verts", num_verts)
    
    base.accept("escape", base.userExit)
    
    def rotate_cam(task):
        base.cam.set_pos(np.sin(task.frame/200.)*5.,
            -np.cos(2.*np.pi+task.frame/200.)*5.,np.cos(task.frame/800.)*3. + 2.)
        base.cam.look_at((0., 0., 0.))
        return task.cont

    base.taskMgr.add(rotate_cam, "rotate-camera")

    #base.cam.set_pos(0., -6. * sphere_rad, 5.)
    #base.cam.look_at(0., 0., 1.)

    base.run()