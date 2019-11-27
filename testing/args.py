import argparse

# ---------- Add command line arguments ----------
parser = argparse.ArgumentParser(
                                 description = 'Dook Robotics - Object Detection Master Script',
                                 epilog = "Dook Robotics - https://github.com/dook-robotics"
                                )

parser.add_argument(
                               '--debug',
                     dest    = 'debugCLA',
                     action  = 'store_true',
                     default = False,
                     help    = 'Prints out all debug messages.'
                    )

parser.add_argument(
                               '--hardwareOff',
                     dest    = 'hardwareCLA',
                     action  = 'store_true',
                     default = False,
                     help    = 'Allows hardware to be called.'
                    )

parser.add_argument(
                               '--battery',
                     dest    = 'batteryNumCLA',
                     required = True,
                     help    = 'Battery number.'
                    )

args = parser.parse_args()


print("\n ===================================")
print(" ========== Dook Robotics ==========")
print(" ==========  Version 1.0  ==========")
print(" ===================================\n")

print(args.batteryNumCLA)
