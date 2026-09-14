#version 430

const float TAU = 6.28318531;

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
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

vec4 generate_tube (vec4 world_pos, float time, uint point_ID) {
    return vec4(mod(world_pos.x + time + point_ID, scene_scale.x), 
                    world_pos.y + cos(time + point_ID), 
                    world_pos.z + sin(time + point_ID), 1);
}

vec4 generate_hoop (vec4 world_pos, float time, uint point_ID) {
    time *= .01;
    return vec4(cos(sin(time)*3*time + point_ID)*scene_scale.x,
                sin(sin(time)*3*time + point_ID)*scene_scale.y,
                -cos(time + point_ID)*scene_scale.z, 1.);
}

vec4 generate_spiral (vec4 world_pos, float time, uint point_ID) {
    time *= .002;
    return vec4(cos(TAU + time + point_ID)*scene_scale.x,
                sin(TAU + time + point_ID)*scene_scale.y,
                -cos(TAU + time + point_ID * .1)*scene_scale.z, 1.);
}

vec4 generate_spiral2 (vec4 pos, float time, uint point_ID) {
    time *= .02;
    return vec4(cos(4. * TAU * pos.x + time)*scene_scale.x,
                sin(4. * TAU * pos.x + time)*scene_scale.y,
                -cos(TAU * pos.x + time * .25)*scene_scale.z, 1.);
}

void generate_torus (float time, uint point_ID) {
    time *= .002;
    float theta = TAU * time;
    positions[point_ID] += vec4(((cos(theta)*scene_scale.x) + cos(theta) * cos(92.*theta)*2.),
                ((sin(theta)*scene_scale.y + sin(theta) * cos(92.*theta)*2.)),
                (sin(92.* theta)*2. + scene_scale.z/2.), 1.);
    //return positions[point_ID];
}

void spin(float time, float dt, uint point_ID) {
    vec4 prevPos = positions[point_ID];
    // test by spinning in circles
    positions[point_ID] += vec4(cos(time)*point_ID * dt,sin(time)*point_ID * dt, 0., 1.);
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

    if (state > 0) generate_torus(osg_FrameTime, point_ID);
    else spin(osg_FrameTime, osg_DeltaFrameTime, point_ID);

    // 1) world space
    vec4 world_pos = p3d_ModelMatrix * vec4(positions[point_ID].xyz,1.);
    //world_pos = generate_spiral2(world_pos, time, point_ID);

    // 2) View Space

    vec4 view_pos = p3d_ViewMatrix * world_pos;

    // rotate to antialias by aligning vert with the direction of travel? 
    //  would require next pos or more dynamics

    gl_PointSize = 20. / length(view_pos.xyz);

    // 3) Screen Space

    gl_Position = p3d_ProjectionMatrix * view_pos;

    // gl_PointSize = 20. / gl_Position.w;
}
