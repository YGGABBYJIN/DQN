class GridManager:
    def __init__(self, size=5):
        self.size = size
        self.grid = [['-' for _ in range(size)] for _ in range(size)]
        self.agent = {"col": 0, "row": 0}
        self.blocks = [
            {"col": 1, "row": 3},
            {"col": 3, "row": 1}
        ]
        self.goal = {"col": 4, "row": 4}

        self.block_reward = -1  # 장애물 도착 시 보상
        self.goal_reward = 10   # 목적지 도착 시 보상
        self.update_grid()

        self.total_reward = 0.
        self.current_reward = 0.
        self.total_game = 0

    def update_grid(self):
        self.grid = [['-' for _ in range(self.size)] for _ in range(self.size)]
        self.grid[self.agent["row"]][self.agent["col"]] = 'A'
        for block in self.blocks:
            self.grid[block["row"]][block["col"]] = 'B'
        self.grid[self.goal["row"]][self.goal["col"]] = 'G'

    def print_grid(self):
        print("\n")
        for row in self.grid:
            for cell in row:
                print(cell, end=' ')
            print()

    def move_agent(self, direction):
        # 방향에 따른 에이전트 위치 업데이트
        if direction == "UP":
            self.agent["row"] = max(0, self.agent["row"] - 1)
        elif direction == "DOWN":
            self.agent["row"] = min(self.size - 1, self.agent["row"] + 1)
        elif direction == "LEFT":
            self.agent["col"] = max(0, self.agent["col"] - 1)
        elif direction == "RIGHT":
            self.agent["col"] = min(self.size - 1, self.agent["col"] + 1)

        self.update_rewards()

    def update_rewards(self):
        # 위치에 따른 보상 업데이트
        if self.agent == self.goal: # 목적지에 도착했을 때 보상 주기
            self.current_reward += self.goal_reward
        elif self.agent in self.blocks: # 장애물에 도착했을 때 보상 주기
            self.current_reward += self.block_reward


        self.total_reward += self.current_reward
        self.update_grid()

    def reset(self):
        self.agent = {"col": 0, "row": 0}
        self.current_reward = 0
        self.total_reward = 0
        self.total_game += 1
        self.update_grid()

    def agent_action(self):
        # 사용자 입력에 따라 에이전트 이동
        action = input("Move (w=up, s=down, a=left, d=right): ").strip().lower()
        if action == 'w':
            self.move_agent("UP")
        elif action == 's':
            self.move_agent("DOWN")
        elif action == 'a':
            self.move_agent("LEFT")
        elif action == 'd':
            self.move_agent("RIGHT")
        else:
            print("'w', 's', 'a', 'd' 만 사용 가능합니다.")

        if self.the_end():
            print("에피소드 종료")
            print(f"Total Reward: {self.total_reward}")
            if self.agent == self.goal:
                print("목적지에 도달")
            else:
                print("장애물에 도달")

            self.reset()

    def the_end(self):
        # 에이전트가 장애물과 충돌했거나 목적지에 도착하면 True 반환
        if self.agent in self.blocks or self.agent == self.goal:
            return True
        return False

    # 게임 실행
simulation = GridManager()
while True:
    simulation.print_grid()  # 현재 그리드 상황 출력
    simulation.agent_action()  # 입력에 따라 에이전트 이동 및 게임 상태 업데이트