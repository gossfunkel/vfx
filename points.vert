#version 430

const float TAU = 6.28318531;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
//uniform int osg_FrameNumber;
uniform float osg_FrameTime;
uniform float osg_DeltaFrameTime;

in vec3 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;
in vec3 scene_scale;
in int num_points;
uniform int state;

// SSBO containing audio data
layout (std430, binding = 0) buffer ssbo { 
    vec4 positions[];
};

out vec2 texcoord;
out vec4 col;
flat out uint point_ID;

void generate_tube (float time, uint point_ID) {
    positions[point_ID] = vec4(mod(positions[point_ID].x + time + point_ID, scene_scale.x), 
                    positions[point_ID].y + cos(time + point_ID), 
                    positions[point_ID].z + sin(time + point_ID), 1);
}

void generate_hoop (float time, uint point_ID) {
    time *= .01;
    positions[point_ID] = vec4(cos(sin(time)*3*time + point_ID)*scene_scale.x,
                sin(sin(time)*3*time + point_ID)*scene_scale.y,
                -cos(time + point_ID)*scene_scale.z, 1.);
}

void generate_spiral (float time, uint point_ID) {
    time *= .002;
    positions[point_ID] = vec4(cos(TAU + time + point_ID)*scene_scale.x,
                sin(TAU + time + point_ID)*scene_scale.y,
                -cos(TAU + time + point_ID * .1)*scene_scale.z, 1.);
}

void generate_spiral2 (float time, uint point_ID) {
    time *= .02;
    positions[point_ID] = vec4(cos(4. * TAU * positions[point_ID].x + time)*scene_scale.x,
                sin(4. * TAU * positions[point_ID].x + time)*scene_scale.y,
                -cos(TAU * positions[point_ID].x + time * .25)*scene_scale.z, 1.);
}

void spin_torus (float time, uint point_ID) {
    float theta = TAU * time * .2;
    positions[point_ID] += vec4(cos(theta),
                sin(theta),
                sin(8.* theta), 1.);
    //return positions[point_ID];
}

void spin_flower (float time, float dt, uint point_ID) {
    vec4 prevPos = positions[point_ID];
    // test by spinning in circles
    positions[point_ID] += vec4(cos(point_ID  + time)*10. * dt,
                                sin(point_ID  + time)*10. * dt, 
                                -sin(point_ID + time)*10. * dt, 1.);
    //return positions[point_ID];
}

vec4 lerp_point_to (vec4 dest, float start_time, float time, float arrival_time, float dt, uint point_ID) {
    float dt_remaining = arrival_time - time;
    vec4 distance_remaining = dest - positions[point_ID];
    positions[point_ID] += distance_remaining / dt_remaining; // v = s/t
    return positions[point_ID]; // velocity is the change in position for a timestep
}

void main() {
    texcoord = vec2(p3d_Vertex.x, p3d_MultiTexCoord0.y);
    col = p3d_Color;
    point_ID = gl_VertexID;

    if (state == 1) spin_torus(osg_FrameTime, point_ID);
    else if (state == 2) spin_flower(osg_FrameTime, osg_DeltaFrameTime, point_ID);

    vec4 wv_pos = p3d_ModelViewMatrix * vec4(positions[point_ID].xyz,1.);

    // rotate to antialias by aligning vert with the direction of travel? 
    //  would require next pos or more dynamics

    gl_PointSize = 20. / length(wv_pos.xyz);

    gl_Position = p3d_ProjectionMatrix * wv_pos;
}
