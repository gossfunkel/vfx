from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d.core import (
    load_prc_file_data, NodePath, Vec3, Shader, GeomNode, GeomPoints, 
    Geom, GeomEnums, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    ModelRoot, BoundingBox, ShaderBuffer, Texture, SamplerState,
    TransparencyAttrib, TexGenAttrib, ShaderAttrib, ColorBlendAttrib
)
from cam_control import enable_camera_controls
import scipy.io.wavfile as sp
import numpy as np
import sounddevice as sd
import struct, copy

CONFIG = """
win-size 1200 800
gl-version 4 3
load-display pandagl
gl-debug true
gl-debug-buffers true
gl-force-glsl-version 430 // required for ssbo format
gl-support-spirv false    // prevent a specific driver error
hardware-points true
hardware-point-sprites true
singular-points true
framebuffer-srgb true
hardware-animated-vertices true
"""
load_prc_file_data('', CONFIG)

# entry point: this is not to be run from elsewhere
if __name__ == "__main__":
    print("="*14 + " Point Cloud Visualiser " + "="*8)
    filename = input("Please enter filename in local directory:")
    if filename == '': filename = "badhabit.wav" 

    ShowBase()                                                          # base available from here
    base.disableMouse() 

    base.set_background_color(0.,0.,0.,1.)

    # get audio data from file, and examine header
    with open(filename, 'rb') as wav_file:
        header_beginning = wav_file.read(0x18)
        # TODO: get bit depth from header
        num_channels = struct.unpack_from('<H', header_beginning, 0x16)[0]
        
    base.samplerate, base.audio = sp.read(filename)

    # if the audio isn't a multiple of the samplerate, pad it with 0s to allow stream to close cleanly
    padding = len(base.audio) % base.samplerate
    if padding > 0:
        print("== Padding audio to whole buffer size")
        if (num_channels > 2):
            for channel in range(num_channels):
                base.audio[:, channel] = np.append(base.audio[:, channel], np.zeros(padding, dtype=np.int16))
        else:
            np.append(base.audio[:], np.zeros(padding, dtype=np.int16))

    # set up audio output
    device = sd.default.device
    print(f"== Initialising stream with {num_channels} channels at {base.samplerate}Hz, " +
           f"default device ({device}) set")
    base.stream = sd.OutputStream(samplerate=base.samplerate, device=device, channels=num_channels, 
                                  dtype=np.int16)
    base.stream.start()
    print("== Stream running ")

    # prepend a buffer of zeros (plus some for sync) for the visualiser and write to an SSBO
    ssbo = ShaderBuffer("ssbo", np.append(np.zeros(base.samplerate+20), base.audio[:, 1]).tobytes(), 
                        GeomEnums.UHStatic)

    # define how many points we will generate
    num_points = base.samplerate # one per sample for 1s

    # define the size of the scene
    width = 25.
    depth = 100.
    height = 20.
    scale = Vec3(width, depth, height)

    # define VBO
    vtx_format = GeomVertexFormat.getV3c4()
    vtx_data   = GeomVertexData('pts_vbo', vtx_format, Geom.UHStatic)
    vtx_data.set_num_rows(num_points)

    # fill VBO with initial data and create geometry primitives
    vtx_writer = GeomVertexWriter(vtx_data, "vertex")
    col_writer = GeomVertexWriter(vtx_data, "color")
    for quad in range(num_points):
        vtx_writer.add_data3(float(quad)/num_points, 0., 0.)
        col_writer.add_data4(1.,1.,1.,1.)

    # create primitive for mesh
    prim = GeomPoints(Geom.UHStatic)
    prim.add_consecutive_vertices(0, num_points)
    prim.close_primitive()

    # create mesh
    geom = Geom(vtx_data)
    geom.add_primitive(prim)
    geom.set_bounds(BoundingBox((-1.,-1.,-1.), (width+1.,depth+1.,height+1.)))
    node = GeomNode('pts_geomnode')
    node.add_geom(geom)

    # assemble node structure
    root = ModelRoot('pts_root')
    root.add_child(node)
    nodepath = NodePath(root)
    nodepath.reparent_to(base.render)

    # set up additive blending (thanks rdb!)
    #nodepath.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_incoming_alpha, ColorBlendAttrib.O_one))
    #nodepath.set_depth_write(False)

    # attach shaders to node
    attrib = ShaderAttrib.make()
    attrib = attrib.setShader(Shader.load(Shader.SL_GLSL,
                                    vertex="visualiser.vert", 
                                    fragment="visualiser.frag"))
    attrib = attrib.set_shader_input("scene_scale", scale)
    attrib = attrib.set_shader_input("num_points", num_points)
    attrib = attrib.set_shader_input("ssbo", ssbo)
    attrib = attrib.set_flag(ShaderAttrib.F_shader_point_size, True)
    root.set_attrib(attrib)

    # create texture buffer
    filter_mgr = FilterManager(base.win, base.cam)
    #filter_mgr.resizeBuffers()
    #filter_mgr.windowEvent(base.win)
    screen_tex = Texture()
    screen_tex.setMagfilter(SamplerState.FT_nearest)
    screen_tex.setMinfilter(SamplerState.FT_nearest)
    #screen_tex.setMatchFramebufferFormat()
    quad = filter_mgr.renderSceneInto(colortex=screen_tex)
    screen_tex.set_format(Texture.F_srgb_alpha)
    quad.set_shader(Shader.load(Shader.SL_GLSL, vertex="quad.vert", fragment="screen.frag"))
    quad.set_shader_input("screen_scale", base.win.properties.getSize())
    quad.set_shader_input("screen_tex", screen_tex)
    quad.set_attrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add, ColorBlendAttrib.O_one , ColorBlendAttrib.O_one_minus_incoming_alpha ))

    # don't clear the window colour at the start of the frame
    base.win.set_clear_color_active(False)
    for dr in base.win.display_regions:
        dr.set_clear_color_active(False)

    base.accept("v", base.bufferViewer.toggleEnable)

    #filter_mgr.buffers[0].set_clear_color_active(True)

    # set Esc key as quit button
    base.accept("escape", base.userExit)

    # position camera
    base.cam.setPos(0.,-65.,10.)
    base.cam.setHpr(0., 0., 0.)
    enable_camera_controls()

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

    print(f"== Playing file {filename}; {base.audio.shape[0]/base.samplerate}s duration...")
    taskMgr.add(call_play_audio, "play_audio")

    base.run()                                                          # taskMgr takes over from here
