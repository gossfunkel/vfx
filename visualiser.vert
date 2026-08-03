#version 430

// constants
const float TAU = 6.28318531;

// panda3d builtin shader inputs
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform float osg_FrameTime;

// custom shader inputs
in vec3 p3d_Vertex;
in vec4 p3d_Color;
uniform vec3 scene_scale;
uniform int num_points;

// SSBO containing audio data
layout (std430, binding = 0) buffer ssbo { 
    float samples[];
};

out vec2 texcoord;
out vec4 col;
flat out uint point_ID;

vec4 generate_torus_waveform (vec4 pos, float time, uint point_ID) {
    int audIdx = int(point_ID+num_points*int(time+pos.x))%samples.length();
    float audio_sample = log(abs(samples[audIdx]));
    // pos.x is a range from 0-1 (like numpy.linspace)
    float theta = TAU * pos.x; // theta is the angle around the centrepoint where we find the vertex
    return vec4((cos(theta)*scene_scale.x) + cos(theta) * (cos(92.*theta + time)+audio_sample),
                sin(theta)*scene_scale.y + sin(theta) * (cos(92.*theta + time)+audio_sample),
                sin(92.* theta + time)+audio_sample + scene_scale.z/2., 1.);
}

vec4 generate_circle_waveform (vec4 pos, float time, uint point_ID) {
    int audIdx = int(point_ID+num_points*int(time+pos.x))%samples.length();
    float audio_sample = log(samples[audIdx])*2.;
    float theta = TAU * (pos.x + time); 
    return vec4((cos(theta)*scene_scale.x),
                sin(theta)*scene_scale.y,
                scene_scale.z/2. + audio_sample, 1.);
}

vec4 generate_linear_waveform (vec4 pos, float time, uint point_ID) {
    int intime = int(2*time+pos.x);
    // for some damn reason I can't seem to amend this next line at all without breaking it with no error
    int audIdx = int(point_ID+num_points*intime)%samples.length();
    float audio_sample = log(samples[audIdx]*2.)*10;
    // a line from scene_scale.x/2,y=0,z=amplitude -> scene_scale.x/2,y=scene_scale.y, z=amplitude
    //   mapped to            audio_sample         ->      log(samples[0])*2 (should be 0)
    return vec4((.5-pos.x)*2.*scene_scale.x,
                0.,
                audio_sample, 1.);
}

vec4 lerp_point_to (vec4 pos, vec4 dest, float time, float arrival_time) {
    float dt_remaining = arrival_time - time;
    vec4 distance_remaining = dest - pos;
    vec4 speed = distance_remaining / dt_remaining; // v = s/t
    return pos + speed; // velocity is the change in position for a timestep
}

void main() {
    // set up integer and normalised float coords for the vertices
    point_ID = gl_VertexID;
    texcoord = vec2(p3d_Vertex.x, gl_VertexID);
    // pass that and the colour to the fragment shader
    col = p3d_Color;

    // 1) world space
    vec4 world_pos = p3d_ModelMatrix * vec4(p3d_Vertex,1.);

    world_pos = generate_linear_waveform(world_pos, osg_FrameTime, point_ID);

    // 2) View Space

    vec4 view_pos = p3d_ViewMatrix * world_pos;

    gl_PointSize = 20. / length(view_pos.xyz);

    // 3) Screen Space

    gl_Position = p3d_ProjectionMatrix * view_pos;
}
