import argparse
from aigeanpy.satmap import get_satmap


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='+',
                        help='All information about the file in meta data')
    args = parser.parse_args()
    errorlist = []
    if len(args.filename) == 1:
        try:
            filename = args.filename[0]
            map = get_satmap(filename)
            for key in map.meta:
                print(str(key)+': '+str(map.meta[key]))
        except:
            errorlist.append(filename)

    elif len(args.filename) > 1:
        for filename in args.filename:
            try:
                map = get_satmap(filename)
                for key in map.meta:
                    print(str(filename)+':'+str(key)+': '+str(map.meta[key]))
            except:
                errorlist.append(filename)

    if len(errorlist) == 0:
        pass
    else:
        print('These files failed while being processed')
        for file in errorlist:
            print('- '+f'{file}')


if __name__ == "__main__":
    main()
