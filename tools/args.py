import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Simple NAS/GW managing script')
    parser.add_argument('-c', '--command')
    parser.add_argument('-cf', '--commands-file')
    parser.add_argument('-H', '--host')
    parser.add_argument('-hf', '--hosts-file')
    args = parser.parse_args()
    return args
