# The Team210 mic to visuals tool for DJs
# Copyright (C) 2018  Alexander Kraus <nr4@z10.info>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

cmake_minimum_required(VERSION 2.8)

project(mic-visuals)

if(WIN32)
#     include_directories("C:\\Users\\NR4\\Downloads\\fftw-3.3.8\\api")
#     link_directories("C:\\Users\\NR4\\Downloads\\fftw-3.3.8\\build\\Release")
    
    add_definitions(/Gy /O1 /fp:fast /GR- /GS- /MT)
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /ENTRY:demo /SUBSYSTEM:Windows  /OPT:REF  /OPT:ICF=10 /VERBOSE /NODEFAULTLIB") 
    add_executable(fontdemo fontdemo.c)
    
    # for debug output: User32.lib ucrt.lib msvcrt.lib
    target_link_libraries(fontdemo opengl32.lib Winmm.lib User32.lib ucrt.lib msvcrt.lib)
endif()

