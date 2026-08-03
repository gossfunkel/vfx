#version 430

in vec2 texcoord;
in vec4 col;
flat in uint quad_id;
uniform float osg_FrameTime;

out vec4 p3d_FragColor;

void main() {
    vec3 col_val = vec3(cos(osg_FrameTime + quad_id*10),
                        sin(osg_FrameTime/3 + quad_id*10),
                        -cos(osg_FrameTime/2 + quad_id*10));
    p3d_FragColor = vec4(col_val, col_val.x+col_val.y+col_val.z);
}
