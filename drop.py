class Drop():
    def __init__(self, coord, ident):
        self.coord = coord
        self.ident = ident
        assert len(self.coord) == 2

    def __len__(self):
        return len(self.coord)

    def __getitem__(self, i):
        assert i >= 0
        return self.coord[i]

    def __eq__(self, other):
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True
