import argparse

parser = argparse.ArgumentParser(
                                 description='Dook Robotics - Object Detection Master Script',
                                 epilog="Dook Robotics - https://github.com/dook-robotics"
                                )

parser.add_argument(
                    '--debug',
                    dest='debugCLA',
                    action='store_true',
                    help='Prints out all debug messages'
                    )

args = parser.parse_args()
print(args.debugCLA)
