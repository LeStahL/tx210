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
    off *= .5;
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
    vec2 ind = (vec2(mod(off, iFontWidth), floor(off/iFontWidth))+.5)/iFontWidth;
    // Repair end of line glitches
//     if(ind.x >=1.)
//         ind += vec2(-1., 1./iFontWidth);
    // Get 4 bytes of data from the texture
    vec4 block = texture(iFont, ind);
    // Select the appropriate word
    vec2 data = mix(block.rg, block.ba, hilo);
    // Convert bytes to unsigned short.
    return (dot(vec2(255., 65280.), data));
}

// Compute distance to glyph from ascii value
float dglyph(vec2 x, int ascii)
{
//     if(rshort(10) == 637) return 1.;
//     else return -1.;

    // Get glyph index length
    float nchars = rshort(0.);
    
    // Find character in glyph index
    float off = -1.;
    for(float i=0.; i<nchars; i+=1.)
    {
        int ord = int(rshort(1.+2.*i));
        if(ord == ascii)
        {
            off = rshort(1.+2.*i+1);
            break;
        }
    }
    // Ignore characters that are not present in the glyph index.
    if(off == -1.) return 1.;
    
    // Get short range offsets. Sign is read separately.
    vec2 dx = mix(c.xx,c.zz,vec2(rshort(off), rshort(off+2.)))*vec2(rshort(off+1.), rshort(off+3.));
    
    // Read the glyph splines from the texture
    float npts = rshort(off+4.);
    float xoff = off+5., 
        yoff = off+6.+npts,
//         coff = off 
//         toff = off+7.+2.*npts,
        d = 1.;
    for(float i=0.; i<npts; i+=1.)
    {
        vec2 xa = ( vec2(rshort(xoff+i), rshort(yoff+i)) + dx )/65536.*.5;
        d = min(d, length(x-xa)-.005);
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
    col *= smoothstep(-1.5/iResolution.y,1.5/iResolution.y,dglyph(uv, 105));
    fragColor = vec4(col,1.0);

    // Output to screen
/*
     #define N 502
    float data[N] = float[N](4.0, 46.0, 9.0, 99.0, 54.0, 100.0, 192.0, 101.0, 377.0, 0.0, 1223.0, 1.0, 218.0, 12.0, 1966.0, 0.0, 0.0, 0.0, 2228.0, 4238.0, 6160.0, 8126.0, 8126.0, 8126.0, 5854.0, 3888.0, 12.0, 0.0, 2096.0, 3800.0, 5766.0, 8125.0, 8125.0, 8125.0, 6247.0, 4412.0, 2402.0, 0.0, 0.0, 12.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 11.0, 0.0, 1398.0, 1.0, 218.0, 43.0, 4762.0, 0.0, 0.0, 0.0, 2796.0, 7252.0, 9698.0, 12101.0, 14765.0, 14765.0, 14765.0, 13149.0, 11839.0, 11009.0, 10004.0, 10004.0, 10004.0, 10179.0, 10222.0, 10441.0, 10441.0, 10441.0, 9873.0, 9349.0, 8344.0, 6596.0, 5548.0, 5548.0, 5548.0, 9960.0, 11751.0, 15901.0, 17911.0, 18435.0, 19090.0, 19658.0, 20313.0, 20313.0, 20313.0, 19483.0, 17430.0, 11707.0, 9043.0, 43.0, 0.0, 4849.0, 8824.0, 12362.0, 17692.0, 20575.0, 20575.0, 20575.0, 17736.0, 15508.0, 13673.0, 11139.0, 11139.0, 11139.0, 11926.0, 12625.0, 12930.0, 13717.0, 13891.0, 14547.0, 15115.0, 15682.0, 16294.0, 16294.0, 16294.0, 14503.0, 11445.0, 9610.0, 4543.0, 4543.0, 4543.0, 6945.0, 9348.0, 9960.0, 9960.0, 9960.0, 8911.0, 7994.0, 6334.0, 5285.0, 2752.0, 0.0, 0.0, 43.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 42.0, 0.0, 1529.0, 1.0, 218.0, 58.0, 25949.0, 26604.0, 26604.0, 26604.0, 25774.0, 23983.0, 19702.0, 17605.0, 14285.0, 12538.0, 10703.0, 7951.0, 6116.0, 3451.0, 0.0, 0.0, 0.0, 2971.0, 8169.0, 11402.0, 12232.0, 16906.0, 20707.0, 22585.0, 25075.0, 25075.0, 25075.0, 20270.0, 16251.0, 16426.0, 17605.0, 18522.0, 19702.0, 22148.0, 24201.0, 24726.0, 25381.0, 19396.0, 17736.0, 16557.0, 16294.0, 21187.0, 21187.0, 21187.0, 20619.0, 20226.0, 8475.0, 10135.0, 11402.0, 10965.0, 10965.0, 10965.0, 11052.0, 8650.0, 5461.0, 5461.0, 5461.0, 7645.0, 58.0, 9960.0, 8911.0, 7994.0, 6247.0, 5285.0, 3101.0, 0.0, 0.0, 0.0, 3888.0, 1572.0, 0.0, 0.0, 0.0, 3975.0, 7164.0, 10659.0, 16644.0, 20444.0, 20794.0, 29269.0, 41282.0, 41282.0, 41282.0, 37874.0, 34423.0, 29531.0, 16425.0, 9523.0, 6989.0, 4805.0, 4805.0, 4805.0, 6902.0, 9348.0, 9960.0, 9960.0, 37001.0, 31103.0, 21580.0, 16381.0, 27041.0, 33506.0, 35166.0, 37001.0, 37001.0, 4412.0, 5766.0, 7601.0, 9960.0, 12887.0, 13935.0, 16294.0, 15551.0, 10615.0, 7601.0, 4412.0, 4412.0, 58.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 3.0, 36.0, 45.0, 57.0, 0.0, 1442.0, 1.0, 218.0, 38.0, 20706.0, 21362.0, 21362.0, 21362.0, 20532.0, 18915.0, 13018.0, 9654.0, 5067.0, 0.0, 0.0, 0.0, 2533.0, 7033.0, 9872.0, 12406.0, 15464.0, 15464.0, 15464.0, 11139.0, 5984.0, 7077.0, 10135.0, 12100.0, 17124.0, 18959.0, 19483.0, 20138.0, 7513.0, 5285.0, 5285.0, 5285.0, 7863.0, 10833.0, 10833.0, 10833.0, 9916.0, 9130.0, 38.0, 9960.0, 8911.0, 7994.0, 6247.0, 5285.0, 3320.0, 0.0, 0.0, 0.0, 4980.0, 9304.0, 12319.0, 17517.0, 20575.0, 20575.0, 20575.0, 17561.0, 14984.0, 11969.0, 7644.0, 6378.0, 4368.0, 4368.0, 4368.0, 7120.0, 9348.0, 9960.0, 9960.0, 16294.0, 12537.0, 9872.0, 9785.0, 10397.0, 12843.0, 14459.0, 15289.0, 16294.0, 16294.0, 38.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 2.0, 27.0, 37.0, 0.0);
    for(float ind = 0.; ind < N; ind += 1.)
    {
    //float ind = 2.;
        if(uv.x+.5 > 1./float(N)*ind && uv.x+.5 < 1./float(N)*(ind+1.))
            col *= mix(.6,1.1, mod(ind,2.))*step(uv.y+.5-rshort(ind)/2./data[int(ind)], 0.);
    }
    fragColor = vec4(col,1.0);// * dot(texture(iFont, uv).ba, vec2(256., 65536.)); */
    
//     if(rshort(0.) == 8.)
//         fragColor = c.yxyy;
}

void main()
{
    mainImage(gl_FragColor, gl_FragCoord.xy);
}
