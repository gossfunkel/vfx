#version 430

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float osg_FrameTime;

in vec3 p3d_Vertex;
in vec4 p3d_Color;
out vec4 vertex_col;
flat out uint vtx_id;
uniform uint num_verts;

layout (std430, binding = 0) buffer vert_buff {
    vec3 pos[];
};

void main() {
    vtx_id = gl_VertexID;
    float val = sin(float(vtx_id) + osg_FrameTime);
    vertex_col = vec4(val,-val,float(vtx_id)/12.,1.);

    gl_Position = p3d_ModelViewProjectionMatrix * vec4(pos[vtx_id], 1.);
}