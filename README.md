# scancrop

Locate the actual photo position from the given scanned image and crop it. Can support multiple photos in a picture with gaps between them and the script will automatically find the possible multiple photos.

The scanned image should be with a bright background and the angle of the photo inside should be as straight as possible. If there are multiple photos, there should be a gap between the photos and the photos should not differ too much in size.

## Detect the photos

The script will automatically find possible photo areas in the image, merge overlapping parts, and discard areas that are too small.

![merge roi](./doc/images/merge.gif)

## Usage

`python scancrop.py` runs the script in working directory and puts the results in `./output` directory. Run `python scancrop.py --help` for detail customization.
