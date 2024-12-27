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
        self.move_history = []  # [(from_pos, to_pos, captured_piece), ...]
        self.current_move = -1  # Şu anki hamle indeksi
    
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
            # Hamleyi geçici olarak yap
            captured_piece = self.board[to_row][to_col]
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            
            # Hamle sonrası kendi şahımız tehdit altında mı kontrol et
            if self.is_king_in_check(piece.color):
                # Hamleyi geri al
                self.board[from_row][from_col] = piece
                self.board[to_row][to_col] = captured_piece
                return False, "Bu hamle şahınızı tehlikeye atar!"
            
            # Hamle geçerliyse devam et
            piece.has_moved = True
            
            # Hamle geçmişini güncelle
            self.current_move += 1
            if self.current_move < len(self.move_history):
                self.move_history = self.move_history[:self.current_move]
            self.move_history.append((from_pos, to_pos, captured_piece))
            
            # Sırayı değiştir
            self.current_turn = 'black' if self.current_turn == 'white' else 'white'
            return True, "Hamle başarılı!"
        
        return False, "Geçersiz hamle!"

    def undo_move(self):
        """Son hamleyi geri al"""
        if self.current_move < 0:
            return False, "Geri alınacak hamle yok!"
        
        # Son hamleyi al
        from_pos, to_pos, captured_piece = self.move_history[self.current_move]
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Taşı geri taşı
        piece = self.board[to_row][to_col]
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured_piece
        
        # Sırayı geri al
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        self.current_move -= 1
        return True, "Hamle geri alındı"

    def redo_move(self):
        """Geri alınan hamleyi tekrar yap"""
        if self.current_move >= len(self.move_history) - 1:
            return False, "İleri alınacak hamle yok!"
        
        # Bir sonraki hamleyi al
        from_pos, to_pos, _ = self.move_history[self.current_move + 1]
        
        # Hamleyi tekrar yap
        piece = self.board[from_pos[0]][from_pos[1]]
        captured_piece = self.board[to_pos[0]][to_pos[1]]
        
        self.board[to_pos[0]][to_pos[1]] = piece
        self.board[from_pos[0]][from_pos[1]] = None
        
        # Sırayı değiştir
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        self.current_move += 1
        return True, "Hamle ileri alındı"

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

    def get_valid_moves(self, from_pos):
        """Seçilen pozisyondaki taşın gidebileceği tüm geçerli konumları döndür"""
        valid_moves = []
        from_row, from_col = from_pos
        piece = self.board[from_row][from_col]
        
        if piece is None:
            return valid_moves
        
        # Tahtadaki tüm kareleri kontrol et
        for to_row in range(8):
            for to_col in range(8):
                to_pos = (to_row, to_col)
                # Aynı pozisyonu atlayalım
                if to_pos == from_pos:
                    continue
                
                # Hamle geçerli mi kontrol et
                if self.is_valid_move(from_pos, to_pos):
                    valid_moves.append(to_pos)
        
        return valid_moves

    def is_king_in_check(self, color):
        """Verilen renkteki şahın tehdit altında olup olmadığını kontrol et"""
        # Şahın konumunu bul
        king_pos = None
        king_symbol = '♔' if color == 'white' else '♚'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.symbol == king_symbol:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False
        
        # Rakip taşların şahı tehdit edip etmediğini kontrol et
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if self.is_valid_move((row, col), king_pos):
                        return True
        return False

    def is_checkmate(self, color):
        """Verilen renk için şah mat durumunu kontrol et"""
        # Eğer şah tehdit altında değilse mat değildir
        if not self.is_king_in_check(color):
            return False
        
        # Tüm taşları kontrol et
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    # Bu taşın yapabileceği tüm hamleleri kontrol et
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move((row, col), (to_row, to_col)):
                                # Hamleyi geçici olarak yap
                                captured_piece = self.board[to_row][to_col]
                                self.board[to_row][to_col] = piece
                                self.board[row][col] = None
                                
                                # Şah hala tehdit altında mı kontrol et
                                still_in_check = self.is_king_in_check(color)
                                
                                # Hamleyi geri al
                                self.board[row][col] = piece
                                self.board[to_row][to_col] = captured_piece
                                
                                # Eğer bir kurtuluş hamlesi bulunduysa mat değildir
                                if not still_in_check:
                                    return False
        
        # Hiçbir kurtuluş hamlesi bulunamadıysa mat olmuştur
        return True

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