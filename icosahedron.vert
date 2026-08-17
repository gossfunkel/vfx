#version 430

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float osg_FrameTime;

in vec3 p3d_Vertex;
in vec4 p3d_Color;
out vec4 vertex_col;
uniform uint num_verts;

layout (std430, binding = 0) buffer vert_buff {
    vec3 pos[];
};

void main() {
    vertex_col = p3d_Color;

    gl_Position = p3d_ModelViewProjectionMatrix * vec4(pos[gl_VertexID], 1.);
}