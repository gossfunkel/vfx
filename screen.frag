#version 430

// uniform shader inputs
//layout(rgba8) uniform readonly image2D screen_tex;
layout(binding=0) uniform sampler2D screen_tex;
uniform ivec2 screen_scale;

// ins from vertex shader
in vec2 texcoord;

// fragment colour for render
out vec4 p3d_FragColor;

void main() {
    ivec2 img_size = textureSize(screen_tex, 0);
    ivec2 itexcoord = ivec2(int(texcoord.x * screen_scale.x),
                            int(texcoord.y * screen_scale.y));//+(img_size.y - screen_scale.y));

    // get the fresh data from the screen buffer and pack it with the damping factor for the previous data
    p3d_FragColor = vec4(texelFetch(screen_tex, itexcoord, 0).xyz, .4);
}