from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, GeomNode, Geom, GeomEnums, ModelRoot,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, 
    BoundingVolume, BoundingBox, ComputeNode, ColorBlendAttrib, CardMaker,
    Shader, ShaderBuffer, Texture, SamplerState, ShaderAttrib, 
    Material, DirectionalLight, AmbientLight
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

    sphere_rad = 32
    num_stacks = 25
    num_sectors = 25
    sector_len = TAU / num_sectors;
    stack_len = (TAU/2.) / num_stacks;
    num_verts = num_stacks + (num_stacks - 2) * (num_sectors - 1)
    raw_ssbo_data = np.zeros(4*num_verts, dtype=np.float32)

    idx = 1
    for stack in range(num_stacks):
        theta = TAU / 4. - stack * stack_len;
        xy = sphere_rad * np.cos(theta)
        zpos = sphere_rad * np.sin(theta);
        if (stack == 0):
            raw_ssbo_data[0] = 0.
            raw_ssbo_data[1] = 0.
            raw_ssbo_data[2] = zpos
        elif (stack == num_stacks - 1):
            raw_ssbo_data[(num_verts-1)*4] = 0.
            raw_ssbo_data[(num_verts-1)*4 + 1] = 0.
            raw_ssbo_data[(num_verts-1)*4 + 2] = zpos
        else:
            for sector in range(num_sectors):
                phi = sector * sector_len;
                raw_ssbo_data[idx*4] = xy * np.cos(phi); # r * cos(u) * cos(v)
                raw_ssbo_data[idx*4+1] = xy * np.sin(phi);
                raw_ssbo_data[idx*4+2] = zpos
                idx += 1

    ssbo = ShaderBuffer('ssbo_sprites', raw_ssbo_data.tobytes(), GeomEnums.UHStatic)

    vtx_format = GeomVertexFormat.get_empty()
    vtx_data = GeomVertexData('vbo_sprites', vtx_format, GeomEnums.UH_static)

    #num_tris = (num_sectors-2)*2*(num_stacks-2) + num_stacks*2
    geom_tris = GeomTriangles(GeomEnums.UH_static)
    for stack in range(num_stacks-1):
        for sector in range(num_sectors):
            if (stack == 0):
                geom_tris.add_vertex(0)
                geom_tris.add_vertex(1 + sector)
                if (sector == num_sectors-1):
                    geom_tris.add_vertex(1)
                else:
                    geom_tris.add_vertex(2 + sector)
            elif (stack == num_stacks-2):
                geom_tris.add_vertex(num_verts-1)
                if (sector == num_sectors-1):
                    geom_tris.add_vertex(1 + (stack-1)*num_sectors)
                else:
                    geom_tris.add_vertex(2 + (stack-1)*num_sectors + sector)
                geom_tris.add_vertex(1 + (stack-1)*num_sectors + sector)
            else:
                geom_tris.add_vertex(1 + (stack-1)*num_sectors + sector)
                geom_tris.add_vertex(1 + stack*num_sectors + sector)
                if (sector == num_sectors-1):
                    geom_tris.add_vertex(1 + (stack-1)*num_sectors)
                    geom_tris.add_vertex(1 + (stack-1)*num_sectors)
                else:
                    geom_tris.add_vertex(2 + (stack-1)*num_sectors + sector)
                    geom_tris.add_vertex(2 + (stack-1)*num_sectors + sector)
                geom_tris.add_vertex(1 + stack*num_sectors + sector)
                if (sector == num_sectors-1):
                    geom_tris.add_vertex(1 + stack*num_sectors)
                else:
                    geom_tris.add_vertex(2 + stack*num_sectors + sector)

    geom = Geom(vtx_data)
    geom.add_primitive(geom_tris)
    geom.set_bounds(BoundingBox((-1, -1, -1), (100, 100, 100)))

    geom_node = GeomNode("gnode")
    geom_node.add_geom(geom)

    metal_mat = Material()
    metal_mat.setShininess(5.0)
    metal_mat.setAmbient((.9, .9, 1., 1.))
    metal_mat.setSpecular((.8,1.,.9,1.))

    mesh_shader = Shader.load(Shader.SL_GLSL, "mesh_sphere.vert", "mesh_sphere.frag")
    mesh_np = base.render.attach_new_node(geom_node)
    mesh_np.set_shader(mesh_shader)
    mesh_np.set_shader_input("vert_buff", ssbo)
    mesh_np.set_shader_input("num_verts", num_verts)
    mesh_np.set_shader_input("num_stacks", num_stacks)
    mesh_np.set_shader_input("num_sectors", num_sectors)
    #mesh_np.set_two_sided(True)
    mesh_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    mesh_np.set_depth_write(True)
    mesh_np.set_depth_offset(3)
    mesh_np.node().set_bounds_type(BoundingVolume.BT_box)
    mesh_np.set_color_off()
    mesh_np.set_material(metal_mat)

    compute_node = ComputeNode("compute")
    compute_node.add_dispatch(num_verts // 64, 4, 1)
    compute_np = base.render.attach_new_node(compute_node)
    compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "mesh_sphere.comp"))
    compute_np.set_shader_input("vert_buff", ssbo)
    compute_np.set_shader_input("sphere_rad", sphere_rad)
    compute_np.set_shader_input("num_verts", num_verts)
    compute_np.set_shader_input("num_stacks", num_stacks)
    compute_np.set_shader_input("num_sectors", num_sectors)

    # TODO set card shader input with light's perspective matrices
    # TODO write shaders
    filter_mgr = FilterManager(base.win, base.cam)
    #filter_mgr.resizeBuffers()
    #filter_mgr.windowEvent(base.win)
    screen_tex = Texture()
    depth_tex = Texture()
    screen_tex.setMagfilter(SamplerState.FT_nearest)
    screen_tex.setMinfilter(SamplerState.FT_nearest)
    #screen_tex.setMatchFramebufferFormat()
    screen_card = filter_mgr.renderSceneInto(colortex=screen_tex, depthtex=depth_tex)
    screen_tex.set_format(Texture.F_srgb_alpha)
    screen_card.set_shader(Shader.load(Shader.SL_GLSL, vertex="shadowmap.vert", fragment="shadowmap.frag"))
    screen_card.set_shader_input("screen_scale", base.win.properties.getSize())
    screen_card.set_shader_input("screen_tex", screen_tex)
    #screen_card.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_one , ColorBlendAttrib.O_one_minus_incoming_alpha))
    #screen_card.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha , ColorBlendAttrib.O_one))
    #base.win.set_clear_color_active(True)

    ambient = AmbientLight('ambient')
    ambient.setColor((0.075, 0.12, 0.15, 1))
    ambient_np = render.attachNewNode(ambient)
    render.setLight(ambient_np)

    back_light = DirectionalLight('light')
    back_light.set_color((.9,.6,1.,1.))
    back_light.set_shadow_caster(True, 1024, 1024)
    back_light_np = render.attachNewNode(back_light)
    back_light_np.set_pos(-10.,0., 45.)
    back_light_np.set_hpr(-30.,30.,0.)
    render.set_light(back_light_np)

    render.setShaderAuto()
    
    base.accept("escape", base.userExit)
    
    def rotate_cam(task):
        base.cam.set_pos(np.sin(task.frame/200.)*sphere_rad*6.,
            -np.cos(2.*np.pi+task.frame/200.)*sphere_rad*6.,np.cos(task.frame/800.)*3. + 2.)
        base.cam.look_at((0., 0., 1.))
        return task.cont

    base.taskMgr.add(rotate_cam, "rotate-camera")

    #base.cam.set_pos(0., -6. * sphere_rad, 5.)
    #base.cam.look_at(0., 0., 1.)

    base.run()