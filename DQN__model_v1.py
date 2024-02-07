import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
import numpy as np
import random
from collections import deque

from DQN__env_v4 import GridManager

class DQN:
    REPLAY_MEMORY = 100000
    BATCH_SIZE = 64
    GAMMA = 0.99
    STATE_VIEW = 4

    def __init__(self):
        self.width = 5
        self.height = 5 # 그리드의 크기
        self.num_action = 4 # 행동: 상, 하, 좌, 우
        self.replay_memory = deque(maxlen=DQN.REPLAY_MEMORY) # 리플레이 메모리 # 메모리의 크기를 정하고 싶다면 deque(maxlen=10000)
        self.state = None # 현재 그리드의 상태

        self.grid_manager = GridManager(size=5)

        # 모델 생성
        self.q_network = self.create_model()
        self.target_network = self.create_model()

    def create_model(self):
        model = Sequential()
        model.add(Flatten(input_shape=(self.width, self.height, DQN.STATE_VIEW))) # 그리드의 각 셀을 입력값으로 받음
        model.add(Dense(128, activation='relu'))
        model.add(Dense(self.num_action, activation='linear')) # 행동의 수만큼 출력으로 받음 # Q 값을 예측하기 위해 linear 출력 사용
        model.compile(optimizer='adam', loss = 'mse')
        return model

    def update_target_network(self):
        self.target_network.set_weights(self.q_network.get_weights()) # 타겟 네트워크를 q 네트워크의 가중치로 업데이트

    def remember(self, state, action, reward, next_state, done): # 각 스텝에서의 경험을 리플레이 메모리에 저장(상태, 행동, 보상, 다음 상태, 종료 여부)
        self.replay_memory.append((state, action, reward, next_state, done))

    def act(self, state, epsilon): # 현재 상태에 대한 행동을 결정
        if np.random.rand() <= epsilon:  # epsilon gradient 사용
            return random.randrange(self.num_action)
        q_values = self.q_network.predict(state)
        return np.argmax(q_values[0])

    def replay(self): # 리플레이 메모리에서 무작위로 배치를 추출하여 학습
        if len(self.replay_memory) < DQN.BATCH_SIZE:
            return
        minibatch = random.sample(self.replay_memory, DQN.BATCH_SIZE)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + DQN.GAMMA * np.amax(self.target_network.predict(next_state)[0])) # 타겟 q값 계산하기
            target_f = self.q_network.predict(state)
            target_f[0][action] = target
            self.q_network.fit(state, target_f, epochs=1, verbose=0)

    def train(self, num_episodes, epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.995):
        epsilon = epsilon_start
        for e in range(num_episodes):
            self.grid_manager.reset()  # 상태 초기화
            initial_state = self.grid_manager.get_state()  # 초기 상태 로드
            state = np.expand_dims(initial_state, axis=0)  # 모델 입력 형태에 맞게 차원 확장
            done = False
            total_reward = 0  # 에피소드별 총 보상

            while not done:
                action = self.act(state, epsilon)  # 현재 상태에 대한 행동 결정
                # 환경으로부터 다음 상태, 보상 받기
                self.grid_manager.move_agent(action)  # 에이전트 이동
                next_state = self.grid_manager.get_state()  # 다음 상태
                reward = self.grid_manager.current_reward  # 받은 보상
                done = self.grid_manager.the_end()  # 에피소드 종료 여부

                next_state = np.expand_dims(next_state, axis=0)  # 다음 상태 형태 조정
                total_reward += reward

                self.remember(state, action, reward, next_state, done)  # 메모리에 경험 저장
                state = next_state  # 상태 업데이트

                if done:
                    self.update_target_network()  # 타겟 네트워크 업데이트
                    print(f"에피소드: {e + 1}/{num_episodes}, 점수: {total_reward}")

            self.replay()  # 경험 재생을 통한 학습
            epsilon = max(epsilon_end, epsilon_decay * epsilon)  # 엡실론 값 감소
