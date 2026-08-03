#version 430

const float TAU = 6.28318531;

in vec2 texcoord;
in vec4 col;
flat in uint point_ID;
uniform int num_points;
uniform float osg_FrameTime;

out vec4 p3d_FragColor;

void main() {
    float time = osg_FrameTime/6.;
    //vec3 col_val = vec3(1.,1.,1.);
    float theta = TAU * texcoord.x;
    vec3 col_val = vec3(abs(sin(theta + time)),
                        abs(sin(theta + TAU/3. + time)),
                        abs(sin(theta + 2.*TAU/3. + time)));
    p3d_FragColor = vec4(col_val, col_val.x+col_val.y+col_val.z);
}
