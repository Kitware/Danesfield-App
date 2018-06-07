#!/bin/bash
set -eo pipefail

# Wrapper script for p3d Docker image to support running from Girder Worker.
#
# This script accepts the same arguments as the p3d Docker container, with one
# exception.  Instead of specifying the image input directory with --in, specify
# --images followed by the image filenames. This script consolidates those files
# into a single directory and updates the arguments to pass --in with that
# directory.
#
# This script also intercepts the --out argument and creates the specified
# directory.  This works around an issue where directly using the p3d Docker
# image from Girder Worker fails because the specified output directory doesn't
# exist in the container. If the p3d Docker image is updated to create the
# output directory, then this step can be removed.
#
# Following the input steps, this script runs the updated command, presumably to
# run p3d to generate point cloud files.
#
# On the output side, this script ensures that the point cloud files are located
# in the root output directory. This ensures that they will be uploaded to
# Girder by GirderUploadVolumePathToFolder. By default, the p3d Docker image
# places the point cloud files in a tp_manual_<timestamp> subdirectory of the
# root output directory.


#
# Parse command line arguments
#

# Arguments to pass to p3d container
ARGS=()

# Input image filenames
IMAGES=()

# Flag set when parsing input image filenames
PARSING_IMAGES=false

while [[ $# -gt 0 ]]
do
key="$1"
    case "$key" in
        --images) # Input images argument
        PARSING_IMAGES=true
        # Shift argument
        shift
        ;;

        --*) # Other option argument
        PARSING_IMAGES=false
        case "$key" in
            --out)
            # Store output directory
            OUT="$2"
            # Add args to array
            ARGS+=("$1")
            ARGS+=("$2")
            # Shift arguments
            shift
            shift
            ;;

            *)
            # Add arg to array
            ARGS+=("$1")
            # Shift argument
            shift
            ;;
        esac
        ;;

        *) # Other argument
        if [ "$PARSING_IMAGES" = true ]
        then
            # Add arg to image array
            IMAGES+=("$1")
        else
            # Add arg to array
            ARGS+=("$1")
        fi
        # Shift argument
        shift
        ;;
    esac
done

# Consolidate images into a single directory
IMAGE_DIR=./P3D/Images
for i in "${IMAGES[@]}"
do
    FILENAME=$(basename "${i}")
    ln -s "${i}" "${IMAGE_DIR}/${FILENAME}"
done

# Create output directory
mkdir -p "${OUT}"

# Set updated command line
set -- "${ARGS[@]}" "--in" "${IMAGE_DIR}"

# Run command
"$@"

# Girder Worker's GirderUploadVolumePathToFolder uploads the files
# in the specified output directory to an item, nonrecursively.
# Move the primary point cloud output file to the output directory
# and delete the rest.

# Delete irrelevant output files in root output directory
find "${OUT}" -maxdepth 1 -type f -delete

# Move primary point cloud file to root output directory
mv --target-directory "${OUT}" "${OUT}"/tp_manual_*/tp_manual_*_flt.las

# Remove subdirectories for clarity, even though they won't be uploaded
find "${OUT}" -mindepth 1 -type d -print0 | xargs -0 rm -rf
