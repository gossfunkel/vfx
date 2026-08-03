#version 430

const float TAU = 6.2831853;

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec3 p3d_Vertex;
in vec4 p3d_Color;

//uniform uint num_verts;
uniform float osg_FrameTime;

layout (std430, binding = 0) buffer vert_buff {
    vec3 pos[];
};

out vec4 col;

void main() {
    uint sprite_idx = gl_VertexID;

   /*  vec4 posn = p3d_ModelViewMatrix * vec4((.5 + sin(TAU * float(sprite_idx)/float(num_sprites) + osg_FrameTime)*.5)*pos[sprite_idx].x,
                                           pos[sprite_idx].y,
                                           (.5 + cos(TAU * float(sprite_idx)/float(num_sprites) + osg_FrameTime)*.5)*pos[sprite_idx].z, 
                                           1.); */
    vec4 posn = vec4(pos[sprite_idx].xyz, 1.);
    posn.y = mod(posn.y + osg_FrameTime, 255.);
    if (sprite_idx >= 256) {
        posn.x *= .5 + sin(TAU*pos[sprite_idx].y/255. + osg_FrameTime/2. + TAU*.5)*.5;
        posn.z *= .5 + cos(TAU*pos[sprite_idx].y/255. + osg_FrameTime/2. + TAU*.5)*.5;
    } else {
        posn.x *= .5 + sin(TAU*pos[sprite_idx].y/255. + osg_FrameTime/2.)*.5;
        posn.z *= .5 + cos(TAU*pos[sprite_idx].y/255. + osg_FrameTime/2.)*.5;
    }

    col = p3d_Color * vec4(posn.y/255.,1.-posn.y/127.5,1.-posn.y/255.,1.);

    gl_Position = p3d_ModelViewProjectionMatrix * posn;
}
