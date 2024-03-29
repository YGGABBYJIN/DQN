# 알파고를 만든 구글의 딥마인드의 논문을 참고한 DQN 모델을 생성합니다.
# http://www.nature.com/nature/journal/v518/n7540/full/nature14236.html
import tensorflow as tf
import numpy as np
import random
from collections import deque


class DQN:
    # 학습에 사용할 플레이결과를 얼마나 많이 저장해서 사용할지를 정합니다.
    # (플레이결과 = 게임판의 상태 + 취한 액션 + 리워드 + 종료여부)
    REPLAY_MEMORY = 10000

    # 학습시 사용/계산할 상태값(정확히는 replay memory)의 갯수를 정합니다.
    BATCH_SIZE = 32 # 한 번 학습할 때 몇 개의 기억을 사용할지

    # 과거의 상태(오래된 상태)에 대한 가중치를 줄이는 역할을 합니다.
    GAMMA = 0.99 # 벨만 방정식

    # 한 번에 볼 총 프레임 수 입니다.
    # 앞의 상태까지 고려하기 위함입니다.
    STATE_LEN = 4

    ### DQN 객체를 초기화 (세션, 가로/세로 크기, 행동의 개수)
    def __init__(self, session, width, height, n_action):
        self.session = session
        self.n_action = n_action
        self.width = width
        self.height = height
        # 게임 플레이결과를 저장할 메모리
        self.memory = deque() # 자료구조 과목에서 배움. 배열과 비슷하지만 선입선출을 쉽게 해주며 저장하는 개수를 쉽게 유지하게 해줌.
        # 현재 게임판의 상태
        self.state = None

        ### 게임의 상태를 입력받을 변수
        # [게임판의 가로 크기, 게임판의 세로 크기, 게임 상태의 갯수(현재+과거+과거..)]
        self.input_X = tf.placeholder(tf.float32, [None, width, height, self.STATE_LEN])
        # 원핫 인코딩이 아니라, 행동을 나타내는 숫자를 그대로 받아서 사용함

        # 각각의 상태를 만들어낸 액션의 값들입니다. 0, 1, 2 ..
        self.input_A = tf.placeholder(tf.int64, [None])

        # 손실값을 계산하는데 사용할 입력값입니다. train 함수를 참고하세요.
        self.input_Y = tf.placeholder(tf.float32, [None])

        """
        Q값은 행동에 따른 가치를 나타내는 값
        - 타깃 신경망에서 구한 Q값: 구한 값 중 최대의 값(최적 행동) 사용
        - 학습 신경망에서 구한 Q값: 현재 행동에 따른 값을 사용
        
        학습을 진행할 신경망과 타깃 신경망을 구성하는 데, 두 신경망은 구성이 같으므로 이름만 다르게 지음.
        타깃 신경망은 단순 Q값만을 사용하더라도 손실값과 최적화 함수를 사용하지 않음.  
        """
        self.Q = self._build_network('main')
        self.cost, self.train_op = self._build_op()

        ### 학습을 더 잘 되게 하기 위해,
        # 손실값 계산을 위해 사용하는 타겟(실측값)의 Q value를 계산하는 네트웍을 따로 만들어서 사용합니다
        self.target_Q = self._build_network('target') # 학습 시에만 보조적으로 사용되는 신경망

    """
    학습 신경망과 목표 신경망을 구성하는 함수
    - 상태값 input_X를 받아 행동의 가짓수만큼 출력값을 만들고, 이 값들의 최대값을 취해 다음 행동 결정
    - 간단한 CNN 구조이지만, pooling 계층이 없음(표현력을 높여 이미지의 세세한 부분까지 판단하기 위함)
    """
    def _build_network(self, name):
        with tf.variable_scope(name):
            model = tf.layers.conv2d(self.input_X, 32, [4, 4], padding='same', activation=tf.nn.relu)
            model = tf.layers.conv2d(model, 64, [2, 2], padding='same', activation=tf.nn.relu)
            model = tf.contrib.layers.flatten(model)
            model = tf.layers.dense(model, 512, activation=tf.nn.relu)

            Q = tf.layers.dense(model, self.n_action, activation=None)

        return Q

    """
    DQN의 손실함수를 구하는 함수
    - 현재 상태를 이용해 학습 신경망으로 구한 Q_Value와,
    다음 상태를 이용해 타깃 신경망으로 구한 Q_Value(Input_Y)를 이용해 손실값을 구하고 최적화 함 
    """
    def _build_op(self):
        # DQN 의 손실 함수를 구성하는 부분입니다. 다음 수식을 참고하세요.
        # Perform a gradient descent step on (y_j-Q(ð_j,a_j;θ))^2
        one_hot = tf.one_hot(self.input_A, self.n_action, 1.0, 0.0) # 현재 행동에 대한 값만 선택하기 위해 one-hot 이용
        Q_value = tf.reduce_sum(tf.multiply(self.Q, one_hot), axis=1)
        cost = tf.reduce_mean(tf.square(self.input_Y - Q_value))
        train_op = tf.train.AdamOptimizer(1e-6).minimize(cost)

        return cost, train_op

    """
    타깃 신경망을 갱신하는 함수
    - 학습 신경망의 변수들의 값을 타깃 신경망으로 복사해서 타깃 신경망의 함수들을 최신값으로 갱신
    """
    # refer: https://github.com/hunkim/ReinforcementZeroToAll/
    def update_target_network(self):
        copy_op = []

        main_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='main')
        target_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='target')

        # 학습 네트웍의 변수의 값들을 타겟 네트웍으로 복사해서 타겟 네트웍의 값들을 최신으로 업데이트합니다.
        for main_var, target_var in zip(main_vars, target_vars):
            copy_op.append(target_var.assign(main_var.value()))

        self.session.run(copy_op)

    """
    현재 상태를 이용해 다음에 취해야 할 행동을 찾는 함수
    - build_network 함수에서 사용한 Q_value 값을 이용
    """
    def get_action(self):
        Q_value = self.session.run(self.Q,
                                   feed_dict={self.input_X: [self.state]})

        action = np.argmax(Q_value[0])

        return action

    """
    현재 상태 초기와 함수 
    """
    def init_state(self, state):
        # 현재 게임판의 상태를 초기화합니다. 앞의 상태까지 고려한 스택으로 되어 있습니다.
        state = [state for _ in range(self.STATE_LEN)]
        # axis=2 는 input_X 의 값이 다음처럼 마지막 차원으로 쌓아올린 형태로 만들었기 때문입니다.
        # 이렇게 해야 컨볼루션 레이어를 손쉽게 이용할 수 있습니다.
        # self.input_X = tf.placeholder(tf.float32, [None, width, height, self.STATE_LEN])
        self.state = np.stack(state, axis=2)

    """
    게임 플레이 결과를 받아 메모리에 기억하는 기능을 수행하는 함수 
    """
    def remember(self, state, action, reward, terminal):
        # 학습데이터로 현재의 상태만이 아닌, 과거의 상태까지 고려하여 계산하도록 하였고,
        # 이 모델에서는 과거 3번 + 현재 = 총 4번의 상태를 계산하도록 하였으며,
        # 새로운 상태가 들어왔을 때, 가장 오래된 상태를 제거하고 새로운 상태를 넣습니다.
        next_state = np.reshape(state, (self.width, self.height, 1))
        next_state = np.append(self.state[:, :, 1:], next_state, axis=2)

        # 플레이결과, 즉, 액션으로 얻어진 상태와 보상등을 메모리에 저장합니다.
        self.memory.append((self.state, next_state, action, reward, terminal))

        # 저장할 플레이결과의 갯수를 제한합니다.
        if len(self.memory) > self.REPLAY_MEMORY:
            self.memory.popleft()

        self.state = next_state

    """
    기억해둔 게임 플레이에서 임의의 메모리를 배치 크기만큼 가져옴
    """
    def _sample_memory(self):
        sample_memory = random.sample(self.memory, self.BATCH_SIZE)

        state = [memory[0] for memory in sample_memory]
        next_state = [memory[1] for memory in sample_memory]
        action = [memory[2] for memory in sample_memory]
        reward = [memory[3] for memory in sample_memory]
        terminal = [memory[4] for memory in sample_memory]

        return state, next_state, action, reward, terminal

    """
    앞서 작성한 텐서들로 학습을 시키는 부분
    """
    def train(self):
        # 게임 플레이를 저장한 메모리에서 배치 사이즈만큼을 샘플링하여 가져옵니다.
        state, next_state, action, reward, terminal = self._sample_memory()

        # 학습시 다음 상태를 타겟 네트웍에 넣어 target Q value를 구합니다
        target_Q_value = self.session.run(self.target_Q,
                                          feed_dict={self.input_X: next_state})

        # DQN 의 손실 함수에 사용할 핵심적인 값을 계산하는 부분입니다. 다음 수식을 참고하세요.
        # if episode is terminates at step j+1 then r_j
        # otherwise r_j + γ*max_a'Q(ð_(j+1),a';θ')
        # input_Y 에 들어갈 값들을 계산해서 넣습니다.
        Y = []
        for i in range(self.BATCH_SIZE):
            if terminal[i]:
                Y.append(reward[i])
            else:
                Y.append(reward[i] + self.GAMMA * np.max(target_Q_value[i]))

        self.session.run(self.train_op,
                         feed_dict={
                             self.input_X: state,
                             self.input_A: action,
                             self.input_Y: Y
                         })