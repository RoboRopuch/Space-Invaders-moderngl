vertex_shader_grid='''
    #version 330
    uniform mat4 Mvp;
    in vec3 in_vert;
    void main() {
        gl_Position = Mvp * vec4(in_vert, 1.0);
    }
'''
fragment_shader_grid='''
    #version 330
    out vec4 fragColor;
    uniform vec2 u_resolution;

    void main() {
        vec2 st = gl_FragCoord.xy / u_resolution;
        fragColor = vec4(0.8,0.8,0.8, 1.0);
    }
'''

vertex_shader_ship = '''
    #version 330
    uniform mat4 Mvp;
    uniform float scale_factor;

    in vec3 in_position;
    in vec3 in_normal;
    in vec3 in_color;
    in vec3 in_origin;
    in mat3 in_basis;

    out vec3 FragPos;
    out vec3 Normal;
    out vec3 Color;

    void main() {
        vec3 worldPos = in_origin + in_basis * (in_position * scale_factor);

        worldPos.z = worldPos.z;

        // Rotate the X component using transformation matrix
        mat3 flip_matrix = mat3(
            1.0, 0.0, 0.0,
            0.0, cos(radians(90.0)), -sin(radians(90.0)),
            0.0, sin(radians(90.0)), cos(radians(90.0))
        );

        mat3 flip_matrix1 = mat3(
            cos(radians(180.0)), -sin(radians(180.0)), 0.0,
            sin(radians(180.0)), cos(radians(180.0)), 0.0,
            0.0, 0.0, 1.0
        );

        // Rotate
        worldPos = flip_matrix * flip_matrix1 * worldPos;
        FragPos = vec3(Mvp * vec4(worldPos, 1.0));
        Normal = normalize(in_basis * in_normal);
        Color = in_color;

        gl_Position = Mvp * vec4(worldPos, 1.0);
    }
'''
fragment_shader_ship = '''
    #version 330
    uniform vec3 lightPos;
    uniform vec3 viewPos;
    uniform float lightIntensity;


    in vec3 FragPos;
    in vec3 Normal;
    in vec3 Color;

    out vec4 fragColor;

    void main() {
        // Flip the Y component
        vec3 flippedFragPos = FragPos;
        flippedFragPos.y = -flippedFragPos.y;


        // Ambient
        float ambientStrength = 0.1;
        vec3 ambient = ambientStrength * Color;

        // Diffuse
        vec3 lightDir = normalize(lightPos - FragPos);
        float diff = max(dot(Normal, lightDir), 0.0);
        vec3 diffuse = diff * Color;

        // Specular
        float specularStrength = 0.5;
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, Normal);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
        vec3 specular = specularStrength * spec * vec3(1.0, 1.0, 1.0);

        vec3 result = ambient + diffuse + specular;
        fragColor = vec4(result * lightIntensity, 1.0);
    }
'''

vertex_shader_enemy = '''
    #version 330
    uniform mat4 Mvp;
    uniform float scale_factor;


    in vec3 in_position;
    in vec3 in_normal;
    in vec3 in_color;
    in vec3 in_origin;
    in mat3 in_basis;

    out vec3 FragPos;
    out vec3 Normal;
    out vec3 Color;

    void main() {
        vec3 worldPos = in_origin + in_basis * (in_position * scale_factor);

        // Rotate the Y component to fix upside-down rendering
        worldPos.y = -worldPos.y;

        // Rotate the X component using transformation matrix
        mat3 flip_matrix1 = mat3(
            1.0, 0.0, 0.0,
            0.0, cos(radians(90.0)), -sin(radians(90.0)),
            0.0, sin(radians(90.0)), cos(radians(90.0))
        );

        // Rotate
        worldPos = flip_matrix1 * worldPos;

        FragPos = vec3(Mvp * vec4(worldPos, 1.0));
        Normal = normalize(in_basis * in_normal);
        Color = in_color;

        gl_Position = Mvp * vec4(worldPos, 1.0);
    }

'''

fragment_shader_enemy = '''
    #version 330
    uniform vec3 lightPos;
    uniform vec3 viewPos;
    uniform float lightIntensity;



    in vec3 FragPos;
    in vec3 Normal;
    in vec3 Color;

    out vec4 fragColor;

    void main() {
        // Ambient
        float ambientStrength = 0.1;
        vec3 ambient = ambientStrength * Color;

        // Diffuse
        vec3 lightDir = normalize(lightPos - FragPos);
        float diff = max(dot(Normal, lightDir), 0.0);
        vec3 diffuse = diff * Color;

        // Specular
        float specularStrength = 0.5;
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, Normal);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
        vec3 specular = specularStrength * spec * vec3(1.0, 1.0, 1.0);

        vec3 result = ambient + diffuse + specular;
        fragColor = vec4(result * lightIntensity, 1.0);
    }
'''

