#version 430

//uniform uint num_verts;
in vec4 vertex_col;

layout (std430, binding = 0) buffer vert_buff {
    vec3 pos[];
};

out vec4 p3d_FragColor;

void main() {
    p3d_FragColor = vec4(1.);
}