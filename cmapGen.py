#!/usr/bin/python3
#
# This script is designed to create a colormap compliant
# with the popular ncview tool. The only parameter needed
# is an ordered list of named colours
#


################################################
#
# requirements
#
################################################

import pdb
import sys
import getopt
import argparse
import traceback
import numpy as np
from termcolor import colored
import matplotlib.colors as mcolors


################################################
#
# adjust_to_sum
#
################################################

def adjust_to_sum(values):
    # Step 1: Round values to the nearest integer
    rounded_values = [int(round(v)) for v in values]
    
    # Step 2: Calculate the difference between the rounded sum and the target
    difference = 256 - sum(rounded_values)
    
    # Step 3: Adjust values based on the differences
    # Create a list of (index, fractional_part) and sort by the largest fractional parts
    adjustments = sorted(
        enumerate(values),
        key=lambda x: x[1] - round(x[1]),
        reverse=(difference > 0)
    )

    # Distribute the difference among the values
    for i in range(abs(difference)):
        index, _ = adjustments[i]
        # If difference is positive, increment; if negative, decrement
        rounded_values[index] += 1 if difference > 0 else -1
    
    return rounded_values


################################################
#
# get_rgb_value_255
#
################################################

def get_rgb_value_255(color_name):

    try:
        
        # Convert the color name to an RGB tuple in the 0-1 range
        rgb = mcolors.to_rgb(color_name)
        
        # Scale the RGB values to the 0-255 range
        rgb_255 = tuple(int(255 * val) for val in rgb)

        # return
        return rgb_255
    
    except ValueError:
        return "Invalid color name"

    
################################################
#
# generate_color_gradient
#
################################################

def generate_color_gradient(color1, color2, interval_size):
    """
    Generates a smooth transition between two RGB colors.
    
    Parameters:
    - color1: Tuple of RGB values for the first color (e.g., (1.0, 0.0, 0.0) for red).
    - color2: Tuple of RGB values for the second color (e.g., (0.0, 0.0, 1.0) for blue).
    - n: Number of steps in the gradient.
    
    Returns:
    - List of RGB tuples representing the gradient.
    """

    # Convert the color values to the 0-1 range for interpolation
    # Interpolate each of the RGB channels separately
    gradient = [
        (
            int(np.linspace(color1[0], color2[0], interval_size)[i]),
            int(np.linspace(color1[1], color2[1], interval_size)[i]),
            int(np.linspace(color1[2], color2[2], interval_size)[i])
        )
        for i in range(interval_size)
    ]
    
    return gradient


################################################
#
# MAIN
#
################################################

if __name__ == "__main__":     

    ################################################
    #
    # read command line parameters
    #
    ################################################

    try:
        # Define the short and long options
        opts, args = getopt.getopt(sys.argv[1:], "hc:p:o:", ["help", "colours=", "percentages=", "outputfile="])
    except getopt.GetoptError:
        print("Usage: cmapGen.py --colours <value>")
        print("where the value is a comma-separated list of named colours.")
        print()
        print("Allowed colours are:")
        print(list(mcolors.CSS4_COLORS.keys()))
        sys.exit(2)

    # initialise two empty lists for colour intervals (one for human-readable labels, the other for 255rgb values)
    # and two empty lists to deal with the size of these intervals
    intervals = [] 
    intervals_255 = []
    percentages = []
    range_sizes = []

    # initialize the output file name
    outputFile = None

    # process the options
    for opt, arg in opts:
        
        if opt in ("-h", "--help"):
            print("Usage: script.py --colours <value> or -c <value>")
            sys.exit()
            
        elif opt in ("-c", "--colours"):
            interval = arg.split(",")
            interval_255 = []
            for colour in interval:
                interval_255.append(get_rgb_value_255(colour))

            # append the new interval to the lists
            intervals.append(interval)
            intervals_255.append(interval_255)

        elif opt in ("-p", "--percentages"):
            percentages = [int(x) for x in arg.split(",")]
            print(percentages)
            
        elif opt in ("-o", "--outputfile"):
            outputFile = arg
            
    ################################################
    #
    # check input parameters
    #
    ################################################

    # check if an output filename was provided:
    if not outputFile:
        print(colored("ERROR", "red", attrs=["bold",]) + " -- An output filename must be provided with --outputfile=<FILE> !")
        sys.exit(1)        
    
    # check if at least an interval was provided
    if len(intervals) == 0:
        print(colored("ERROR", "red", attrs=["bold",]) + " -- At least a color interval must be provided!")
        sys.exit(1)

    # check if percentages were provided
    if len(percentages) == 0:
        
        if len(intervals) > 1:
            print(colored("INFO", "yellow", attrs=["bold",]) + " -- Colour ranges will have the same size")
            range_sizes = 256 / len(intervals)
            range_sizes = adjust_to_sum(range_sizes)
        else:
            range_sizes = [256]
            
    else:
        if np.sum(percentages) != 100:        
            print(colored("ERROR", "red", attrs=["bold",]) + " -- Sum of percentages must be 100!")
            sys.exit(1)
        else:

            # get the number of items for each color interval
            for p in percentages:
                range_sizes.append(256 * p / 100)
                
            # fix the ranges so that they are formed by integer numbers
            range_sizes = adjust_to_sum(range_sizes)
            
    # print the list of the requested intervals
    print("INFO -- Will generate colormap interpolating the following intervals:")
    for i in range(len(intervals_255)):
        print(f" * {intervals[i]}")


    ################################################
    #
    # generate the colormap
    #
    ################################################

    # generate list of colours
    colormap = []
    for  i in range(len(intervals_255)):
        interval = intervals_255[i]
        interval_size = range_sizes[i]
        colormap.extend(generate_color_gradient(interval[0], interval[1], interval_size))

    # write to output file
    with open(outputFile, "w") as f:
        for c in colormap:
            f.write(f"{c[0]} {c[1]} {c[2]}\n")
        
