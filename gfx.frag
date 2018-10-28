#version 130

// Uniforms
uniform float iTime;
uniform vec2 iResolution;
uniform sampler2D iFont;
uniform float iFontWidth;

// Global constants
const vec3 c = vec3(1.,0.,-1.);

// Read short value from texture at index off
float rshort(float off)
{
    // Determine texture coordinates
    vec2 ind = vec2(mod(off, iFontWidth), floor(off/iFontWidth))/iFontWidth;
    // 4 bytes of data
    vec4 block = texture(iFont, ind);
    // Select the appropriate word
    vec2 data = mix(block.rg, block.ba, mod(off, 2.));
    // Convert bytes to unsigned short.
    return dot(vec2(256., 65536.), data);
}

// Compute distance to glyph from ascii value
float dglyph(vec2 x, int ascii)
{
    // Get glyph index length
    float nchars = rshort(0.);
    
    // Find character in glyph index
    float off;
    for(float i=0.; i<nchars; i+=1.)
    {
        float ord = rshort(1.+2.*i);
        if(ord == float(ascii))
        {
            off = rshort(1.+2.*i+1);
            break;
        }
    }
    
    // Get short range offsets
    vec2 dx = mix(c.xx,c.zz,vec2(rshort(off), rshort(off+2.)))*vec2(rshort(off+1.), rshort(off+3.));
    
    // Get number of points
    float npts = rshort(off+4.);
    
    return x.x + .1*float(nchars);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.yy;

    // Time varying pixel color
    vec3 col = 0.5 + 0.5*cos(uv.xyx+vec3(0,2,4));
//     col *= step(0.,dglyph(uv, 2));

    // Output to screen
    float ind = 0;
    col *= step(uv.y-rshort(ind)/10., 0.);
    fragColor = vec4(col,1.0);// * dot(texture(iFont, uv).ba, vec2(256., 65536.));
    
    if(rshort(0.) == 8.)
        fragColor = c.yxyy;
}

void main()
{
    mainImage(gl_FragColor, gl_FragCoord.xy);
}
