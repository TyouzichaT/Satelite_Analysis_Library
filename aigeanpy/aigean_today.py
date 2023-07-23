import argparse
from datetime import date
from aigeanpy.net import download_isa, query_isa
from aigeanpy.satmap import get_satmap
from aigeanpy.utilis import print_err
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--instrument', help='Select a specific instrument to get data (lir, manannan, fand, or ecne)')
    parser.add_argument('-s', '--saveplot', default=False,
                        help='Save the plot if the file downloaded is from one of the three imagers')
    args = parser.parse_args()

    if args.instrument is not None:
        if args.instrument.casefold() == 'lir'.casefold():
            instrument = 'Lir'
        elif args.instrument.casefold() == 'manannan'.casefold():
            instrument = 'Manannan'
        elif args.instrument.casefold() == 'fand'.casefold():
            instrument = 'Fand'
        elif args.instrument.casefold() == 'ecne'.casefold():
            instrument = 'Ecne'
        else:
            print_err("Invalid input of instrument")
    else:
        instrument = None

    saveplot = args.saveplot
    if not isinstance(saveplot, bool):
        print_err("Invalid input of saveplot, should be bool value (True or False)")

    today = str(date.today())
    file_list = query_isa(today, today, instrument)
    sorted_list = sorted(file_list, key=lambda x: x.__getitem__('time'))
    file_meta = sorted_list[-1]
    file_name = file_meta['filename']
    download_isa(filename=file_name, save_dir=os.getcwd())

    if saveplot is True:
        if file_meta['instrument'] == 'ecne':
            print_err("The file type (csv) does not support visualisation")
        else:
            map = get_satmap(file_name)
            map.visualise(save=saveplot, savepath=os.getcwd())


if __name__ == "__main__":
    main()
