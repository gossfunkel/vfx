#pragma once

uniform uint num_sprites;

struct Sprite_data {
    vec3 neighbour;       // 16B
    vec3 pos_0;           // 16B
    vec3 pos_1;           // 16B
    vec3 vel;             // 16B
    vec3 force;           // 16B
};

layout (std430, binding = 0) buffer sprite_buff {
    Sprite_data sprites[];
};
