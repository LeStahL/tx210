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
const float pi = acos(-1.);

// Global variables
float size = 1.;
vec2 carriage = vec2(0.,0.);

// Add objects to scene with proper antialiasing
vec4 add(vec4 sdf, vec4 sda)
{
    return vec4(
        min(sdf.x, sda.x), 
        mix(sda.gba, sdf.gba, smoothstep(-1.5/iResolution.y, 1.5/iResolution.y, sda.x))
    );
}

// Distance to line segment
float lineseg(vec2 x, vec2 p1, vec2 p2)
{
    vec2 d = p2-p1;
    return length(x-mix(p1, p2, clamp(dot(x-p1, d)/dot(d,d),0.,1.)));
}

// Distance to stroke for any object
float stroke(float d, float w)
{
    return abs(d)-w;
}

//distance to quadratic bezier spline with parameter t
float dist(vec2 p0,vec2 p1,vec2 p2,vec2 x,float t)
{
    t = clamp(t, 0., 1.);
    return length(x-pow(1.-t,2.)*p0-2.*(1.-t)*t*p1-t*t*p2);
}

//minimum distance to quadratic bezier spline
float spline2(vec2 p0, vec2 p1, vec2 p2, vec2 x)
{
    //coefficients for 0 = t^3 + a * t^2 + b * t + c
    vec2 E = x-p0, F = p2-2.*p1+p0, G = p1-p0;
    vec3 ai = vec3(3.*dot(G,F), 2.*dot(G,G)-dot(E,F), -dot(E,G))/dot(F,F);

	//discriminant and helpers
    float tau = ai.x/3., p = ai.y-tau*ai.x, q = - tau*(tau*tau+p)+ai.z, dis = q*q/4.+p*p*p/27.;
    
    //triple real root
    if(dis > 0.) 
    {
        vec2 ki = -.5*q*c.xx+sqrt(dis)*c.xz, ui = sign(ki)*pow(abs(ki), c.xx/3.);
        return dist(p0,p1,p2,x,ui.x+ui.y-tau);
    }
    
    //three distinct real roots
    float fac = sqrt(-4./3.*p), arg = acos(-.5*q*sqrt(-27./p/p/p))/3.;
    vec3 t = c.zxz*fac*cos(arg*c.xxx+c*pi/3.)-tau;
    return min(
        dist(p0,p1,p2,x, t.x),
        min(
            dist(p0,p1,p2,x,t.y),
            dist(p0,p1,p2,x,t.z)
        )
    );
}

// add sign to polygon distance
float intersector(vec2 p0, vec2 p1, vec2 x)
{
    vec2 k = x-p0, d = p1-p0;
    float alpha,beta;
    
    if(d.y == 0.) return 0.;
    beta = k.y/d.y;
    alpha = d.x*beta-k.x;
    
    return step(0., beta)*step(beta, 1.)*step(0., alpha);
}

// add sign to polyspline distance
float intersector(vec2 p0, vec2 p1, vec2 p2, vec2 x)
{
    // Compute coefficients for quadratic equation
    float a = p2.y-2.*p1.y+p0.y, b = 2.*p1.y-2.*p0.y, C = p0.y-x.y;
    
//     Degenerate case where a = 0
    if(p0.y == p1.y || p1.y == p2.y)
        return intersector(p0, p2, x);
    
    // Discriminant
    float dis = b*b-4.*a*C;
    
    // Solution
    if(dis == 0.)
    {
        float t = -b/2./a, 
            alpha = (1.-t)*(1.-t)*p0.x+2.*(1.-t)*t*p1.x+t*t*p2.x-x.x;
        return step(0., t)*step(t, 1.)*step(0., alpha);
    }
    else if(dis > 0.)
    {
        vec2 t = (-b*c.xx+c.xz*sqrt(dis))/2./a,
            alpha = (c.xx-t)*(c.xx-t)*p0.x+2.*(c.xx-t)*t*p1.x+t*t*p2.x-x.x;
        t = step(c.yy, t)*step(t, c.xx)*step(c.yy, alpha);
        return  t.x+t.y;
    }
    return 0.;
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
    vec2 ind = (vec2(mod(off, iFontWidth), floor(off/iFontWidth))+.05)/iFontWidth;
    // Get 4 bytes of data from the texture
    vec4 block = texture(iFont, ind);
    // Select the appropriate word
    vec2 data = mix(block.rg, block.ba, hilo);
    // Convert bytes to unsigned short. The lower bytes operate on 255,
    // the higher bytes operate on 65280, which is the maximum range 
    // of 65535 minus the lower 255.
    return dot(vec2(255., 65280.), data);
}

