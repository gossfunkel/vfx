#version 430

uniform sampler2D p3d_Texture0;
in vec2 texcoord;
in vec4 col;

out vec4 p3d_FragColor;

void main(){
    vec4 col_sample = texture(p3d_Texture0, texcoord);
    col_sample *= col;
    p3d_FragColor = col_sample;
}