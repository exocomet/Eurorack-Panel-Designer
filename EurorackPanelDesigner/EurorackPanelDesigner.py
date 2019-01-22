#!/usr/bin/env python
#
# Eurorack Panel Designer by THX2112, Neon22
# https://github.com/THX2112/Eurorack-Panel-Designer
# https://github.com/Neon22/Eurorack-Panel-Designer
#
# v4
# - reference: http://www.doepfer.de/a100_man/a100m_e.htm
# Adds lasercutting color and refactoring

import sys
import math

import inkex
import simplestyle



colors = dict(
    orange = '#f6921e',
    blue = '#0000ff',
    red = '#ff0000',
    grey = '#eeeeee',
    darkgrey = '#666666',
    white = '#ffffff',
    panel_color = '#e6e6e6'
)


class EurorackPanelEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

        self.OptionParser.add_option('-t', '--hp', action='store', type='int', dest='hp', default=6, help='Panel HP?')
        self.OptionParser.add_option('-o', '--offset', action='store', type='float', dest='offset', default=0.36, help='Amount of material to remove for fitting?')
        self.OptionParser.add_option('-s', '--symmetrical', action='store', type='inkbool', dest='symmetrical', default='False', help='Remove material from both sides?')
        self.OptionParser.add_option('-v', '--oval', action='store', type='inkbool', dest='oval', default='False', help='Oval holes?')
        self.OptionParser.add_option('-c', '--centers', action='store', type='inkbool', dest='centers', default='False', help='Mark centers?')
        self.OptionParser.add_option('-l', '--lasercut', action='store', type='inkbool', dest='lasercut', default='False', help='Lasercut style?')
        self.OptionParser.add_option('-w', '--lasercut-width', action='store', type='float', dest='lasercut_width', default='0.01', help='Lasercut width [mm]')
        self.OptionParser.add_option('-L', '--layers', action='store', type='inkbool', dest='layers', default='False', help='Creates additional layers.')
        self.OptionParser.add_option('-C', '--components', action='store', type='inkbool', dest='components', default='False', help='Add component templates.')

        self.panel_root_element = None


    def create_layer(self, name):
        svg = self.document.getroot()
        newLayer = inkex.etree.SubElement(svg, 'g')
        newLayer.set(inkex.addNS('label', 'inkscape'), name)
        newLayer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        return newLayer


    def get_style(self, *args, **kwargs):
        '''Some default style settings'''
        style = {}
        if self.options.lasercut:
            style['stroke'] = colors['blue']
            style['stroke-width'] = self.options.lasercut_width
            style['fill'] = 'none'
        else:
            style['stroke'] = kwargs.get('stroke', colors['darkgrey'])
            style['stroke-width'] = kwargs.get('strokewidth', '0.0mm')
            style['fill'] = kwargs.get('fill', colors['white'])

        return simplestyle.formatStyle(style)


    def draw_SVG_circle(self, x, y, d, parent):
        attr = {
            'style': self.get_style(),
            inkex.addNS('cx', 'sodipodi'): str(x),
            inkex.addNS('cy', 'sodipodi'): str(y),
            inkex.addNS('rx', 'sodipodi'): str(d/2),
            inkex.addNS('ry', 'sodipodi'): str(d/2),
            inkex.addNS('open', 'sodipodi'): 'false',
            inkex.addNS('start', 'sodipodi'): str(0),
            inkex.addNS('end', 'sodipodi'): str(2 * math.pi),
            inkex.addNS('type', 'sodipodi'): 'arc',
        }
        return inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attr)



    def draw_SVG_panel(self, w, h, x, y, rx, ry, parent):
        """Draw the Basic Panel Shape"""
        style = self.get_style(fill=colors['panel_color'])

        attr = {
            'style': style,
            'height': str(h),
            'width': str(w),
            'x': str(x),
            'y': str(y),
            'rx': str(rx),
            'ry': str(ry)
        }
        return inkex.etree.SubElement(parent, inkex.addNS('rect', 'svg'), attr)


    def draw_SVG_square(self, (w, h), (x, y), (rx, ry), parent):
        """Draw Oval shaped holes"""
        style = self.get_style()
        attr = {
            'style': style,
            'height': str(h),
            'width': str(w),
            'x': str(x),
            'y': str(y),
            'rx': str(rx),
            'ry': str(ry)
        }
        return inkex.etree.SubElement(parent, inkex.addNS('rect', 'svg'), attr)


    def draw_SVG_ellipse(self, (rx, ry), (cx, cy), parent):
        style = self.get_style()
        ell_attr = {
            'style': style,
            inkex.addNS('cx', 'sodipodi'): str(cx),
            inkex.addNS('cy', 'sodipodi'): str(cy),
            inkex.addNS('rx', 'sodipodi'): str(rx),
            inkex.addNS('ry', 'sodipodi'): str(ry),
            #inkex.addNS('start', 'sodipodi'): str(start),
            #inkex.addNS('end', 'sodipodi'): str(end),
            inkex.addNS('open', 'sodipodi'): 'false',
            inkex.addNS('type', 'sodipodi'): 'arc'
        }
        inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attr)


    def draw_SVG_line(self, (x1, y1), (x2, y2), parent):
        style = self.get_style(stroke=colors['orange'], strokewidth='0.2')
        line_attr = {
            'style': style,
            'd': 'M %s,%s L %s,%s' % (x1, y1, x2, y2)
        }
        inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), line_attr)


    def draw_center_mark(self, x, y, w=2, h=2):
        parent = self.panel_root_element
        self.draw_SVG_line((x-w/2, y), (x+w/2, y), parent)
        self.draw_SVG_line((x, y+h/2), (x, y-h/2), parent)


    def add_potentiometer(self, x, y, d=7):
        parent = self.panel_root_element
        p = self.draw_SVG_circle(x, y, d, parent)
        if self.options.centers:
            self.draw_center_mark(x, y)


    def add_led(self, x, y, d=5):
        parent = self.panel_root_element
        self.draw_SVG_circle(x, y, d, parent)
        if self.options.centers:
            self.draw_center_mark(x, y)


    def add_audiosocket(self, x, y, d=6):
        parent = self.panel_root_element
        self.draw_SVG_circle(x, y, d, parent)
        if self.options.centers:
            self.draw_center_mark(x, y)


    def add_components(self):
        self.add_potentiometer(10, 20, 6)
        self.add_led(10, 30, 3)
        self.add_led(10, 40, 5)
        self.add_audiosocket(10, 50)


    def effect(self):
        hp = self.options.hp
        symmetrical = self.options.symmetrical
        offset = self.options.offset
        oval = self.options.oval
        centers = self.options.centers
        unitfactor = self.unittouu('1mm') # all our dimensions are in mm

        # Dimensions
        height = 128.5
        if symmetrical:
            width = 7.5 + ((hp - 3) * 5.08) + 7.5
        else:
            width = (hp * 5.08) - offset

        # Calculate final width and height of panel
        pheight = height * unitfactor
        pwidth =  width * unitfactor

        # Build top level group to put everything in
        # Put in in the centre of current view
        group_transform = 'translate(%s,%s)' % (self.view_center[0]-pwidth/2, self.view_center[1]-pheight/2 )
        group_name = 'EuroPanel'
        group_attribs = {
            inkex.addNS('label', 'inkscape'): group_name,
            'transform': group_transform
        }
        group = inkex.etree.SubElement(self.current_layer, 'g', group_attribs)
        self.panel_root_element = group

        # Draw Panel
        self.draw_SVG_panel(pwidth, pheight, 0, 0, 0, 0, group)

        ## margins
        TopHoles = 3.0
        BottomHoles = 125.5
        LeftHoles = 7.5
        RightHoles = ((hp - 3.0) * 5.08) + 7.5
        HoleRadius = 1.6

        leftH = LeftHoles * unitfactor
        rightH = RightHoles * unitfactor
        bottomH = BottomHoles * unitfactor
        topH = TopHoles * unitfactor
        holeR = HoleRadius * unitfactor
        gap = holeR/2

        if oval == False: # Draw Round holes
            rx = HoleRadius * unitfactor
            ry = rx # circles

            self.draw_SVG_ellipse((rx, ry), (leftH, bottomH), group)
            self.draw_SVG_ellipse((rx, ry), (leftH, topH), group)

            # if hp >= 5:
            #     self.draw_SVG_ellipse((rx, ry), (rightH, bottomH), group)
            #     self.draw_SVG_ellipse((rx, ry), (rightH, topH), group)

            # if self.options.centers:
            #     if hp < 5:
            #         self.draw_center_mark(rx, ry)
            #     else:


            # Draw Left-side Centers
            if centers == True:
                # Bottom Left Centers
                # Horizontal Line
                self.draw_SVG_line( (leftH-holeR+gap, bottomH), (leftH+holeR-gap, bottomH), group)
                # Vertical Line
                self.draw_SVG_line( (leftH, bottomH+holeR-gap), (leftH, bottomH-holeR+gap), group)
                # Top Left Centers
                # Horizontal Line
                self.draw_SVG_line( (leftH-holeR+gap, topH), (leftH+holeR-gap, topH), group)
                # Vertical Line
                self.draw_SVG_line( (leftH, topH+holeR-gap), (leftH, topH-holeR+gap), group)
            # Draw the Righthand side Mounting holes
            if hp >= 5:
                # Bottom Right
                self.draw_SVG_ellipse((rx, ry), (rightH, bottomH), group)
                # Top Right
                self.draw_SVG_ellipse((rx, ry), (rightH, topH), group)
                # Draw Right-side Centers
                if centers == True:
                    # Bottom Right Centers - Horizontal Line
                    self.draw_SVG_line( (rightH-holeR+gap, bottomH), (rightH+holeR-gap, bottomH), group)
                    # Vertical Line
                    self.draw_SVG_line( (rightH, bottomH+holeR-gap), (rightH, bottomH-holeR+gap), group)
                    # Top Right Centers - Horizontal Line
                    self.draw_SVG_line( (rightH-holeR+gap, topH), (rightH+holeR-gap, topH), group)
                    # Vertical Line
                    self.draw_SVG_line( (rightH, topH+holeR-gap), (rightH, topH-holeR+gap), group)

        else: # oval == True
            # Oval Holes: (a square with rounded corners)
            oval_size = 5.5  # 3.2mm hole. Oval is 5.5mm across
            oval_stretch = oval_size/2 # 2.75
            #
            gapH = oval_stretch*unitfactor - gap
            oval_offset = (oval_stretch-HoleRadius)*unitfactor # 1.15
            oval_width = oval_size*unitfactor
            oval_height = HoleRadius*2*unitfactor

            # Bottom Left
            self.draw_SVG_square((oval_width,oval_height), (leftH-oval_stretch*unitfactor,bottomH-holeR), (holeR,0), group)
            # Top Left
            self.draw_SVG_square((oval_width,oval_height), (leftH-oval_stretch*unitfactor,topH-holeR), (holeR,0), group)

            # Draw Left-side Centers
            if centers == True:
                # Bottom Left Centers - Horizontal Line
                self.draw_SVG_line( (leftH-gapH, bottomH), (leftH+gapH, bottomH), group)
                # Vertical Lines
                offset = -oval_offset
                for i in range(3):
                    self.draw_SVG_line( (leftH+offset, bottomH+holeR-gap), (leftH+offset, bottomH-holeR+gap), group)
                    offset += oval_offset
                # Top Left Centers - Horizontal Line
                self.draw_SVG_line( (leftH-gapH, topH), (leftH+gapH, topH), group)
                # Vertical Lines
                offset = -oval_offset
                for i in range(3):
                    self.draw_SVG_line( (leftH+offset, topH+holeR-gap), (leftH+offset, topH-holeR+gap), group)
                    offset += oval_offset

            # Draw the Righthand side Mounting holes
            if hp >= 5:
                # Bottom Right
                self.draw_SVG_square((oval_width,oval_height), (rightH-oval_stretch*unitfactor,bottomH-holeR), (holeR,0), group)
                # Top Right
                self.draw_SVG_square((oval_width,oval_height), (rightH-oval_stretch*unitfactor,topH-holeR), (holeR,0), group)

                # Draw Left-side Centers
                if centers == True:
                    # Bottom Right Centers - Horizontal Line
                    self.draw_SVG_line( (rightH-gapH, bottomH), (rightH+gapH, bottomH), group)
                    # Left Vertical Line
                    # Vertical Lines
                    offset = -oval_offset
                    for i in range(3):
                        self.draw_SVG_line( (rightH+offset, bottomH+holeR-gap), (rightH+offset, bottomH-holeR+gap), group)
                        offset += oval_offset
                    # Top Right Centers
                    # Horizontal Line
                    self.draw_SVG_line( (rightH-gapH, topH), (rightH+gapH, topH), group)
                    # Left Vertical Line
                    offset = -oval_offset
                    for i in range(3):
                        self.draw_SVG_line( (rightH+offset, topH+holeR-gap), (rightH+offset, topH-holeR+gap), group)
                        offset += oval_offset

        if self.options.components:
            self.add_components()


# Create effect instance and apply it.
effect = EurorackPanelEffect()
effect.affect()