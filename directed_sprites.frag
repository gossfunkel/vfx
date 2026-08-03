#version 430

in vec2 texcoord;
uniform float osg_FrameTime;
uniform sampler2D p3d_Texture0;
uniform uint num_sprites;

struct Sprite_data {
    vec3 pos;           // 32B
    vec3 facing;        // 32B
};

layout (std430, binding = 0) buffer sprite_buff {
    Sprite_data sprites[];
};

out vec4 p3d_FragColor;
in float sprite_idx;

void main() {
    vec4 col_sample = texture(p3d_Texture0, texcoord);
    float sprite_norm = sprite_idx/float(num_sprites);
    col_sample.x *= min(.5,sprite_norm) - max(0.,sprite_norm-.5);
    //col_sample.y *= abs(sin(osg_FrameTime+sprite_idx));
    col_sample.y *= abs(sin(sprite_idx));
    col_sample.z *= 1. - (min(.5,sprite_norm) - max(0.,sprite_norm-.5));
    /*col_sample.x *= sprites[int(sprite_idx)].pos.z;
    col_sample.z *= -sprites[int(sprite_idx)].pos.z; */
    //col_sample.y *= sin(osg_FrameTime*2. + sprite_idx);
    //col_sample.z *= -sin(osg_FrameTime*3. + sprite_idx);
    p3d_FragColor = col_sample;
}
