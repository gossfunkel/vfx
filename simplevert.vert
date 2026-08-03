#version 450

#pragma include "common.glsl"

// variable vertex shader inputs (unique per vertex)
//uniform mat4 p3d_ModelViewProjectionMatrix;
//uniform mat4 p3d_ViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

//in vec4 p3d_Vertex;
//in vec2 p3d_MultiTexCoord0;

// output variables sent to fragment shader
out vec2 texcoord;
out vec4 col;

/*float coulomb(vec3 r, float q1, float q2) {
	float q = q1 * q2;
	float rAbsolute = sqrt(r.x*r.x+r.y*r.y+r.z*r.z);
	if (rAbsolute == 0) return 1.5e+308;
	else return  q/(rAbsolute*rAbsolute);
}*/

void main() {
	int dataPointId = gl_VertexID / 3;
	int vtxid = gl_VertexID % 3;

	vec3 norm = p3d_NormalMatrix * dataPoints[dataPointId].normal;

	col = dataPoints[dataPointId].col;

	vec4 pos = p3d_ModelViewMatrix * dataPoints[dataPointId].pos;
	// i should transform the normal vector into view-space coordinates, somehow
	// vec4(dataPoints[dataPointId].normal, 1.)
	//vec4 pos = p3d_ModelViewMatrix * vec4(dataPoints[dataPointId].pos, 1);

	if (vtxid == 0) {
		pos.y -= 0.1 * dataPoints[dataPointId].size;
		texcoord = vec2(0., -1.);
	} else if (vtxid == 1) {
		pos.x -= 0.1 * dataPoints[dataPointId].size;
		texcoord = vec2(-2., 1.5);
	} else if (vtxid == 2) {
		pos.x += 0.1 * dataPoints[dataPointId].size;
		texcoord = vec2(4., 1.5);
	}
	
	gl_Position = p3d_ProjectionMatrix * pos;
	//gl_Position = p3d_ProjectionMatrix * pos;
	//gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
	//gl_Position = p3d_ViewProjectionMatrix * p3d_Vertex;
	//texcoord = p3d_MultiTexCoord0;
}

