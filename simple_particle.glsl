#pragma once

const float TAU = 6.2831853;
const float G = 6.67430 * pow(10,-11);

struct Particle {
    vec3 pos;
    float mass;
    vec3 vel;
    float size;
};

uniform uint num_sprites;
uint half_pairs = num_sprites/2 - 1;

layout (std430, binding = 0) buffer sprite_buff {
    Particle p[];
};

layout (std430, binding = 1) buffer force_buff {
    vec3 f[];
};

float dist_sq(vec3 vect_a_to_b) {
    return vect_a_to_b.x * vect_a_to_b.x + 
           vect_a_to_b.y * vect_a_to_b.y +
           vect_a_to_b.z * vect_a_to_b.z;
}
