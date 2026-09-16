#version 430

//const float TAU = 6.28318531;

in vec4 col;
//uniform int num_points;
//uniform float osg_FrameTime;

out vec4 p3d_FragColor;

void main() {
    //float time = osg_FrameTime/6.;
    //vec3 col_val = vec3(1.,1.,1.);
    //float theta = TAU * texcoord.x;
    p3d_FragColor = col;
}
