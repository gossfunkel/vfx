#pragma once

struct Sprite {
    vec3 pos;
    vec3 vel;
};

// quadkey is index
struct Cell {
    vec3 pos;
    uint num_sprites;
    uint sprites[num_sprites];
}

const float TAU = 6.2831853;
const uint num_cells = ((2**10)*3);
