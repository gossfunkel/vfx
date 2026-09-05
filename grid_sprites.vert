#version 430

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
//uniform mat4 p3d_ModelViewProjectionMatrix;

in vec3 p3d_Vertex;

struct Sprite_data {
    vec3 pos;
    float vel;
};

layout (std430, binding = 0) buffer sprite_buff {
    Sprite_data sprites[];
};

out vec2 texcoord;
flat out uint sprite_idx;

void main() {
    sprite_idx = gl_VertexID / 3;
    uint corner_idx = gl_VertexID % 3;

    vec4 pos = p3d_ModelViewMatrix * vec4(sprites[sprite_idx].pos, 1.);
    //float size = sprites[sprite_idx].size * scale;
    if (corner_idx == 0) { // middle bottom
        //pos.y -= 0.15 * size;
        pos.y -= .15;
        texcoord = vec2(.5, -.5);
    } else if (corner_idx == 1) { // top left
        //pos.x -= 0.15 * size;
        pos.x -= .15;
        texcoord = vec2(-.9, 1.);
    } else { // top right
        //pos.x += 0.15 * size;
        pos.x += .15;
        texcoord = vec2(1.9, 1.);
    }

    gl_Position = p3d_ProjectionMatrix * pos;
}