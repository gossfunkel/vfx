#version 430

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform float osg_FrameTime;

in vec3 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

out vec2 texcoord;
out vec4 col;
out uint quad_id;

void main() {
    // note - we want to retain the relationship between the vertices to avoid breaking the quads
    texcoord = p3d_MultiTexCoord0;
    quad_id = uint(gl_VertexID/4);
    uint vtx_pos = uint(gl_VertexID%4);
    col = p3d_Color;

    // 1) world space
    vec4 world_pos = p3d_ModelMatrix * vec4(quad_pos,1.);

    world_pos = vec4(mod(world_pos.x + osg_FrameTime + quad_id, 25), // FIXME actually pass in width
                         world_pos.y + cos(osg_FrameTime + quad_id), 
                         world_pos.z + sin(osg_FrameTime + quad_id), 1);

    // 2) View Space

    //vec4 view_pos = vec4(world_pos.x/world_pos.y, 0., world_pos.z/world_pos.y, 1.);

    vec4 view_pos = p3d_ViewMatrix * world_pos;
    /*
    if (vtx_pos == 0) { // top left 
        view_pos.x -= 0.04;
        view_pos.y += -0.04;
    } else if (vtx_pos == 1) { // bottom left 
        view_pos.x -= 0.04;
        view_pos.y -= -0.04;
    } else if (vtx_pos == 1) { // top right 
        view_pos.x += 0.04;
        view_pos.y += -0.04;
    } else { // bottom right 
        view_pos.x += 0.04;
        view_pos.y -= -0.04;
    }
    */
    // 3) Screen Space

    gl_Position = p3d_ProjectionMatrix * view_pos;
}
