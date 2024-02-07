import tensorflow as tf
import numpy as np
import random
import time

from DQN__env_v4 import GridManager

### 하이퍼 파라미터 설정
# 최대 학습 횟수 10000번
MAX_EPISODE = 10000
# 1000번의 학습마다 한 번씩 타겟신경망 업데이트
TARGET_UPDATE_INTERVAL = 1000
# 4개 state마다 한 번씩 학습
TRAIN_INTERVAL = 4
# 데이터를 몇 번 쌓은 후 학습을 시작할지
OBSERVE = 100
# 행동
NUM_ACTION=4 #상, 하, 좌, 우


