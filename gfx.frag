/* The Team210 font compression tool
 * Copyright (C) 2018  Alexander Kraus <nr4@z10.info>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#version 130

// Uniforms
uniform float iTime;
uniform vec2 iResolution;
uniform sampler2D iFont;
uniform float iFontWidth;

// Global constants
const vec3 c = vec3(1.,0.,-1.);

// Add objects to scene with proper antialiasing
vec4 add(vec4 sdf, vec4 sda)
{
    return vec4(
        min(sdf.x, sda.x), 
        mix(sda.gba, sdf.gba, smoothstep(-1.5/iResolution.y, 1.5/iResolution.y, sda.x))
    );
}

// Read short value from texture at index off
float rshort(float off)
{
    // Parity of offset determines which byte is required.
    float hilo = mod(off, 2.);
    // Find the pixel offset your data is in (2 unsigned shorts per pixel).
    off = floor(off/2.);
    // - Determine texture coordinates.
    //     offset = i*iFontWidth+j for (i,j) in [0,iFontWidth]^2
    //     floor(offset/iFontWidth) = floor((i*iFontwidth+j)/iFontwidth)
    //                              = floor(i)+floor(j/iFontWidth) = i
    //     mod(offset, iFontWidth) = mod(i*iFontWidth + j, iFontWidth) = j
    // - For texture coordinates (i,j) has to be rescaled to [0,1].
    // - Also we need to add an extra small offset to the texture coordinate
    //   in order to always "hit" the right pixel. Pixel width is
    //     1./iFontWidth.
    //   Half of it is in the center of the pixel.
    vec2 ind = vec2(mod(off, iFontWidth), floor(off/iFontWidth))/iFontWidth + .5/iFontWidth*c.xx;
    // Get 4 bytes of data from the texture
    vec4 block = texture(iFont, ind);
    // Select the appropriate word
    vec2 data = mix(block.rg, block.ba, hilo);
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
    
    // Read the glyph splines from the texture
    float npts = rshort(off+4.),
        xoff = off+5., 
        yoff = off+6.+npts,
        toff = off+7.+2.*npts,
        d = 1.;
    for(float i=0.; i<npts; i+=1.)
    {
        vec2 xa = ( vec2(rshort(xoff), rshort(yoff)) + dx )/65536.*12.;
        d = min(d, length(x-xa)-.01);
    }
    return d;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.yy-.5;
    
//     vec4 s = vec4(dglyph(uv, 65),c.yxy);
//     vec3 col = s.gba * smoothstep(1.5/iResolution.y, -1.5/iResolution.y, s.x);
//     fragColor = vec4(col, 1.);

    // Time varying pixel color
    vec3 col = 0.5 + 0.5*cos(uv.xyx+vec3(0,2,4));
//     col *= step(0.,dglyph(uv, 2));

    // Output to screen
    #define N 48
    float data[N] = float[N](1.,46.,3.,0.,1223.,1.,218.,12.,1966.,0.,0.,0., 2228.,4238.,6160.,8126.,8126.,8126.,5854.,3888.,12.,0.,2096.,3800.,5766.,8125.,8125.,8125.,6247.,4412.,2402.,0.,0.,12.,0.,0.,1.,0.,0.,1.,0.,0.,1.,0.,0.,1.,1.,11.);
    for(float ind = 0.; ind < N; ind += 1.)
    {
    //float ind = 2.;
        if(uv.x+.5 > 1./float(N)*ind && uv.x+.5 < 1./float(N)*(ind+1.))
            col *= step(uv.y+.5-rshort(ind)/2./data[int(ind)], 0.);
    }
    fragColor = vec4(col,1.0);// * dot(texture(iFont, uv).ba, vec2(256., 65536.));
    
//     if(rshort(0.) == 8.)
//         fragColor = c.yxyy;
}

void main()
{
    mainImage(gl_FragColor, gl_FragCoord.xy);
}
