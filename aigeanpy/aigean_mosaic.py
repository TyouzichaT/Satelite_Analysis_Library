import argparse
from aigeanpy.satmap import get_satmap
from aigeanpy.utilis import print_err


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resolution',
                        help='Resolution of the instrument')
    parser.add_argument('filename', nargs='+', help='Name of the files')
    args = parser.parse_args()
    if len(args.filename) < 2:
        print_err("You should provide at least 2 filenames")

    cnt = 0
    for filename in args.filename:
        if cnt == 0:
            try:
                map = get_satmap(filename)
            except:
                print_err("File fails")
        else:
            try:
                medium = get_satmap(filename)
            except:
                print_err("File fails")

            map = map.mosaic(medium, resolution=args.resolution)
        cnt += 1
    figname = map.visualise(save=True)
    print(figname)


if __name__ == "__main__":
    main()