// Compute distance to glyph from ascii value out of the font texture.
// This function parses glyph point and control data and computes the correct
// Spline control points. Then it uses the signed distance function to
// piecewise bezier splines to get a signed distance to the font glyph.
float dglyph(vec2 x, int ascii)
{
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
    float npts = rshort(off+4.),
        xoff = off+5., 
        yoff = off+6.+npts,
        toff = off+7.+2.*npts, 
        coff = off+8.+3.*npts,
        ncont = rshort(coff-1.),
        d = 1., n = 0.;
    
    // Loop through the contours of the glyph. All of them are closed.
    for(float i=0.; i<ncont; i+=1.)
    {
        // Get the contour start and end indices from the contour array.
        float istart = 0., 
            iend = rshort(coff+i);
        if(i>0.)
            istart = rshort(coff+i-1.) + 1.;
        
        // Prepare a stack
        vec2 stack[3];
        float tstack[3];
        int stacksize = 0;
        
        // Loop through the segments
        for(float j = istart; j <= iend; j += 1.)
        {
            tstack[stacksize] = rshort(toff + j);
            stack[stacksize] = (vec2(rshort(xoff+j), rshort(yoff+j)) + dx)/65536.*size;
            ++stacksize;
            
            // Check if line segment is finished
            if(stacksize == 2)
            {
                if(tstack[0]*tstack[1] == 1)
                {
                    d = min(d, lineseg(x, stack[0], stack[1]));
                    n += intersector(stack[0], stack[1], x);
                    --j;
                    stacksize = 0;
                }
            }
            else 
            if(stacksize == 3)
            {
                if(tstack[0]*tstack[2] == 1.)
                {
                    d = min(d, spline2(stack[0], stack[1], stack[2], x));
                    n += intersector(stack[0], stack[1], stack[2], x);
                    --j;
                    stacksize = 0;
                }
                else
                {
                    vec2 p = mix(stack[1], stack[2], .5);
                    d = min(d, spline2(stack[0], stack[1], p, x));
                    n += intersector(stack[0], stack[1], p, x);
                    stack[0] = p;
                    tstack[0] = 1.;
                    --j;
                    stacksize = 1;
                }
            }
        }
        tstack[stacksize] = rshort(toff + istart);
        stack[stacksize] = (vec2(rshort(xoff+istart), rshort(yoff+istart)) + dx)/65536.*size;
        ++stacksize;
        if(stacksize == 2)
        {
            d = min(d, lineseg(x, stack[0], stack[1]));
            n += intersector(stack[0], stack[1], x);
        }
        else 
        if(stacksize == 3)
        {
            d = min(d, (spline2(stack[0], stack[1], stack[2], x)));
            n += intersector(stack[0], stack[1], stack[2], x);
        }
    }
    
    // Debug output of the spline control points
    for(float i=0.; i<npts; i+=1.)
    {
        vec2 xa = ( vec2(rshort(xoff+i), rshort(yoff+i)) + dx )/65536.*size;
        d = min(d, length(x-xa)-.002);
    }
    
//     return d;
    return mix(d, -d, mod(n, 2.));
}

