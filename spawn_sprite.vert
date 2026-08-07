#version 430

const float TAU = 6.2831853;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;

in vec3 p3d_Vertex;
in vec4 p3d_Color;
in uint num_sprites;

//uniform uint num_verts;
uniform float osg_FrameTime;

layout (std430, binding = 0) readonly buffer vert_buff {
    vec3 pos[];
};

out vec2 texcoord;
out vec4 col;

void main() {
    uint sprite_idx = gl_VertexID / 3;
    uint corner_idx = gl_VertexID % 3;

   /*  vec4 posn = p3d_ModelViewMatrix * vec4((.5 + sin(TAU * float(sprite_idx)/float(num_sprites) + osg_FrameTime)*.5)*pos[sprite_idx].x,
                                           pos[sprite_idx].y,
                                           (.5 + cos(TAU * float(sprite_idx)/float(num_sprites) + osg_FrameTime)*.5)*pos[sprite_idx].z, 
                                           1.); */
    vec4 posn = vec4(pos[sprite_idx].xyz, 1.);

    col = p3d_Color * vec4(posn.y/255.,1.-posn.y/127.5,1.-posn.y/255.,1.);
    posn = p3d_ModelViewMatrix * posn;
    if (corner_idx == 0) {          // middle bottom
        posn.y -= .25 ;
        texcoord = vec2(.5, -.5);
    } else if (corner_idx == 1) {   // top left
        posn.x -= .5;
        posn.y += .25 ;
        texcoord = vec2(-.9, 1.);
    } else {                        // top right
        posn.x += .5;
        posn.y += .25 ;
        texcoord = vec2(1.9, 1.);
    }

    gl_Position = p3d_ProjectionMatrix * posn;
}
