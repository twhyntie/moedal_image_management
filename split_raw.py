#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 CERN@school and MoEDAL - Splitting scan images.

 See the README.md file and the GitHub wiki for more information.

 http://moedal.web.cern.ch

"""

# Import the code needed to manage files.
import os, glob

#...for parsing the arguments.
import argparse

#...for the logging.
import logging as lg

#...for file manipulation.
from shutil import rmtree

#...for the plotting.
import matplotlib.pyplot as plt

#...for the image conversions.
import Image

#...for the image manipulation.
import matplotlib.image as mpimg

#...for the MATH.
import numpy as np

#...for the image scaling.
import scipy.ndimage.interpolation as inter

if __name__ == "__main__":

    print("*")
    print("*===============================================*")
    print("* CERN@school and MoEDAL: Splitting scan images *")
    print("*===============================================*")

    # Get the datafile path from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("dataPath",         help="Path to the data to catalogue.")
    parser.add_argument("--subject-width",  help="The desired subject image width [pixels].",  default=128, type=int)
    parser.add_argument("--subject-height", help="The desired subject image height [pixels].", default=128, type=int)
    parser.add_argument("-v", "--verbose",  help="Increase output verbosity", action="store_true")
    args = parser.parse_args()

    ## The path to the data.
    data_path = args.dataPath
    #data_path = os.path.join(args.dataPath, "RAW/data")
    #
    if not os.path.isdir(data_path):
        raise IOError("* ERROR: Unable to find data at '%s'." % (data_path))

    ## The output path.
    output_path = "./"
    #output_path = os.path.join(args.dataPath, "SPL/data")
    #
    # Check if the output directory exists. If it doesn't, raise an error.
    if not os.path.isdir(output_path):
        raise IOError("* ERROR: '%s' output directory does not exist!" % (output_path))

    ## The required width of the subject images [pixels].
    SubjectWidth = args.subject_width

    ## The required height of the split images [pixels].
    SubjectHeight = args.subject_height

    # Set the logging level.
    if args.verbose:
        level=lg.DEBUG
    else:
        level=lg.INFO

    # Configure the logging.
    lg.basicConfig(filename='split_raw.log', filemode='w', level=level)

    print("*")
    print("* Data path         : '%s'" % (data_path))
    print("* Writing to        : '%s'" % (output_path))
    print("*")

    lg.info(" *===============================================*")
    lg.info(" * CERN@school and MoEDAL: Splitting scan images *")
    lg.info(" *===============================================*")
    lg.info(" *")
    lg.info(" * Data path         : '%s'" % (data_path))
    lg.info(" * Writing to        : '%s'" % (output_path))


    lg.info(" *")
    lg.info(" * Required subject size : %d x %d" % (SubjectWidth, SubjectHeight))
    lg.info(" *")

    ## A list of te data entities found in RAW/data.
    entity_list = glob.glob(os.path.join(data_path, "MoEDAL*.png"))

    # Loop through the scan PNG files found.
    for f in sorted(entity_list):

        ## The base name.
        bn = os.path.basename(f)

        ## The image ID.
        image_id = bn[:-4]

        lg.info(" * Current image                    : %s" % (bn))
        lg.info(" * Current image ID                 : %s" % (image_id))

        ## The image as a NumPy array.
        img = mpimg.imread(f)

        u_min = 0

        ## The original image width [pixels].
        OriginalImageWidth = img.shape[1]

        v_min = 0

        ## The original image height [pixels].
        OriginalImageHeight = img.shape[0]


        ## The left vertical gutter width, delta u_l [pixels].
        LeftVerticalGutterWidth =  int(0.5 * (SubjectWidth - (OriginalImageWidth % SubjectWidth)))
        #
        ## The right vertical gutter width, delta u_r [pixels].
        RightVerticalGutterWidth =  LeftVerticalGutterWidth
        #
        if ((OriginalImageHeight % SubjectHeight)%2) != 0: # Unless they're odd...
            LeftVerticalGutterWidth  = int(0.5 * ((SubjectWidth - (OriginalImageWidth % SubjectWidth)) - 1))
            RightVerticalGutterWidth = int(0.5 * ((SubjectWidth - (OriginalImageWidth % SubjectWidth)) + 1))

        ## The top horizontal gutter width, delta v_t [pixels].
        TopHorizontalGutterWidth = int(0.5 * (SubjectHeight - (OriginalImageHeight % SubjectHeight)))
        #
        ## The bottom horizontal gutter width, delta v_b [pixels].
        BottomHorizontalGutterWidth = TopHorizontalGutterWidth
        #
        if ((OriginalImageHeight % SubjectHeight) % 2) != 0: # Unless they're odd...
            TopHorizontalGutterWidth    = int(0.5 * ((SubjectHeight - (OriginalImageHeight % SubjectHeight)) - 1))
            BottomHorizontalGutterWidth = int(0.5 * ((SubjectHeight - (OriginalImageHeight % SubjectHeight)) + 1))

        ## The width of the image with gutters and padding [pixels].
        ImageToSplitWidth = int(OriginalImageWidth + LeftVerticalGutterWidth + RightVerticalGutterWidth + (2*SubjectWidth))

        ## The height of the image with gutters and padding [pixels].
        ImageToSplitHeight = int(OriginalImageHeight + TopHorizontalGutterWidth + BottomHorizontalGutterWidth + (2*SubjectHeight))

        ## The number of columns in the original image, including the gutters.
        NumberOfColumnsInTheOriginalImage = int((OriginalImageWidth + LeftVerticalGutterWidth + RightVerticalGutterWidth) / SubjectWidth)

        ## The number of rows in the original image, including the gutters.
        NumberOfRowsInTheOriginalImage = int((OriginalImageHeight + TopHorizontalGutterWidth + BottomHorizontalGutterWidth) / SubjectHeight)

        lg.info(" *")
        lg.info(" * Original image dimensions (img.shape)             : %s" % (str(img.shape)))
        lg.info(" * Original image dimensions (Delta U x Delta V)     : (%d x %d) [pixels x pixels]" % (OriginalImageWidth, OriginalImageHeight))
        lg.info(" *")
        lg.info(" * Left  vertical   gutter width (\delta u_l)        : %d [pixels]" % (LeftVerticalGutterWidth))
        lg.info(" * Right vertical   gutter width (\delta u_r)        : %d [pixels]" % (RightVerticalGutterWidth))
        lg.info(" * Left horizontal  gutter width (\delta v_l)        : %d [pixels]" % (TopHorizontalGutterWidth))
        lg.info(" * Right horizontal gutter width (\delta v_r)        : %d [pixels]" % (BottomHorizontalGutterWidth))
	lg.info(" *")
        lg.info(" * Image to split dimensions (Delta U_0 x Delta V_0) : (%d x %d) [pixels x pixels]" % (ImageToSplitWidth, ImageToSplitHeight))
        lg.info(" *")
        lg.info(" * Number of rows    in the original image           : % 6d" % (NumberOfRowsInTheOriginalImage))
        lg.info(" * Number of columns in the original image           : % 6d" % (NumberOfColumnsInTheOriginalImage))

        ## The (greyscale) colour for the image gutter.
        GutterGrey = 256 - 64

        ## NumPy array representing the left-hand gutter.
        LeftGutter = int(GutterGrey) * np.ones((OriginalImageHeight, LeftVerticalGutterWidth, 3), dtype=np.uint8)
        #
        # Add the left-hand gutter.
        ImageToBeSplit = np.concatenate((LeftGutter, img), axis=1)

        ## NumPy array representing the right-hand gutter.
        RightGutter = int(GutterGrey) * np.ones((OriginalImageHeight, LeftVerticalGutterWidth, 3), dtype=np.uint8)
        #
        # Add the right-hand gutter.
        ImageToBeSplit = np.concatenate((ImageToBeSplit, RightGutter), axis=1)

        ## The original image width plus the width of the gutters.
        OriginalImageWithGutterWidth = OriginalImageWidth + LeftVerticalGutterWidth + RightVerticalGutterWidth

        ## NumPy array representing the top gutter.
        TopGutter = int(GutterGrey) * np.ones((TopHorizontalGutterWidth, OriginalImageWithGutterWidth, 3), dtype=np.uint8)
        #
        # Add the top gutter.
        ImageToBeSplit = np.concatenate((TopGutter, ImageToBeSplit), axis=0)

        ## NumPy array representing the bottom gutter.
        BottomGutter = int(GutterGrey) * np.ones((BottomHorizontalGutterWidth, OriginalImageWithGutterWidth, 3), dtype=np.uint8)
        #
        # Add the bottom gutter.
        ImageToBeSplit = np.concatenate((ImageToBeSplit, TopGutter), axis=0)

        ## The (greyscale) colour of the padding.
        PaddingGrey = 256 - 0

        ## Height of the original image plus the gutters.
        OriginalImageWithGutterHeight = OriginalImageHeight + TopHorizontalGutterWidth + BottomHorizontalGutterWidth

        ## NumPy array representing the vertical padding blocks.
        VerticalPadding = int(PaddingGrey) * np.ones((OriginalImageWithGutterHeight, SubjectWidth, 3), dtype=np.uint8)
        #
        # Add the vertical padding.
        ImageToBeSplit = np.concatenate((VerticalPadding, ImageToBeSplit), axis=1)
        ImageToBeSplit = np.concatenate((ImageToBeSplit, VerticalPadding), axis=1)

        ## The width of the image to be split, i.e. with gutter and padding [pixels].
        ImageToSplitWidthFull = OriginalImageWithGutterWidth + (2 * SubjectWidth)

        ## The height of the image to be split, i.e. with gutter and padding [pixels].
        ImageToSplitHeightFull = OriginalImageWithGutterHeight + (2 * SubjectHeight)

        ## NumPy array representing the horizontal padding blocks.
        HorizontalPadding = int(PaddingGrey) * np.ones((SubjectHeight, ImageToSplitWidthFull, 3), dtype=np.uint8)
        #
        # Add the vertical padding.
        ImageToBeSplit = np.concatenate((HorizontalPadding, ImageToBeSplit), axis=0)
        ImageToBeSplit = np.concatenate((ImageToBeSplit, HorizontalPadding), axis=0)

        # Save the image to be split.
        #mpimg.imsave(os.path.join(output_path, "imtosplit.png"), ImageToBeSplit)

        #
        # THE NON-OFFSET IMAGES
        #

        ## The row limits.
        RowLimits = range(SubjectHeight, ImageToSplitHeightFull, SubjectHeight)

        ## The number of rows in the image.
        NumberOfRowsInTheImageToSplit = NumberOfRowsInTheOriginalImage + 2
        #
        lg.info(" * % 3d rows    - limits: %s" % (NumberOfRowsInTheImageToSplit, str(RowLimits)))
        lg.info(" * Number of rows in the image to split              : % 6d" % (NumberOfRowsInTheImageToSplit))
        if NumberOfRowsInTheImageToSplit != (len(RowLimits) + 1):
            raise IOError("* ERROR: Image rows mismatch!")

        ## The column limits.
        ColumnLimits = range(SubjectWidth, ImageToSplitWidthFull, SubjectWidth)

        ## The number of rows in the image.
        NumberOfColumnsInTheImageToSplit = NumberOfColumnsInTheOriginalImage + 2
        #
        lg.info(" * Number of columns in the image to split           : % 6d" % (NumberOfColumnsInTheImageToSplit))
        if NumberOfColumnsInTheImageToSplit != len(ColumnLimits) + 1:
            raise IOError("* ERROR: Image columns mismatch!")

        # Split the montage into rows.
        RowImages = np.split(ImageToBeSplit, RowLimits)

        lg.info(" *-->")

        # Loop over the rows.
        for j, row_im in enumerate(RowImages):

            lg.info(" *--> Row dimensions: %s" % (str(row_im.shape)))
            lg.info(" *-->")

            # Save the row images.
            #mpimg.imsave(os.path.join(output_path, "%s_%02d.png" % (image_id, j)), row_im)

            # Split the row into the images.
            imgs = np.split(row_im, ColumnLimits, axis=1)

            # Loop over the images.
            for i, img in enumerate(imgs):

                lg.info(" *-----> Split image dimensions: %s" % (str(img.shape)))

                # Save the images.
                if i!=0 and i!=NumberOfColumnsInTheImageToSplit-1 and j!= 0 and j!= NumberOfRowsInTheImageToSplit-1:
                    mpimg.imsave(os.path.join(output_path, "%s_A_%02d_%02d.png" % (image_id, i, j)), img)

            lg.info(" *-->")

        #
        # THE OFFSET IMAGES.
        #

        ## The offset row limits.
        OffsetRowLimits = range(SubjectHeight/2, ImageToSplitHeightFull, SubjectHeight)

        ## The number of "offset" rows in the image.
        NumberOfOffsetRowsInTheImageToSplit = NumberOfRowsInTheOriginalImage + 1
        #
        lg.info(" * % 3d offset rows    - limits: %s" % (NumberOfOffsetRowsInTheImageToSplit, str(OffsetRowLimits)))
        lg.info(" * Number of offset rows in the image to split       : % 6d" % (NumberOfOffsetRowsInTheImageToSplit))
        if NumberOfOffsetRowsInTheImageToSplit != (len(OffsetRowLimits) - 1):
            raise IOError("* ERROR: Image offset rows mismatch!")

        ## The column limits.
        OffsetColumnLimits = range(SubjectWidth/2, ImageToSplitWidthFull, SubjectWidth)

        ## The number of "offset" columns in the image.
        NumberOfOffsetColumnsInTheImageToSplit = NumberOfColumnsInTheOriginalImage + 1
        #
        lg.info(" * % 3d offset columns - limits: %s" % (NumberOfOffsetColumnsInTheImageToSplit, str(OffsetColumnLimits)))
        lg.info(" * Number of offset columns in the image to split    : % 6d" % (NumberOfOffsetColumnsInTheImageToSplit))
        if NumberOfOffsetColumnsInTheImageToSplit != len(OffsetColumnLimits) - 1:
            raise IOError("* ERROR: Image offset columns mismatch!")

        # Split the montage into the offset rows.
        OffsetRowImages = np.split(ImageToBeSplit, OffsetRowLimits)

        lg.info(" *-->")

        # Loop over the rows.
        for j, offset_row_im in enumerate(OffsetRowImages):

            lg.info(" *--> Row dimensions: %s" % (str(offset_row_im.shape)))
            lg.info(" *-->")

            ## Save the row images.
            #if j!= 0 and j <= NumberOfOffsetRowsInTheImageToSplit:
            #    mpimg.imsave(os.path.join(output_path, "%s_1_%02d.png" % (image_id, j)), offset_row_im)

            # Split the row into the images.
            imgs = np.split(offset_row_im, OffsetColumnLimits, axis=1)

            # Loop over the images.
            for i, img in enumerate(imgs):

                lg.info(" *-----> Split image dimensions: %s" % (str(img.shape)))

                # Save the offset images.
                if i>0 and i<=NumberOfOffsetRowsInTheImageToSplit and j>0 and j<=NumberOfOffsetRowsInTheImageToSplit:
                    mpimg.imsave(os.path.join(output_path, "%s_B_%02d_%02d.png" % (image_id, i, j)), img)

            lg.info(" *-->")
