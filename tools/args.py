import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Simple NAS/GW managing script')
    parser.add_argument('-e', '--execute-command')
    parser.add_argument('-c', '--config-file')
    parser.add_argument('-i', '--inventory-file')
    parser.add_argument('-H', '--host')
    parser.add_argument('-C', '--commands-file')
    args = parser.parse_args()
    return args
