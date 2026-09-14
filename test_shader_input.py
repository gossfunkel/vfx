from direct.showbase.ShowBase import ShowBase
from panda3d.core import Shader, CardMaker, NodePath, load_prc_file_data

vtx = """
#version 430

/*
layout(std430, binding = 0)
struct data {
	int option;
} data;
*/

in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform int option;
out vec4 col;

void main() {
	switch (option) {
		case 0:
			col = vec4(1.,0.,0.,1.); break;
		case 1:
			col = vec4(0.,1.,0.,1.); break;
		case 2:
			col = vec4(0.,0.,1.,1.); break;
		default:
			col = vec4(1.,1.,1.,1.);
	};
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
"""[1:]

frag = """
#version 430

in vec4 col;
out vec4 p3d_FragColor;
        
void main() {
	p3d_FragColor = col;
}
"""

CONFIG = """
win-size 1200 800
gl-version 4 3
"""
load_prc_file_data('', CONFIG)

if __name__ == "__main__":
	ShowBase()
	base.set_background_color(0.,0.,0.,1.)

	cm = CardMaker("screencard")
	#cm.clearColor()
	#cm.setHasUvs(1)
	cm.setFrameFullscreenQuad()
	#cm.setUvRange(0,1)

	screencard_np = NodePath(cm.generate())
	screencard_np.setShader(Shader.make(Shader.SL_GLSL, vertex=vtx, fragment=frag))
	screencard_np.setShaderInput("option", 0)

	#screencard_np.setPos(0,0,0)
	#screencard_np.setHpr(0,180,0)

	screencard_np.reparentTo(base.render2d)

	def turnBlue():
		print("Instructing shader to turn screen blue...")
		screencard_np.setShaderInput("option", 1)

	def turnGreen():
		print("Instructing shader to turn screen green...")
		screencard_np.setShaderInput("option", 2)

	base.accept("g-up", turnGreen)
	base.accept("b-up", turnBlue)

	base.accept("escape", base.userExit)

	base.run()