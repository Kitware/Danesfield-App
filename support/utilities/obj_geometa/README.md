# OBJ Geospatial Metadata

Set geospatial metadata on a Girder item for an OBJ file.

## Requirements

- Python 3
- Python packages in `requirements.txt`

## Usage

- Set `GIRDER_API_KEY` environment variable to authenticate with a Girder
  instance using an [API key](https://girder.readthedocs.io/en/latest/user-guide.html#api-keys).
- Determine the file IDs of the following files in the Girder instance:
    - The OBJ file on which to set the geospatial metadata.
    - A text file that specifies a global offset for the OBJ geometry.
        - The file should contain 3 floating point values on separate lines to
        represent x, y, and z.
  - A GeoTIFF image in the same AOI as the OBJ file. The source coordinate
    reference system is extracted from this file.
- Run the script as demonstrated in the example below.

## Example

```bash
export GIRDER_API_KEY=<key>
python ./obj_geometa.py \
    --api-url http://core3d.kitware.com:8080/api/v1 \
    --offset-file-id 5b6c9cd9076129311e07751c \
    --obj-file-id 5b6c9cd9076129311e077519 \
    --tiff-file-id=5b719f560761292c7f27ab32 
```
