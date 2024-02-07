class GridManager:
    def __init__(self, size=5):
        self.size = size
        self.grid = [['-' for _ in range(size)] for _ in range(size)] # 나머지 공간은 -으로 채우기
        self.agent = {"col": 0, "row": 0}  # 에이전트의 초기 위치
        self.blocks = [
            {"col": 1, "row": 3}, # 장애물 1의 위치
            {"col": 3, "row": 1,} # 장애물 2의 위치
        ]
        self.goal = {"col": 4, "row": 4} # 목적지의 위치
        self.update_grid()

        self.total_reward = 0.
        self.current_reward = 0.
        self.total_game = 0

    def update_grid(self):
        ### 그리드를 초기화하고 객체의 위치를 업데이트하는 메서드
        # 그리드 초기화
        self.grid = [['-' for _ in range(self.size)] for _ in range(self.size)]
        # 에이전트의 위치는 A로 나타내기
        self.grid[self.agent["row"]][self.agent["col"]] = 'A'
        # 장애물의 위치는 B로 나타내기
        for block in self.blocks:
            self.grid[block["row"]][block["col"]] = 'B'
        # 목적지의 위치는 G로 나타내기
        self.grid[self.goal["row"]][self.goal["col"]] = 'G'

    def print_grid(self):
        ### 그리드를 출력하는 메서드
        for row in self.grid:
            for cell in row:
                print(cell, end=' ')
            print()

    def move_agent(self, col, row):
        """자동차의 위치를 변경하는 메서드"""
        self.agent["col"] = col
        self.agent["row"] = row
        self.update_grid()

    def agent_action(self, action):
        # 에이전트가 그리드를 넘어가지 못하게하는 코드
        self.agent["col"] = max(0, min(self.agent["col"], self.size))
        self.agent["row"] = max(0, min(self.agent["row"], self.size))

    def reset(self): # 에이전트, 장애물 위치, 보상값 초기화
        self.current_reward = 0
        self.total_game += 1


simulation=GridManager()
simulation.print_grid()  # 초기 그리드 출력
