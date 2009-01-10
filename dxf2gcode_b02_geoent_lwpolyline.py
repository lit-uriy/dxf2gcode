#!/usr/bin/python
# -*- coding: cp1252 -*-
#
#dxf2gcode_b02_geoent_lwpolyline
#Programmers:   Christian Kohl�ffel
#               Vinzenz Schulz
#
#Distributed under the terms of the GPL (GNU Public License)
#
#dxf2gcode is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from math import sqrt, sin, cos, atan2, radians, degrees
from dxf2gcode_b02_point import PointClass, LineGeo, PointsClass, ContourClass


class LWPolylineClass:
    def __init__(self,Nr=0,caller=None):
        self.Typ='LWPolyline'
        self.Nr = Nr
        self.Layer_Nr = 0
        self.length= 0
        self.geo=[]

        #Lesen der Geometrie
        self.Read(caller)
        
    def __str__(self):
        # how to print the object
        string=("\nTyp: LWPolyline")+\
               ("\nNr: %i" %self.Nr)+\
               ("\nLayer Nr: %i" %self.Layer_Nr)+\
               ("\nNr. of Lines: %i" %len(self.geo))+\
               ("\nlength: %0.3f" %self.length)
        
        return string

    def reverse(self):
        self.geo.reverse()
        for geo in self.geo:
            geo.reverse()    

    def App_Cont_or_Calc_IntPts(self, cont, points, i, tol):
        #Hinzuf�gen falls es keine geschlossene Polyline ist
        if self.geo[0].Pa.isintol(self.geo[-1].Pe,tol):
            self.analyse_and_opt()
            cont.append(ContourClass(len(cont),1,[[i,0]],self.length))
        else:
            points.append(PointsClass(point_nr=len(points),geo_nr=i,\
                                      Layer_Nr=self.Layer_Nr,\
                                      be=self.geo[0].Pa,
                                      en=self.geo[-1].Pe,be_cp=[],en_cp=[]))  
            
    def analyse_and_opt(self):
        summe=0

        #Richtung in welcher der Anfang liegen soll (unten links)        
        Popt=PointClass(x=-1e3,y=-1e6)
        
        #Berechnung der Fl�ch nach Gau�-Elling Positive Wert bedeutet CW
        #negativer Wert bedeutet CCW geschlossenes Polygon            
        for Line in self.geo:
            summe+=(Line.Pa.x*Line.Pe.y-Line.Pe.x*Line.Pa.y)/2
        
        if summe>0.0:
            self.reverse()
         
        #Suchen des kleinsten Startpunkts von unten Links X zuerst (Muss neue Schleife sein!)
        min_distance=self.geo[0].Pa.distance(Popt)
        min_geo_nr=0
        for geo_nr in range(1,len(self.geo)):
            if (self.geo[geo_nr].Pa.distance(Popt)<min_distance):
                min_distance=self.geo[geo_nr].Pa.distance(Popt)
                min_geo_nr=geo_nr

        #Kontur so anordnen das neuer Startpunkt am Anfang liegt
        self.geo=self.geo[min_geo_nr:len(self.geo)]+self.geo[0:min_geo_nr]
        
        
    def Read(self, caller):
        Old_Point=PointClass(0,0)
        #K�rzere Namen zuweisen
        lp=caller.line_pairs
        e=lp.index_code(0,caller.start+1)
        
        #Layer zuweisen
        s=lp.index_code(8,caller.start+1)
        self.Layer_Nr=caller.Get_Layer_Nr(lp.line_pair[s].value)

        #Pa=None f�r den ersten Punkt
        Pa=None
        
        #Number of vertices
        s=lp.index_code(90,s+1,e)
        NoOfVert=int(lp.line_pair[s].value)
        
        #Polyline flag (bit-coded); default is 0; 1 = Closed; 128 = Plinegen
        s=lp.index_code(70,s+1,e)
        LWPLClosed=int(lp.line_pair[s].value)
        
        for i in range(1, NoOfVert):
            #XWert
            s=lp.index_code(10,s+1,e)
            x=float(lp.line_pair[s].value)
            #YWert
            s=lp.index_code(20,s+1,e)
            y=float(lp.line_pair[s].value)
            Pe=PointClass(x=x,y=y)
            #Bulge
            bulge=0
            s_temp=lp.index_code(42,s+1,min(e,lp.index_code(10,s+1,e)))
            #print('stemp: %s, e: %s, next 10: %s' %(s_temp,e,lp.index_code(10,s+1,e)))
            if s_temp!=None:
                bulge=float(lp.line_pair[s_temp].value)
                s=s_temp
                
                    
            #Zuweisen der Geometrien f�r die Polyline
            if not(type(Pa)==type(None)):
                if bulge==0:
                    self.geo.append(LineGeo(Pa=Pa,Pe=Pe))
                else:
                    print bulge
                    self.geo.append(self.bulge2arc(Pa,Pe,bulge))
                    
                self.length+=self.geo[-1].length
            Pa=Pe
                   
        if (LWPLClosed==1):
            print("sollten �bereinstimmen: %s, %s" %(Pa,Pe))
            self.geo.append(LineGeo(Pa=Pa,Pe=self.geo[0].Pa))
            self.length+=self.geo[-1].length
            
        #Neuen Startwert f�r die n�chste Geometrie zur�ckgeben        
        caller.start=e
                                                          

    def get_start_end_points(self,direction=0):
        if not(direction):
            punkt, angle=self.geo[0].get_start_end_points(direction)
        elif direction:
            punkt, angle=self.geo[-1].get_start_end_points(direction)
        return punkt,angle
    
    def bulge2arc(self,Pa,Pe,bulge):
        print("LWpolyline %0.2f" %bulge)
        return LineGeo(Pa=Pa,Pe=Pe)    