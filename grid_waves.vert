#version 430

// constants
const float TAU = 6.28318531;

// panda3d builtin shader inputs
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform float osg_DeltaFrameTime;

// custom shader inputs
in vec3 p3d_Vertex;
in vec4 p3d_Color;
uniform vec3 scene_scale;
uniform int NUM_PTS;

// SSBO containing velocity data
layout (std430, binding = 0) buffer ssbo {
    float y_pos[];
    float vels[];
};

out vec2 texcoord;
out vec4 col;
flat out uint point_ID;

// returns new velocity
float s_h_ode(float pos, float vel, float dt) {
    return vel - pos * dt;
}

// makes four guesses at new velocity
float rk4(float pos, float vel, float dt) {
    float v_1 = s_h_ode(pos, dt,    vel);
    float v_2 = s_h_ode(pos, dt*.5, v_1);
    float v_3 = s_h_ode(pos, dt*.5, v_2);
    float v_4 = s_h_ode(pos, dt,    v_3);
    return (vel + 2. * v_2 + 2. * v_3 + v_4) / 6.;
}

float s_h_osc (float ypos, float dt, uint point_ID) {
    //vels[point_ID] = rk4(pos.y, vels[point_ID], dt);
    //dt *= 0.001;
    //vel = rk4(ypos, vel, dt);
    //vels[point_ID] = s_h_ode(ypos, vels[point_ID], dt);
    //vels[point_ID] -= ypos * dt;
    //vels[point_ID] = 0;

    //ypos += sqrt(vel*vel + dt*dt);
    ypos += vels[point_ID];
    return ypos;
}

void main() {
    // set up integer and normalised float vertex coords for the frag shader
    texcoord = vec2(p3d_Vertex.x, gl_VertexID);

    // calculate position update in model space
    y_pos[gl_VertexID] = s_h_osc(y_pos[gl_VertexID], osg_DeltaFrameTime, gl_VertexID);
    // 1) world space
    vec4 world_pos = p3d_ModelMatrix * vec4(p3d_Vertex.x, y_pos[gl_VertexID], p3d_Vertex.z, 1.);
    col = vec4(y_pos[gl_VertexID], .5 + .5 * abs(vels[gl_VertexID]), -y_pos[gl_VertexID], 1.);

    // 2) View Space

    vec4 view_pos = p3d_ViewMatrix * world_pos;

    gl_PointSize = 40. / length(view_pos.xyz);

    // 3) Screen Space

    gl_Position = p3d_ProjectionMatrix * view_pos;
}
