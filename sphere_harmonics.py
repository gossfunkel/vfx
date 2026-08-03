from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, Shader, GeomNode, GeomPoints, 
    Geom, GeomEnums, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    GeomTriangles, BoundingVolume, ComputeNode, ColorBlendAttrib, CardMaker,
    ModelRoot, BoundingBox, ShaderBuffer, Texture, SamplerState, ShaderAttrib
)
import numpy as np
import scipy.io.wavfile as sp
import sounddevice as sd
import struct

NUM_SPRITES = 32568

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

    filename="test_tone.wav"

    with open(filename, 'rb') as wav_file:
        header_beginning = wav_file.read(0x18)
        # TODO: get bit depth from header
        num_channels = struct.unpack_from('<H', header_beginning, 0x16)[0]

    sample_rate, base.audio = sp.read(filename)

    device = sd.default.device
    print(f"== Initialising stream with {num_channels} channels at {sample_rate}Hz, " +
           f"default device ({device}) set")
    base.stream = sd.OutputStream(samplerate=sample_rate, device=device, channels=num_channels, 
                                  dtype=np.float32)
    base.stream.start()

    fft_out = np.array([])

    for chunk in range(len(base.audio)//NUM_SPRITES):
        np.append(fft_out,np.fft.fft(base.audio[chunk*NUM_SPRITES:], n=NUM_SPRITES))

    audio_ssbo = ShaderBuffer("audio_buff", np.real(fft_out).astype(np.float32).tobytes(), GeomEnums.UHStatic)

    raw_sprite_data = np.zeros(4*NUM_SPRITES, dtype=np.float32)

    sprite_ssbo = ShaderBuffer('sprites', raw_sprite_data.tobytes(), GeomEnums.UHStatic)

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

    sprite_shader = Shader.load(Shader.SL_GLSL, "sphere_harmonics_sprites.vert", "sphere_harmonics_sprites.frag")
    sprite_np = base.render.attach_new_node(geom_node)
    sprite_np.set_shader(sprite_shader)
    sprite_np.set_shader_input("sprite_buff", sprite_ssbo)
    sprite_np.set_shader_input("num_sprites", NUM_SPRITES)
    sprite_np.set_texture(sprite_tex)
    sprite_np.set_two_sided(True)
    sprite_np.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    sprite_np.set_depth_write(False)
    sprite_np.node().set_bounds_type(BoundingVolume.BT_box)

    compute_node = ComputeNode("compute")
    compute_node.add_dispatch(NUM_SPRITES // 64, 4, 1)
    compute_np = base.render.attach_new_node(compute_node)
    compute_np.set_shader(Shader.load_compute(Shader.SL_GLSL, "sphere_harmonics.comp"))
    compute_np.set_shader_input("num_sprites", NUM_SPRITES)
    compute_np.set_shader_input("audio_len", len(fft_out))
    compute_np.set_shader_input("sprite_buff", sprite_ssbo)
    compute_np.set_shader_input("audio_buff", audio_ssbo)

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

    #base.cam.set_pos(16., -10., 2.5)
    #base.cam.set_hpr(0.,-5.,0.)
    
    base.accept("escape", base.userExit)
    
    def rotate_cam(task):
        base.cam.set_pos(np.sin(task.frame/400.)*32. + 32.,-np.cos(task.frame/400.)*64. - 32.,np.cos(task.frame/800.)*16. + 18.)
        base.cam.look_at((16., 16., 16.))
        return task.cont

    base.taskMgr.add(rotate_cam, "rotate-camera")

    def call_play_audio(task):                                          # panda3d task to feed the audio buffer
        remaining = base.stream.write_available
        if remaining < len(base.audio):
            base.stream.write(base.audio[:remaining])
            base.audio = base.audio[remaining:]
            return task.cont
        else:
            base.stream.write(base.audio)
            print("== Stopping stream")
            base.stream.stop()
            return task.done

    print(f"== Playing file {filename}; {base.audio.shape[0]/sample_rate}s duration...")
    taskMgr.add(call_play_audio, "play_audio")

    base.run()