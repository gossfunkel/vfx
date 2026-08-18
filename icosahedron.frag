#version 430

//uniform uint num_verts;
in vec4 vertex_col;

layout (std430, binding = 0) buffer vert_buff {
    vec3 pos[];
};

flat in uint vtx_id;
out vec4 p3d_FragColor;

void main() {
    //float abs_dist = (abs(gl_FragCoord.x - pos[vtx_id].x) + 
    //                 abs(gl_FragCoord.y - pos[vtx_id].y) + 
    //                 abs(gl_FragCoord.z - pos[vtx_id].z))*.0005;
    vec3 dist = abs(gl_FragCoord.xyz - pos[vtx_id])*.01;
    //p3d_FragColor = vec4(abs_dist,abs_dist*abs_dist,abs_dist,1.);
    p3d_FragColor = vec4(dist,1.);
}