vertex_shader_bullet = '''
    #version 330
    uniform mat4 Mvp;
    uniform float scale_factor;

    in vec3 in_position;
    in vec3 in_normal;
    in vec3 in_color;
    in vec3 in_origin;
    in mat3 in_basis;

    out vec3 FragPos;
    out vec3 Normal;
    out vec3 Color;

    void main() {
        vec3 worldPos = in_origin + in_basis * (in_position * scale_factor);

        // Rotate the Y component to fix upside-down rendering
        mat3 flip_matrix = mat3(
            1.0, 0.0, 0.0,
            0.0, cos(radians(180.0)), -sin(radians(180.0)),
            0.0, sin(radians(180.0)), cos(radians(180.0))
        );
        worldPos = flip_matrix * worldPos;

        FragPos = vec3(Mvp * vec4(worldPos, 1.0));
        Normal = normalize(in_basis * in_normal);
        Color = in_color;

        gl_Position = Mvp * vec4(worldPos, 1.0);
    }
'''

fragment_shader_bullet = '''
    #version 330
    uniform vec3 lightPos;
    uniform vec3 viewPos;
    uniform float lightIntensity;


    in vec3 FragPos;
    in vec3 Normal;
    in vec3 Color;

    out vec4 fragColor;

    void main() {
        // Ambient
        float ambientStrength = 0.1;
        vec3 ambient = ambientStrength * Color;

        // Diffuse
        vec3 lightDir = normalize(lightPos - FragPos);
        float diff = max(dot(Normal, lightDir), 0.0);
        vec3 diffuse = diff * Color;

        // Specular
        float specularStrength = 0.5;
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, Normal);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
        vec3 specular = specularStrength * spec * vec3(1.0, 1.0, 1.0);

        vec3 result = ambient + diffuse + specular;
        fragColor = vec4(result * lightIntensity, 1.0);
    }
'''

vertex_shader_game_over='''
    #version 330
    uniform mat4 Mvp;
    uniform float scale_factor;

    in vec3 in_position;
    in vec3 in_normal;
    in vec3 in_color;
    in vec3 in_origin;
    in mat3 in_basis;

    out vec3 v_vert;
    out vec3 v_norm;
    out vec3 v_color;

    void main() {
        // Transform position using origin, basis, and scale_factor
        v_vert = in_origin + in_basis * (in_position * scale_factor);

        // Rotate the position 180 degrees around the x-axis to turn it upside down
        mat3 flip_matrix = mat3(
            1.0, 0.0, 0.0,
            0.0, cos(radians(45.0)), -sin(radians(45.0)),
            0.0, sin(radians(45.0)), cos(radians(45.0))
        );

        mat3 flip_matrix1 = mat3(
            cos(radians(180.0)), -sin(radians(180.0)), 0.0,
            sin(radians(180.0)), cos(radians(180.0)), 0.0,
            0.0, 0.0, 1.0
        );


        v_vert = flip_matrix * flip_matrix1 * v_vert;

        // Transform normal using basis
        v_norm = in_basis * in_normal;

        // Pass color through
        v_color = in_color;

        gl_Position = Mvp * vec4(v_vert, 1.0);
    }
'''
fragment_shader_game_over='''
    #version 330
    uniform vec3 Light;
    in vec3 v_vert;
    in vec3 v_norm;
    in vec3 v_color;
    out vec4 fragColor;
    void main() {
        float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.8 + 0.2;
        fragColor = vec4(v_color * lum, 1.0);
    }
'''
vertex_shader_particle='''
    #version 330
    in vec2 in_vert;
    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
    }
'''
fragment_shader_particle='''
    #version 330
    out vec4 f_color;
    void main() {
        f_color = vec4(1,0,0, 1.0);
    }
'''

vertex_shader_particle_transform='''
    #version 330
    uniform vec2 Acc;
    in vec2 in_pos;
    in vec2 in_prev;
    out vec2 out_pos;
    out vec2 out_prev;
    void main() {
        vec2 velocity = in_pos - in_prev;
        out_pos = in_pos + velocity + Acc;
        out_prev = in_pos;
    }
'''
vertex_shader_particle_transform_test='''
    # version 330
    uniform vec2 Acc;
    in vec2 in_pos;
    in vec2 in_vel;
    out vec2 out_pos;
    out vec2 out_vel;
    void main() {
        vec2 velocity = in_vel + Acc;
        out_pos = in_pos + velocity;
        out_vel = in_vel;
    }
'''