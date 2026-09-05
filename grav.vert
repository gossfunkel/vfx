#version 430

#include "simple_particle.glsl"

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;

in vec3 p3d_Vertex;
in vec4 p3d_Color;

//uniform uint num_verts;
uniform float osg_FrameTime;

out vec2 texcoord;
out vec4 col;

void main() {
    uint sprite_idx = gl_VertexID / 3;
    uint corner_idx = gl_VertexID % 3;

    vec4 posn = vec4(p[sprite_idx].pos, 1.);
    col = vec4(255., p[sprite_idx].mass*200., p[sprite_idx].mass*255., 255.);

    if (corner_idx == 0) {          // middle bottom
        posn.y -= .25 * p[sprite_idx].size;
        texcoord = vec2(.5, -.5);
    } else if (corner_idx == 1) {   // top left
        posn.x -= .5;
        posn.y += .25 * p[sprite_idx].size ;
        texcoord = vec2(-.9, 1.);
    } else {                        // top right
        posn.x += .5;
        posn.y += .25 * p[sprite_idx].size;
        texcoord = vec2(1.9, 1.);
    }

    gl_Position = p3d_ProjectionMatrix * posn;
}
