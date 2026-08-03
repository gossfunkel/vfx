#version 430

// constants
//const float TAU = 6.28318531;

// panda3d builtin shader inputs
//uniform float osg_FrameTime;

// custom shader inputs
in vec2 texcoord;
in vec4 col;
flat in uint point_ID;
uniform int num_points;

// fragment colour for render
out vec4 p3d_FragColor;

void main() {
    // slow down time to make the colours move nicely
    //float time = osg_FrameTime/6.;
    // calculate fragment (point) colour
    //vec3 col_val = vec3(texcoord.y, 0., 1. - texcoord.y);
    // alpha doesn't matter, it's going on the screen buffer
    p3d_FragColor = col;
}
