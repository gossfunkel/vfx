#version 430

const float TAU = 6.2831853;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float osg_FrameTime;

in vec3 p3d_Vertex;
in vec4 p3d_Color;
//uniform uint num_verts;
//in vec2 p3d_MultiTexCoord0;
out vec4 vertex_col;

layout (std430, binding = 0) buffer vert_buff {
    vec3 pos[];
};

void main() {
    float offset = 0.;
    //texcoord = vec2(p3d_Vertex.x,p3d_MultiTexCoord0.y);
    /*
    if (gl_VertexID%4 == 0) {
        offset = TAU/4.;
    } else if (gl_VertexID%4 == 1) {
        offset = TAU/2.;
    } else if (gl_VertexID%4 == 2) {
        offset = 3.*TAU/4.;
    }*/

    offset = TAU * (pos[gl_VertexID].x / 64.) + pos[gl_VertexID].y;

    vertex_col = vec4(abs(sin(osg_FrameTime + offset)/3.),
                      abs(sin(osg_FrameTime + offset + TAU/3.)/3.),
                      abs(sin(osg_FrameTime + offset + 2.*TAU/3.)/3.),1.);

    gl_Position = p3d_ModelViewProjectionMatrix * vec4(pos[gl_VertexID], 1.);
}