#pragma once

const float TAU = 6.2831853;
const float G = 6.67430 * 10**(-11);

struct Particle {
    vec3 pos;
    float mass;
    vec3 vel;
    float size;
};

struct Cell {
    vec3 pos; // centre of mass
    float mass; // total mass
    vec3 force; // total (external) force on particles
    uint first; // id of first member particle in array
    uint members; // total number of particles in cell
}

layout (std430, binding = 0) buffer sprite_buff {
    Particle p[];
};

layout (std430, binding = 1) buffer cell_buff {
    Cell c[];
};

uint find_cell_idx(uint p_id) {
    // find particle's cell position by rounding
    uint cell_x = uint(p[p_id].pos.x);
    uint cell_y = uint(p[p_id].pos.y);
    uint cell_z = uint(p[p_id].pos.z);
    return 25 * cell_x + 5 * cell_y + cell_z;
}

float dist_sq(vec3 vect_a_to_b) {
    return vect_a_to_b.x * vect_a_to_b.x + 
           vect_a_to_b.y * vect_a_to_b.y +
           vect_a_to_b.z * vect_a_to_b.z;
}