mat2 rot(float t)
{
    vec2 sc = vec2(cos(t), sin(t));
    return mat2(sc*c.xz, sc.yx);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.yy-.5;
    int char = 32+int(floor(mod(iTime,126.-32.)));                                                                                                                                                                                                                                                            
//     vec4 s = vec4(dglyph(uv, 65),c.yxy);
//     vec3 col = s.gba * smoothstep(1.5/iResolution.y, -1.5/iResolution.y, s.x);
//     fragColor = vec4(col, 1.);

    // Time varying pixel color
    vec3 col = 0.5 + 0.5*cos(uv.xyx-iTime+vec3(0,2,4));
    size = .6;
    col *= smoothstep(-1.5/iResolution.y,1.5/iResolution.y,dglyph(uv, char)); //103
    fragColor = vec4(col,1.0);

    // Output to screen
/*
     #define N 556
    float data[N] = float[N](95.0, 32.0, 191.0, 33.0, 199.0, 34.0, 299.0, 35.0, 393.0, 36.0, 637.0, 37.0, 855.0, 38.0, 1104.0, 39.0, 1304.0, 40.0, 1355.0, 41.0, 1496.0, 42.0, 1637.0, 43.0, 1844.0, 44.0, 1949.0, 45.0, 2018.0, 46.0, 2066.0, 47.0, 2111.0, 48.0, 2174.0, 49.0, 2262.0, 50.0, 2358.0, 51.0, 2511.0, 52.0, 2682.0, 53.0, 2832.0, 54.0, 3009.0, 55.0, 3157.0, 56.0, 3277.0, 57.0, 3426.0, 58.0, 3574.0, 59.0, 3656.0, 60.0, 3762.0, 61.0, 3849.0, 62.0, 3943.0, 63.0, 4030.0, 64.0, 4190.0, 65.0, 4443.0, 66.0, 4641.0, 67.0, 4857.0, 68.0, 4995.0, 69.0, 5148.0, 70.0, 5343.0, 71.0, 5568.0, 72.0, 5821.0, 73.0, 6095.0, 74.0, 6263.0, 75.0, 6417.0, 76.0, 6735.0, 77.0, 6927.0, 78.0, 7254.0, 79.0, 7503.0, 80.0, 7603.0, 81.0, 7787.0, 82.0, 7965.0, 83.0, 8227.0, 84.0, 8425.0, 85.0, 8596.0, 86.0, 8842.0, 87.0, 9017.0, 88.0, 9267.0, 89.0, 9462.0, 90.0, 9730.0, 91.0, 9955.0, 92.0, 10054.0, 93.0, 10117.0, 94.0, 10216.0, 95.0, 10303.0, 96.0, 10351.0, 97.0, 10411.0, 98.0, 10571.0, 99.0, 10750.0, 100.0, 10888.0, 101.0, 11073.0, 102.0, 11197.0, 103.0, 11375.0, 104.0, 11590.0, 105.0, 11804.0, 106.0, 11940.0, 107.0, 12116.0, 108.0, 12333.0, 109.0, 12457.0, 110.0, 12715.0, 111.0, 12895.0, 112.0, 13025.0, 113.0, 13243.0, 114.0, 13469.0, 115.0, 13646.0, 116.0, 13838.0, 117.0, 14010.0, 118.0, 14190.0, 119.0, 14340.0, 120.0, 14544.0, 121.0, 14781.0, 122.0, 15001.0, 123.0, 15157.0, 124.0, 15349.0, 125.0, 15427.0, 126.0, 15622.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1442.0, 1.0, 218.0, 30.0, 4674.0, 3538.0, 3538.0, 3582.0, 4324.0, 6858.0, 7950.0, 8649.0, 11751.0, 14547.0, 14547.0, 14547.0, 14416.0, 13280.0, 9523.0, 7819.0, 7339.0, 5548.0, 1965.0, 0.0, 0.0, 0.0, 2228.0, 4237.0, 6159.0, 8125.0, 8125.0, 8125.0, 5853.0, 3888.0, 30.0, 10440.0, 11227.0, 12057.0, 12406.0, 17299.0, 29793.0, 34336.0, 37132.0, 37132.0, 37132.0, 35341.0, 34948.0, 34467.0, 29836.0, 16687.0, 11838.0, 10440.0, 10440.0, 0.0, 2096.0, 3800.0, 5766.0, 8125.0, 8125.0, 8125.0, 6247.0, 4412.0, 2402.0, 0.0, 0.0, 30.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 2.0, 17.0, 29.0, 0.0, 4849.0, 0.0, 21930.0, 28.0, 1442.0, 0.0, 131.0, 1005.0, 1442.0, 4805.0, 7689.0, 7689.0, 7689.0, 7470.0, 5723.0, 5417.0, 3670.0, 2534.0, 11053.0, 9611.0, 9742.0, 10616.0, 11053.0, 14416.0, 17300.0, 17300.0, 17300.0, 17081.0, 15334.0, 15028.0, 13281.0, 12145.0, 28.0, 0.0, 1179.0, 2577.0, 10921.0, 14940.0, 14940.0, 14940.0, 12232.0, 11620.0, 10615.0, 2577.0, 1179.0, 0.0, 0.0, 0.0, 1179.0, 2577.0, 10921.0, 14940.0, 14940.0, 14940.0, 12232.0, 11620.0, 10615.0, 2577.0, 1179.0, 0.0, 0.0, 28.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 2.0, 13.0, 27.0, 0.0, 1485.0, 1.0, 349.0, 78.0, 22498.0, 21056.0, 24245.0, 26517.0, 26517.0, 26517.0, 25338.0, 24245.0, 19615.0, 18785.0, 18392.0, 16601.0, 15596.0, 14678.0, 13368.0, 13368.0, 13368.0, 13499.0, 14154.0, 9043.0, 8213.0, 7820.0, 6029.0, 5024.0, 4107.0, 2796.0, 2796.0, 2796.0, 2927.0, 3582.0, 2316.0, 1223.0, 0.0, 0.0, 0.0, 1223.0, 2316.0, 5024.0, 6509.0, 4063.0, 2971.0, 1748.0, 1748.0, 1748.0, 2971.0, 4063.0, 7951.0, 8781.0, 9130.0, 10922.0, 11926.0, 12931.0, 14285.0, 14285.0, 14285.0, 14154.0, 13412.0, 18523.0, 19353.0, 19702.0, 21493.0, 22498.0, 23503.0, 24857.0, 24857.0, 24857.0, 24726.0, 23983.0, 25993.0, 28264.0, 28264.0, 28264.0, 27085.0, 25993.0, 17081.0, 11926.0, 10485.0, 15596.0, 78.0, 15464.0, 10397.0, 10397.0, 10397.0, 7994.0, 6771.0, 5416.0, 5416.0, 5416.0, 2621.0, 1354.0, 0.0, 0.0, 0.0, 1179.0, 2227.0, 2664.0, 3189.0, 5416.0, 5416.0, 2621.0, 1354.0, 0.0, 0.0, 0.0, 1179.0, 2227.0, 2664.0, 3189.0, 5416.0, 5416.0, 5416.0, 6771.0, 7994.0, 9173.0, 10397.0, 10397.0, 10397.0, 15464.0, 15464.0, 15464.0, 16818.0, 18041.0, 19221.0, 20444.0, 20444.0, 20444.0, 23327.0, 24594.0, 25861.0, 25861.0, 25861.0, 24769.0, 23852.0, 23458.0, 23065.0, 20444.0, 20444.0, 23327.0, 24594.0, 25861.0, 25861.0, 25861.0, 24769.0, 23852.0, 23458.0, 23065.0, 20444.0, 20444.0, 20444.0, 18041.0, 16818.0, 15464.0, 15464.0, 15464.0, 15464.0, 10397.0, 10397.0, 78.0);
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
