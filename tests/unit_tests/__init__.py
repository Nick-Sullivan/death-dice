import os
import sys

os.environ['IS_LOCAL'] = 'True'
sys.path.append('lambda/game/handler/')
sys.path.append('lambda/game/layer/python/')
