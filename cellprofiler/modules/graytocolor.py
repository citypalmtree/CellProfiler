'''
<b> Gray to Color</b> takes grayscale images and and produces a
color image from them 
<hr>

This module takes grayscale images as input and assigns them to colors in a red, green,
blue (RGB) image or a cyan, magenta, yellow, black (CMYK) image. Each color's brightness can be adjusted independently by using relative weights.

<p>See also <b>ColorToGray</b>.'''

# CellProfiler is distributed under the GNU General Public License.
# See the accompanying file LICENSE for details.
# 
# Developed by the Broad Institute
# Copyright 2003-2010
# 
# Please see the AUTHORS file for credits.
# 
# Website: http://www.cellprofiler.org

__version__="$Revision$"

import numpy as np

import cellprofiler.cpimage as cpi
import cellprofiler.cpmodule as cpm
import cellprofiler.settings as cps

OFF_RED_IMAGE_NAME = 0
OFF_GREEN_IMAGE_NAME = 1
OFF_BLUE_IMAGE_NAME = 2
OFF_RGB_IMAGE_NAME = 3
OFF_RED_ADJUSTMENT_FACTOR = 4
OFF_GREEN_ADJUSTMENT_FACTOR = 5
OFF_BLUE_ADJUSTMENT_FACTOR = 6

SCHEME_RGB = "RGB"
SCHEME_CMYK = "CMYK"
SCHEME_STACK = "Stack"
LEAVE_THIS_BLACK = "Leave this black"

