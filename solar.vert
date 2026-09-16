#version 430

const float TAU = 6.28318531;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform float osg_FrameTime;
uniform float osg_DeltaFrameTime;

in vec3 p3d_Vertex;
in vec4 p3d_Color;
in int num_pts;

struct point {
    vec4 pos;
    vec3 vel;
};

// SSBO containing audio data
layout (std430, binding = 0) buffer pt_buff { 
    point points[];
};

out vec4 col;

void main() {
    col = p3d_Color;

    points[gl_VertexID].pos += vec4(points[gl_VertexID].vel * osg_DeltaFrameTime, 1.);

    vec4 wv_pos = p3d_ModelViewMatrix * vec4(points[gl_VertexID].pos.xyz,1.);

    // rotate to antialias by aligning vert with the direction of travel? 
    //  would require next pos or more dynamics

    gl_PointSize = 10. / length(wv_pos.xyz);

    gl_Position = p3d_ProjectionMatrix * wv_pos;
}
