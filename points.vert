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

struct point {
    vec4 pos;
    vec4 vel;
};

// SSBO containing audio data
layout (std430, binding = 0) buffer ssbo { 
    point points[];
};

out vec2 texcoord;
out vec4 col;
flat out uint point_ID;

void generate_tube (float time, uint point_ID) {
    points[point_ID].pos = vec4(mod(points[point_ID].pos.x + time + point_ID, scene_scale.x), 
                    points[point_ID].pos.y + cos(time + point_ID), 
                    points[point_ID].pos.z + sin(time + point_ID), 1);
}

void generate_hoop (float time, uint point_ID) {
    time *= .01;
    points[point_ID].pos = vec4(cos(sin(time)*3*time + point_ID)*scene_scale.x,
                sin(sin(time)*3*time + point_ID)*scene_scale.y,
                -cos(time + point_ID)*scene_scale.z, 1.);
}

void generate_spiral (float time, uint point_ID) {
    time *= .002;
    points[point_ID].pos = vec4(cos(TAU + time + point_ID)*scene_scale.x,
                sin(TAU + time + point_ID)*scene_scale.y,
                -cos(TAU + time + point_ID * .1)*scene_scale.z, 1.);
}

void generate_spiral2 (float time, uint point_ID) {
    time *= .02;
    points[point_ID].pos = vec4(cos(4. * TAU * points[point_ID].pos.x + time)*scene_scale.x,
                sin(4. * TAU * points[point_ID].pos.x + time)*scene_scale.y,
                -cos(TAU * points[point_ID].pos.x + time * .25)*scene_scale.z, 1.);
}

void spin_torus (float time, float dt, uint point_ID) {
    float theta = TAU * time * .2;
    points[point_ID].vel = vec4(cos(theta)*dt,
                sin(theta)*dt,
                sin(.2 * theta)*dt, 1.);
}

void spin_flower (float time, float dt, uint point_ID) {
    //vec3 prevPos = points[point_ID].pos.xyz;
    // test by spinning in circles
    points[point_ID].vel = vec4(cos(point_ID  + time)*10. * dt,
                                sin(point_ID  + time)*10. * dt, 
                                -sin(point_ID + time)*10. * dt, 1.);
    //return positions[point_ID];
}

void seek_origin (float dt, uint point_ID) {
    points[point_ID].vel = -points[point_ID].pos * dt;
}

vec4 lerp_point_to (vec4 dest, float start_time, float time, float arrival_time, float dt, uint point_ID) {
    float dt_remaining = arrival_time - time;
    vec4 distance_remaining = dest - points[point_ID].pos;
    points[point_ID].pos += distance_remaining / dt_remaining; // v = s/t
    return points[point_ID].pos; // velocity is the change in position for a timestep
}

void main() {
    texcoord = vec2(p3d_Vertex.x, p3d_MultiTexCoord0.y);
    col = p3d_Color;
    point_ID = gl_VertexID;

    if (state == 1) spin_torus(osg_FrameTime, osg_DeltaFrameTime, point_ID);
    else if (state == 2) spin_flower(osg_FrameTime, osg_DeltaFrameTime, point_ID);
    else if (state == 3) seek_origin(osg_DeltaFrameTime, point_ID);
    else points[point_ID].vel = vec4(0.);

    points[point_ID].pos += points[point_ID].vel * osg_DeltaFrameTime;

    vec4 wv_pos = p3d_ModelViewMatrix * vec4(points[point_ID].pos.xyz,1.);

    // rotate to antialias by aligning vert with the direction of travel? 
    //  would require next pos or more dynamics

    gl_PointSize = 20. / length(wv_pos.xyz);

    gl_Position = p3d_ProjectionMatrix * wv_pos;
}
