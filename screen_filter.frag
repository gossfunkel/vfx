#version 430

layout(binding=0) uniform sampler2D screen_tex;
uniform ivec2 screen_scale;

in vec2 texcoord;

out vec4 p3d_FragColor;

void main() {
    ivec2 img_size = textureSize(screen_tex, 0);
    ivec2 itexcoord = ivec2(int(texcoord.x * screen_scale.x),
                            int(texcoord.y * screen_scale.y));//+(img_size.y - screen_scale.y));
    
    /*
    vec3 conv_pix = vec3(1.);
    for (int x_offset = -2; x_offset < 3; x_offset++) {
        for (int y_offset = -2; y_offset < 3; y_offset++) {
            conv_pix *= texelFetch(screen_tex, itexcoord + ivec2(x_offset, y_offset), 0).xyz / 25.;
        }
    }
    p3d_FragColor = vec4(conv_pix, 1.);
    */
     
    vec4 pix_sample = texelFetch(screen_tex, itexcoord, 0);
    vec4 up_sample = texelFetch(screen_tex, itexcoord + ivec2(0, -1), 0);
    vec4 dn_sample = texelFetch(screen_tex, itexcoord + ivec2(0, 1), 0);
    vec4 lf_sample = texelFetch(screen_tex, itexcoord + ivec2(-1, 0), 0);
    vec4 rg_sample = texelFetch(screen_tex, itexcoord + ivec2(1, 0), 0);
    vec4 tl_sample = texelFetch(screen_tex, itexcoord + ivec2(-1, -1), 0);
    vec4 bl_sample = texelFetch(screen_tex, itexcoord + ivec2(-1, 1), 0);
    vec4 br_sample = texelFetch(screen_tex, itexcoord + ivec2(1, 1), 0);
    vec4 tr_sample = texelFetch(screen_tex, itexcoord + ivec2(1, -1), 0);

    // average colour values
    p3d_FragColor.x = (pix_sample.x + up_sample.x + dn_sample.x + lf_sample.x + rg_sample.x
                                   + tl_sample.x + tr_sample.x + bl_sample.x + br_sample.x) / 9.;
    p3d_FragColor.y = (pix_sample.y + up_sample.y + dn_sample.y + lf_sample.y + rg_sample.y
                                   + tl_sample.y + tr_sample.y + bl_sample.x + br_sample.y) / 9.;
    p3d_FragColor.z = (pix_sample.z + up_sample.z + dn_sample.z + lf_sample.z + rg_sample.z
                                   + tl_sample.z + tr_sample.z + bl_sample.x + br_sample.z) / 9.;
    p3d_FragColor.w = 1.;
    

}