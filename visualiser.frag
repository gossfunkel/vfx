#version 430

// constants
const float TAU = 6.28318531;

// panda3d builtin shader inputs
uniform float osg_FrameTime;

// custom shader inputs
in vec2 texcoord;
in vec4 col;
flat in uint point_ID;
uniform int num_points;

// fragment colour for render
out vec4 p3d_FragColor;

void main() {
    // slow down time to make the colours move nicely
    float time = osg_FrameTime/6.;
    // angle around circle
    float theta = TAU * (texcoord.x + time);
    // calculate fragment (point) colour
    vec3 col_val = vec3(abs(sin(theta)), abs(sin(theta + TAU/3.)), abs(sin(theta + 2.*TAU/3.)));
    // alpha doesn't matter, it's going on the screen buffer
    p3d_FragColor = vec4(col_val, 1.);
}
