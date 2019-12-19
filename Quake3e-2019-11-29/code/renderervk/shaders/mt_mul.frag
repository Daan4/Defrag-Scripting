#version 450

// layout set = 1 - uniform
layout(set = 1, binding = 0) uniform sampler2D texture0;
layout(set = 2, binding = 0) uniform sampler2D texture1;

layout(location = 0) in vec4 frag_color;
layout(location = 1) in vec2 frag_tex_coord0;
layout(location = 2) in vec2 frag_tex_coord1;

layout(location = 0) out vec4 out_color;

layout (constant_id = 0) const int alpha_test_func = 0;
layout (constant_id = 1) const float alpha_test_value = 0.0;

void main() {
	out_color = frag_color * texture(texture0, frag_tex_coord0) * texture(texture1, frag_tex_coord1);

	if (alpha_test_func == 1) {
		if (out_color.a == alpha_test_value) discard;
	} else if (alpha_test_func == 2) {
		if (out_color.a >= alpha_test_value) discard;
	} else if (alpha_test_func == 3) {
		if (out_color.a < alpha_test_value) discard;
	}
}
