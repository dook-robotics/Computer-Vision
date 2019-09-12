import argparse

# Add command line arguments
parser = argparse.ArgumentParser(
                                 description = 'Dook Robotics - Object Detection Master Script',
                                 epilog = "Dook Robotics - https://github.com/dook-robotics"
                                )

parser.add_argument(
                               '--debug',
                     dest    = 'debugCLA',
                     action  = 'store_true',
                     default = 'False',
                     help    = 'Prints out all debug messages.'
                    )

parser.add_argument(
                               '--hardware',
                     choices = ['True', 'False'],
                     dest    = 'hardwareCLA',
                     default = 'False',
                     help    = 'Allows hardware to be called.'
                    )

args = parser.parse_args()
print(args.debugCLA)
print(args.hardwareCLA)
