import json

class ChessPiece:
    def __init__(self, color, symbol):
        self.color = color  # 'white' veya 'black'
        self.symbol = symbol
        self.has_moved = False

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = 'white'  # Oyuna beyaz başlar
        self.initialize_board()
    
    def initialize_board(self):
        # Taşların başlangıç pozisyonlarını ayarla
        # Piyonları yerleştir
        for col in range(8):
            self.board[1][col] = ChessPiece('black', '♟')
            self.board[6][col] = ChessPiece('white', '♙')
        
        # Diğer taşları yerleştir
        piece_order = ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']
        white_pieces = ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']
        
        for col in range(8):
            self.board[0][col] = ChessPiece('black', piece_order[col])
            self.board[7][col] = ChessPiece('white', white_pieces[col])
    
    def is_valid_position(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def make_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        if not self.is_valid_position(from_row, from_col) or not self.is_valid_position(to_row, to_col):
            return False, "Geçersiz pozisyon!"

        piece = self.board[from_row][from_col]
        if piece is None:
            return False, "Seçilen konumda taş yok!"

        if piece.color != self.current_turn:
            return False, f"Şu an {self.current_turn} taşların sırası!"

        if self.is_valid_move(from_pos, to_pos):
            # Hamleyi yap
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            piece.has_moved = True
            
            # Sırayı değiştir
            self.current_turn = 'black' if self.current_turn == 'white' else 'white'
            return True, "Hamle başarılı!"
        
        return False, "Geçersiz hamle!"

    def is_valid_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]

        # Hedef konumda kendi taşımız varsa geçersiz hamle
        if target and target.color == piece.color:
            return False

        # Her taş için özel hamle kontrolü
        if piece.symbol in ['♙', '♟']:  # Piyon
            return self.is_valid_pawn_move(from_pos, to_pos)
        elif piece.symbol in ['♖', '♜']:  # Kale
            return self.is_valid_rook_move(from_pos, to_pos)
        elif piece.symbol in ['♘', '♞']:  # At
            return self.is_valid_knight_move(from_pos, to_pos)
        elif piece.symbol in ['♗', '♝']:  # Fil
            return self.is_valid_bishop_move(from_pos, to_pos)
        elif piece.symbol in ['♕', '♛']:  # Vezir
            return self.is_valid_queen_move(from_pos, to_pos)
        elif piece.symbol in ['♔', '♚']:  # Şah
            return self.is_valid_king_move(from_pos, to_pos)

        return False

    def is_path_clear(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_step = 0 if from_row == to_row else (to_row - from_row) // abs(to_row - from_row)
        col_step = 0 if from_col == to_col else (to_col - from_col) // abs(to_col - from_col)
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        while (current_row, current_col) != (to_row, to_col):
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
        
        return True

    def is_valid_rook_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Kale sadece yatay veya dikey hareket edebilir
        if from_row != to_row and from_col != to_col:
            return False
        
        return self.is_path_clear(from_pos, to_pos)

    def is_valid_knight_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        # At L şeklinde hareket eder: 2 kare bir yönde, 1 kare diğer yönde
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def is_valid_bishop_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Fil sadece çapraz hareket edebilir
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        
        return self.is_path_clear(from_pos, to_pos)

    def is_valid_queen_move(self, from_pos, to_pos):
        # Vezir hem kale hem fil gibi hareket edebilir
        return self.is_valid_rook_move(from_pos, to_pos) or self.is_valid_bishop_move(from_pos, to_pos)

    def is_valid_king_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Şah her yönde sadece 1 kare hareket edebilir
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        return row_diff <= 1 and col_diff <= 1

    def is_valid_pawn_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        direction = -1 if piece.color == 'white' else 1

        # Düz ilerleme
        if from_col == to_col:
            # Bir kare ilerleme
            if to_row == from_row + direction and self.board[to_row][to_col] is None:
                return True
            # İlk hamlede iki kare ilerleme
            if not piece.has_moved and to_row == from_row + 2 * direction:
                if self.board[to_row][to_col] is None and self.board[from_row + direction][from_col] is None:
                    return True
        
        # Çapraz yeme hamlesi
        elif abs(to_col - from_col) == 1 and to_row == from_row + direction:
            if self.board[to_row][to_col] and self.board[to_row][to_col].color != piece.color:
                return True

        return False

    def display_board(self):
        print("  a b c d e f g h")  # Sütun etiketleri
        for row in range(8):
            print(f"{8-row}", end=" ")  # Satır numaraları
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    print('·', end=' ')
                else:
                    print(piece.symbol, end=' ')
            print(f"{8-row}")  # Satır numaralarını sağa da ekle
        print("  a b c d e f g h")

    def to_dict(self):
        """Oyun durumunu dictionary olarak döndür"""
        board_state = []
        for row in self.board:
            board_row = []
            for piece in row:
                if piece is None:
                    board_row.append(None)
                else:
                    board_row.append({
                        'color': piece.color,
                        'symbol': piece.symbol,
                        'has_moved': piece.has_moved
                    })
            board_state.append(board_row)
        
        return {
            'board': board_state,
            'current_turn': self.current_turn
        }

    @classmethod
    def from_dict(cls, data):
        """Dictionary'den oyun durumunu yükle"""
        game = cls()
        for i, row in enumerate(data['board']):
            for j, piece_data in enumerate(row):
                if piece_data is not None:
                    game.board[i][j] = ChessPiece(
                        piece_data['color'],
                        piece_data['symbol']
                    )
                    game.board[i][j].has_moved = piece_data['has_moved']
                else:
                    game.board[i][j] = None
        
        game.current_turn = data['current_turn']
        return game

def main():
    game = ChessBoard()
    while True:
        game.display_board()
        print(f"\n{game.current_turn.capitalize()} taşların sırası")
        
        try:
            move = input("Hamlenizi girin (örn: e2 e4): ").lower().split()
            if move[0] == 'quit':
                break

            # Girişi satranç koordinatlarından array indexlerine çevir
            from_col = ord(move[0][0]) - ord('a')
            from_row = 8 - int(move[0][1])
            to_col = ord(move[1][0]) - ord('a')
            to_row = 8 - int(move[1][1])

            success, message = game.make_move((from_row, from_col), (to_row, to_col))
            print(message)
            
        except (IndexError, ValueError):
            print("Geçersiz giriş! Doğru format: e2 e4")

if __name__ == "__main__":
    main() 