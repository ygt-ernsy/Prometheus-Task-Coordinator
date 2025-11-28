class NavigationMock:
    def __init__(self):
        self.current_pos = (0, 0, 0)

    def navigate_to(self, target_pos: tuple):
        print(f"Navigating from {self.current_pos} to {target_pos}")
        self.current_pos = target_pos
        print(f"Arrived at {self.current_pos}")
        return True  
    
    def get_current(self):
        return self.current_pos
