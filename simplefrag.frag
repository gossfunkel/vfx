#version 450
// test script that changes the colour of the point

// pass value into shader from main code
//uniform vec2 resolution;
//mediump vec2 gl_PointCoord; //fragment position within a point (point rasterization only) 

//uniform sampler2D p3d_Texture0;

// input 
in vec2 texcoord;
//in vec3 col;
in vec4 col;

// out to screen
out vec4 p3d_FragColor;

void main() {
	// fade out colour from centre
	// uv = (2. * resolution.x)/2. + resolution.y or something idk
	float uvDist = pow(sqrt(abs((.5-texcoord.x)*(.5-texcoord.x)) + abs((.5-texcoord.y)*(.5-texcoord.y))),1.);
	//vec2 uv = vec2((texcoord.x+.5)*(texcoord.x+.5)*(texcoord.x+.5)*(texcoord.x+.5),(texcoord.y+.5)*(texcoord.y+.5)*(texcoord.y+.5)*(texcoord.y+.5));
	//p3d_FragColor = vec4(col.x - uvDist, col.y - uvDist, col.z - uvDist,(col.x + col.y + col.z)/3. - uvDist);

	// todo: normalise colour values so that FF0000 and FFFF00 are the same size
	p3d_FragColor = vec4(col.x, 
						 col.y, 
						 col.z,
						 //1.);
						 //col.w - uvDist);
						 (col.x + col.y + col.z)/3. - uvDist);
	
	//p3d_FragColor = vec4(1.,1.,1.,1.);
}