class GrayToColor(cpm.CPModule):
    module_name = 'GrayToColor'
    variable_revision_number = 2
    category = "Image Processing"
    def create_settings(self):
        self.scheme_choice = cps.Choice(
            "Select a color scheme",
            [SCHEME_RGB, SCHEME_CMYK, SCHEME_STACK],
            doc="""This module can use one of two color schemes to combine images:<br/>
            <ul><li><i>RGB</i>: Each input image determines the intensity of
            one of the color channels: red, green, and blue.</li>
            <li><i>CMYK</i>: Three of the input images are combined to determine
            the colors (cyan, magenta, and yellow) and a fourth is used only for brightness. The cyan
            image adds equally to the green and blue intensities. The magenta
            image adds equally to the red and blue intensities. The yellow
            image adds equally to the red and green intensities.</li>
            <li><i>Stack</i>: The channels are stacked in order (arbitrary number).</li></ul>""")
        # # # # # # # # # # # # # # # #
        # 
        # RGB settings
        #
        # # # # # # # # # # # # # # # #
        self.red_image_name = cps.ImageNameSubscriber("Select the input image to be colored red",
                                                      can_be_blank = True,
                                                      blank_text = LEAVE_THIS_BLACK)
        
        self.green_image_name = cps.ImageNameSubscriber("Select the input image to be colored green",
                                                        can_be_blank = True,
                                                        blank_text = LEAVE_THIS_BLACK)
        
        self.blue_image_name = cps.ImageNameSubscriber("Select the input image to be colored blue",
                                                       can_be_blank = True,
                                                       blank_text = LEAVE_THIS_BLACK)
        self.rgb_image_name = cps.ImageNameProvider("Name the output image",
                                                    "ColorImage")
        
        self.red_adjustment_factor = cps.Float("Relative weight for the red image",
                                               value=1,
                                               minval=0,doc='''<i>(Used only if RGB is selected)</i><br>
					       Enter the relative weights: If all relative weights are equal, all three 
					       colors contribute equally in the final image. To weight colors relative to each other, 
					       increase or decrease the relative weights.''')
        
        self.green_adjustment_factor = cps.Float("Relative weight for the green image",
                                                 value=1,
                                                 minval=0,doc='''<i>(Used only if RGB is selected)</i><br>
					       Enter the relative weights: If all relative weights are equal, all three 
					       colors contribute equally in the final image. To weight colors relative to each other, 
					       increase or decrease the relative weights.''')
        
        self.blue_adjustment_factor = cps.Float("Relative weight for the blue image",
                                                value=1,
                                                minval=0,doc='''<i>(Used only if RGB is selected)</i><br>
					       Enter the relative weights: If all relative weights are equal, all three 
					       colors contribute equally in the final image. To weight colors relative to each other, 
					       increase or decrease the relative weights.''')
        # # # # # # # # # # # # # #
        #
        # CYMK settings
        #
        # # # # # # # # # # # # # #
        self.cyan_image_name = cps.ImageNameSubscriber(
            "Select the input image to be colored cyan", can_be_blank = True,
            blank_text = LEAVE_THIS_BLACK)
        
        self.magenta_image_name = cps.ImageNameSubscriber(
            "Select the input image to be colored magenta", can_be_blank = True,
            blank_text = LEAVE_THIS_BLACK)
        
        self.yellow_image_name = cps.ImageNameSubscriber(
            "Select the input image to be colored yellow", can_be_blank = True,
            blank_text = LEAVE_THIS_BLACK)
        
        self.gray_image_name = cps.ImageNameSubscriber(
            "Select the input image that determines brightness", can_be_blank = True,
            blank_text = LEAVE_THIS_BLACK)
        
        self.cyan_adjustment_factor = cps.Float(
            "Relative weight for the cyan image", value=1,
            minval=0,doc='''<i>(Used only if CMYK is selected)</i><br>
			Enter the relative weights: If all relative weights are equal, all 
                        colors contribute equally in the final image. To weight colors relative to each other, 
                        increase or decrease the relative weights.''')
        
        self.magenta_adjustment_factor = cps.Float(
            "Relative weight for the magenta image", value=1,
            minval=0,doc='''<i>(Used only if CMYK is selected)</i><br>
                            Enter the relative weights: If all relative weights are equal, all 
                            colors contribute equally in the final image. To weight colors relative to each other, 
                            increase or decrease the relative weights.''')
        
        self.yellow_adjustment_factor = cps.Float(
            "Relative weight for the yellow image", value=1,
            minval=0,doc='''<i>(Used only if CMYK is selected)</i><br>
                            Enter the relative weights: If all relative weights are equal, all 
                            colors contribute equally in the final image. To weight colors relative to each other, 
                            increase or decrease the relative weights.''')
        
        self.gray_adjustment_factor = cps.Float(
            "Relative weight for the brightness image", value=1,
            minval=0,doc='''<i>(Used only if CMYK is selected)</i><br>
                            Enter the relative weights: If all relative weights are equal, all 
                            colors contribute equally in the final image. To weight colors relative to each other, 
                            increase or decrease the relative weights.''')
    
        # # # # # # # # # # # # # #
        #
        # Stack settings
        #
        # # # # # # # # # # # # # #

        self.stack_channels = []
        self.add_stack_channel_cb(can_remove = False)
        self.add_stack_channel = cps.DoSomething("","Add another channel", self.add_stack_channel_cb)

    def add_stack_channel_cb(self, can_remove=True):
        group = cps.SettingsGroup()
        group.append("image_name", cps.ImageNameSubscriber("Select the input image to add to the stacked image", "None"))
        if can_remove:
            group.append("remover", cps.RemoveSettingButton("", "Remove this image", self.stack_channels, group))
        self.stack_channels.append(group)

    @property
    def color_scheme_settings(self):
        if self.scheme_choice == SCHEME_RGB:
            return [ColorSchemeSettings(self.red_image_name,
                                        self.red_adjustment_factor, 1,0,0),
                    ColorSchemeSettings(self.green_image_name,
                                        self.green_adjustment_factor, 0,1,0),
                    ColorSchemeSettings(self.blue_image_name,
                                        self.blue_adjustment_factor, 0,0,1)]
        elif self.scheme_choice == SCHEME_CMYK:
            return [ColorSchemeSettings(self.cyan_image_name,
                                        self.cyan_adjustment_factor, 0,.5,.5),
                    ColorSchemeSettings(self.magenta_image_name,
                                        self.magenta_adjustment_factor, .5, .5, 0),
                    ColorSchemeSettings(self.yellow_image_name,
                                        self.yellow_adjustment_factor, .5, 0, .5),
                    ColorSchemeSettings(self.gray_image_name,
                                        self.gray_adjustment_factor, 
                                        1./3., 1./3., 1./3.)]
        else:
            return []

    def settings(self):
        result = [self.scheme_choice,
                 self.red_image_name,self.green_image_name,self.blue_image_name,
                 self.rgb_image_name, self.red_adjustment_factor, 
                 self.green_adjustment_factor, self.blue_adjustment_factor,
                 self.cyan_image_name,self.magenta_image_name, 
                 self.yellow_image_name, self.gray_image_name,
                 self.cyan_adjustment_factor, self.magenta_adjustment_factor,
                 self.yellow_adjustment_factor, self.gray_adjustment_factor]
        result += [sc.image_name for sc in self.stack_channels]
        return result
    
    def prepare_settings(self, setting_values):
        num_stack_images = max(len(setting_values) - 16, 1)
        del self.stack_channels[num_stack_images:]
        while len(self.stack_channels) < num_stack_images:
            self.add_stack_channel_cb()

    def visible_settings(self):
        result = [self.scheme_choice]
        result += [color_scheme_setting.image_name 
                   for color_scheme_setting in self.color_scheme_settings]
        result += [self.rgb_image_name]
        for color_scheme_setting in self.color_scheme_settings:
            if not color_scheme_setting.image_name.is_blank:
                result.append(color_scheme_setting.adjustment_factor)
        if self.scheme_choice == SCHEME_STACK:
            for sc_group in self.stack_channels:
                result += sc_group.visible_settings()
            result += [self.add_stack_channel]
        return result
    
    def validate_module(self,pipeline):
        """Make sure that the module's settings are consistent
        
        We need at least one image name to be filled in
        """
        if self.scheme_choice != SCHEME_STACK:
            if all([color_scheme_setting.image_name.is_blank
                    for color_scheme_setting in self.color_scheme_settings]):
                raise cps.ValidationError("At least one of the images must not be blank",\
                                              self.color_scheme_settings[0].image_name)
    def run(self,workspace):
        parent_image = None
        parent_image_name = None
        imgset = workspace.image_set
        rgb_pixel_data = None
        input_image_settings = []
        if self.scheme_choice != SCHEME_STACK:
            for color_scheme_setting in self.color_scheme_settings:
                if color_scheme_setting.image_name.is_blank:
                    continue
                input_image_settings.append(color_scheme_setting.image_name)
                image = imgset.get_image(color_scheme_setting.image_name.value,
                                         must_be_grayscale=True)
                multiplier = (color_scheme_setting.intensities *
                              color_scheme_setting.adjustment_factor.value)
                pixel_data = image.pixel_data
                if parent_image != None:
                    if (parent_image.pixel_data.shape != pixel_data.shape):
                        raise ValueError("The %s image and %s image have different sizes (%s vs %s)"%
                                         (parent_image_name, 
                                          color_scheme_setting.image_name.value,
                                          parent_image.pixel_data.shape,
                                          image.pixel_data.shape))
                    rgb_pixel_data += np.dstack([pixel_data]*3) * multiplier
                else:
                    parent_image = image
                    parent_image_name = color_scheme_setting.image_name.value
                    rgb_pixel_data = np.dstack([pixel_data]*3) * multiplier
        else:
            source_channels = [imgset.get_image(sc.image_name, must_be_grayscale=True).pixel_data 
                               for sc in self.stack_channels]
            parent_image = source_channels[0]
            for idx, pd in enumerate(source_channels):
                if pd.shape != source_channels[0].shape:
                    raise ValueError("The %s image and %s image have different sizes (%s vs %s)"%
                                     (self.stack_channels[0].image_name.value,
                                      self.stack_channels[idx].image_name.value,
                                      source_channels[0].shape,
                                      pd.pixel_data.shape))
            rgb_pixel_data = np.dstack(source_channels)
            print "stacked", rgb_pixel_data.shape, len(source_channels)

        ###############
        # Draw images #
        ###############
        if workspace.frame != None:
            title = "Gray to color #%d"%(self.module_num)
            if self.scheme_choice == SCHEME_CMYK:
                subplots = (3,2)
                subplot_indices = ((0,0),(0,1),(1,0),(1,1),(2,0))
                color_subplot = (2,1)
            elif self.scheme_choice == SCHEME_RGB:
                subplots = (2,2)
                subplot_indices = ((0,0),(0,1),(1,0))
                color_subplot = (1,1)
            else:
                subplots = (1, 1)
                subplot_indices = []
                color_subplot = (0, 0)
            my_frame = workspace.create_or_find_figure(title, subplots)
            for i, input_image_setting in enumerate(input_image_settings):
                x,y = subplot_indices[i]
                my_frame.subplot(x,y).set_visible(True)
                image = imgset.get_image(input_image_setting.value,
                                         must_be_grayscale=True)
                my_frame.subplot_imshow_grayscale(x,y,image.pixel_data,
                                                  title=input_image_setting.value,
                                                  sharex = my_frame.subplot(0,0),
                                                  sharey = my_frame.subplot(0,0))
            for x,y in subplot_indices[len(input_image_settings):]:
                my_frame.subplot(x,y).set_visible(False)
            my_frame.subplot_imshow(color_subplot[0], color_subplot[1]
                                    ,rgb_pixel_data,
                                    title=self.rgb_image_name.value,
                                    sharex = my_frame.subplot(0,0),
                                    sharey = my_frame.subplot(0,0))
        ##############
        # Save image #
        ##############
        rgb_image = cpi.Image(rgb_pixel_data, parent_image = parent_image)
        imgset.add(self.rgb_image_name.value, rgb_image)
    
    def upgrade_settings(self,setting_values,variable_revision_number,
                         module_name,from_matlab):
        if from_matlab and variable_revision_number==1:
            # Blue and red were switched: it was BGR
            temp = list(setting_values)
            temp[OFF_RED_IMAGE_NAME] = setting_values[OFF_BLUE_IMAGE_NAME]
            temp[OFF_BLUE_IMAGE_NAME] = setting_values[OFF_RED_IMAGE_NAME]
            temp[OFF_RED_ADJUSTMENT_FACTOR] = setting_values[OFF_BLUE_ADJUSTMENT_FACTOR]
            temp[OFF_BLUE_ADJUSTMENT_FACTOR] = setting_values[OFF_RED_ADJUSTMENT_FACTOR]
            setting_values = temp
            variable_revision_number = 2
        if from_matlab and variable_revision_number == 2:
            from_matlab = False
            variable_revision_number = 1
        if from_matlab and variable_revision_number == 3:
            image_names = [LEAVE_THIS_BLACK if value == cps.DO_NOT_USE 
                           else value
                           for value in setting_values[:4]]
            rgb_image_name = setting_values[4]
            adjustment_factors = setting_values[5:]
            if image_names[3] == LEAVE_THIS_BLACK:
                #
                # RGB color scheme
                #
                setting_values = (
                    [ SCHEME_RGB ] + image_names[:3] + [rgb_image_name] +
                    adjustment_factors[:3] + ["None"] * 4 + [1] * 4)
            else:
                #
                # CYMK color scheme
                #
                setting_values = (
                    [ SCHEME_CMYK ] + ["None"] * 3 + [rgb_image_name] + 
                    [1] * 3 + image_names + adjustment_factors)
            from_matlab = False
            variable_revision_number = 2
        if (not from_matlab) and variable_revision_number == 1:
            #
            # Was RGB-only. Convert values to CYMK-style
            #
            setting_values = (
                [ SCHEME_CMYK ] + setting_values + 
                ["None"] * 4 + [1] * 4)
            variable_revision_number = 2
        return setting_values, variable_revision_number, from_matlab

class ColorSchemeSettings(object):
    '''Collect all of the details for one color in one place'''
    def __init__(self, image_name_setting, adjustment_setting,
                 red_intensity, green_intensity, blue_intensity):
        '''Initialize with settings and multipliers
        
        image_name_setting - names the image to use for the color
        adjustment_setting - weights the image
        red_intensity - indicates how much it contributes to the red channel
        green_intensity - indicates how much it contributes to the green channel
        blue_intensity - indicates how much it contributes to the blue channel
        '''
        self.image_name = image_name_setting
        self.adjustment_factor = adjustment_setting
        self.red_intensity = red_intensity
        self.green_intensity = green_intensity
        self.blue_intensity = blue_intensity
        
    @property
    def intensities(self):
        '''The intensities in RGB order as a numpy array'''
        return np.array((self.red_intensity, 
                         self.green_intensity, 
                         self.blue_intensity))
