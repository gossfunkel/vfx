#version 430

in vec2 texcoord;
uniform float osg_FrameTime;
uniform sampler2D p3d_Texture0;

struct Sprite_data {
    vec3 pos;
    float vel;
};

layout (std430, binding = 0) buffer sprite_buff {
    Sprite_data sprites[];
};

out vec4 p3d_FragColor;
flat in uint sprite_idx;

void main() {
    vec4 col_sample = texture(p3d_Texture0, texcoord);
    col_sample.x *= sprites[sprite_idx].pos.z;
    col_sample.y *= sprites[sprite_idx].vel;
    col_sample.z *= -sprites[sprite_idx].pos.z;
    //col_sample.y *= sin(osg_FrameTime*2. + sprite_idx);
    //col_sample.z *= -sin(osg_FrameTime*3. + sprite_idx);
    p3d_FragColor = col_sample;
}