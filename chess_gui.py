import pygame
import os
from chess_game import ChessBoard, ChessPiece
import json
from datetime import datetime
pygame.init()

class ChessGUI:
    def __init__(self):
        self.SQUARE_SIZE = 80
        self.BOARD_SIZE = self.SQUARE_SIZE * 8
        self.CAPTURED_WIDTH = self.SQUARE_SIZE * 2
        self.WINDOW_SIZE = (self.BOARD_SIZE + self.CAPTURED_WIDTH, self.BOARD_SIZE)
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Satranç")
        
        # Renkler
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.HIGHLIGHT = (130, 151, 105)
        self.SIDEBAR_COLOR = (49, 46, 43)
        self.TEXT_COLOR = (255, 255, 255)
        self.INPUT_BG = (70, 70, 70)
        
        # Font
        self.font = pygame.font.SysFont('Arial', 24)
        
        # Oyuncu isimleri
        self.white_player = ""
        self.black_player = ""
        
        self.game = ChessBoard()
        self.selected_piece = None
        self.selected_pos = None
        self.captured_white = []
        self.captured_black = []
        self.piece_images = {}
        self.load_pieces()
        
        # Butonlar için renkler
        self.BUTTON_COLOR = (100, 100, 100)
        self.BUTTON_HOVER = (120, 120, 120)
        self.BUTTON_CLICK = (80, 80, 80)
        
        # Butonları küçült ve aşağıya taşı
        button_width = 100
        button_height = 30
        button_x = self.BOARD_SIZE + (self.CAPTURED_WIDTH - button_width) // 2
        button_start_y = self.BOARD_SIZE - (3 * button_height + 20)  # En altta 20 piksel boşluk
        
        # Ana butonlar (Kaydet/Yükle/Çıkış)
        self.save_button = pygame.Rect(button_x, button_start_y, button_width, button_height)
        self.load_button = pygame.Rect(button_x, button_start_y + button_height + 5, button_width, button_height)
        self.exit_button = pygame.Rect(button_x, button_start_y + 2 * (button_height + 5), button_width, button_height)
        
        # Geri/İleri butonları
        self.undo_button = pygame.Rect(button_x, button_start_y - (button_height + 5), button_width//2 - 2, button_height)
        self.redo_button = pygame.Rect(button_x + button_width//2 + 2, button_start_y - (button_height + 5), button_width//2 - 2, button_height)
        
        # Saves klasörünü oluştur
        self.saves_dir = "saves"
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)
        
        # Yeni renkler ekleyelim
        self.POSSIBLE_MOVE = (130, 151, 105, 128)  # Son değer (128) alpha/transparanlık için
        self.MOVE_INDICATOR = (100, 100, 100)
        self.CHECK_COLOR = (230, 100, 50)  # Koyu turuncu renk - şah durumu için
        
        # Olası hamleleri tutacak liste
        self.possible_moves = []

    def get_player_names(self):
        # Kayıtlı oyun yükleme seçeneği ekle
        saves = [f for f in os.listdir(self.saves_dir) if f.startswith('chess_save_')]
        if saves:
            if self.show_dialog("Kayıtlı oyun yüklemek ister misiniz?") == "Evet":
                save_file = self.show_load_game_menu()
                if save_file and self.load_game(save_file):
                    return True
        
        input_active = "white"
        white_input = ""
        black_input = ""
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_active == "white":
                            input_active = "black"
                        elif input_active == "black" and black_input:
                            self.white_player = white_input
                            self.black_player = black_input
                            return True
                    elif event.key == pygame.K_BACKSPACE:
                        if input_active == "white":
                            white_input = white_input[:-1]
                        else:
                            black_input = black_input[:-1]
                    else:
                        if input_active == "white":
                            white_input += event.unicode
                        else:
                            black_input += event.unicode
            
            # Ekranı temizle
            self.screen.fill(self.SIDEBAR_COLOR)
            
            # Başlık
            title = self.font.render("Oyuncu İsimleri", True, self.TEXT_COLOR)
            self.screen.blit(title, (self.WINDOW_SIZE[0]//2 - title.get_width()//2, 50))
            
            # Beyaz oyuncu girişi
            white_label = self.font.render("Beyaz Oyuncu:", True, self.TEXT_COLOR)
            self.screen.blit(white_label, (100, 150))
            
            pygame.draw.rect(self.screen, self.INPUT_BG, (100, 190, 300, 40))
            white_text = self.font.render(white_input, True, self.TEXT_COLOR)
            self.screen.blit(white_text, (110, 195))
            
            if input_active == "white":
                pygame.draw.rect(self.screen, self.TEXT_COLOR, (100, 190, 300, 40), 2)
            
            # Siyah oyuncu girişi
            black_label = self.font.render("Siyah Oyuncu:", True, self.TEXT_COLOR)
            self.screen.blit(black_label, (100, 250))
            
            pygame.draw.rect(self.screen, self.INPUT_BG, (100, 290, 300, 40))
            black_text = self.font.render(black_input, True, self.TEXT_COLOR)
            self.screen.blit(black_text, (110, 295))
            
            if input_active == "black":
                pygame.draw.rect(self.screen, self.TEXT_COLOR, (100, 290, 300, 40), 2)
            
            # Talimatlar
            instructions = self.font.render("Enter tuşu ile devam edin", True, self.TEXT_COLOR)
            self.screen.blit(instructions, (100, 400))
            
            pygame.display.flip()

    def draw_player_info(self):
        # Oyuncu isimlerini ve sırayı göster
        current_player = self.white_player if self.game.current_turn == 'white' else self.black_player
        turn_text = self.font.render(f"Sıra: {current_player}", True, self.TEXT_COLOR)
        # Sıra bilgisini geri/ileri butonlarının üstüne taşı
        text_y = self.undo_button.top - 30
        self.screen.blit(turn_text, (self.BOARD_SIZE + 10, text_y))

    def load_pieces(self):
        pieces = {
            '♔': 'wK', '♕': 'wQ', '♖': 'wR', '♗': 'wB', '♘': 'wN', '♙': 'wP',
            '♚': 'bK', '♛': 'bQ', '♜': 'bR', '♝': 'bB', '♞': 'bN', '♟': 'bP'
        }
        
        for symbol, filename in pieces.items():
            path = os.path.join('pieces', f'{filename}.png')
            try:
                image = pygame.image.load(path)
                image = pygame.transform.scale(image, (self.SQUARE_SIZE, self.SQUARE_SIZE))
                self.piece_images[symbol] = image
            except:
                print(f"Hata: {path} dosyası yüklenemedi")

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                
                # Seçili kareyi vurgula
                if self.selected_pos and self.selected_pos == (row, col):
                    color = self.HIGHLIGHT
                
                # Olası hamleleri vurgula
                elif (row, col) in self.possible_moves:
                    # Kare çiz
                    pygame.draw.rect(self.screen, color,
                                  (col * self.SQUARE_SIZE, 
                                   row * self.SQUARE_SIZE,
                                   self.SQUARE_SIZE, 
                                   self.SQUARE_SIZE))
                    
                    # Yarı saydam yeşil overlay
                    s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(s, self.POSSIBLE_MOVE, s.get_rect())
                    self.screen.blit(s, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE))
                    
                    # Merkeze nokta çiz
                    center_x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    center_y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    pygame.draw.circle(self.screen, self.MOVE_INDICATOR, 
                                    (center_x, center_y), 8)
                    continue
                
                # Şah durumunu vurgula
                piece = self.game.board[row][col]
                if piece:
                    if ((piece.symbol == '♔' and self.game.is_king_in_check('white')) or 
                        (piece.symbol == '♚' and self.game.is_king_in_check('black'))):
                        color = self.CHECK_COLOR
                
                pygame.draw.rect(self.screen, color,
                               (col * self.SQUARE_SIZE, 
                                row * self.SQUARE_SIZE,
                                self.SQUARE_SIZE, 
                                self.SQUARE_SIZE))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece:
                    image = self.piece_images.get(piece.symbol)
                    if image:
                        self.screen.blit(image, 
                                       (col * self.SQUARE_SIZE,
                                        row * self.SQUARE_SIZE))

    def get_square_from_mouse(self, pos):
        x, y = pos
        row = y // self.SQUARE_SIZE
        col = x // self.SQUARE_SIZE
        return row, col

    def draw_captured_pieces(self):
        # Yenen taşlar alanını çiz
        pygame.draw.rect(self.screen, self.SIDEBAR_COLOR,
                        (self.BOARD_SIZE, 0, self.CAPTURED_WIDTH, self.BOARD_SIZE))
        
        # Yenen taşları göster
        captured_pieces = [
            (self.captured_black, 0),                    # Beyazın yediği taşlar üstte
            (self.captured_white, self.BOARD_SIZE // 2)  # Siyahın yediği taşlar altta
        ]
        
        for pieces, base_y in captured_pieces:
            for i, piece in enumerate(pieces):
                x = self.BOARD_SIZE + (i % 2) * (self.SQUARE_SIZE // 2)
                y = base_y + (i // 2) * (self.SQUARE_SIZE // 2)
                
                image = self.piece_images.get(piece.symbol)
                if image:
                    small_image = pygame.transform.scale(image, 
                                                      (self.SQUARE_SIZE // 2, 
                                                       self.SQUARE_SIZE // 2))
                    self.screen.blit(small_image, (x, y))

    def save_game(self):
        """Oyunu kaydet"""
        game_state = {
            'board': self.game.to_dict(),
            'white_player': self.white_player,
            'black_player': self.black_player,
            'captured_white': [piece.symbol for piece in self.captured_white],
            'captured_black': [piece.symbol for piece in self.captured_black],
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Dosya adını oluştur
        current_time = datetime.now()
        date_str = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H-%M")
        
        # Oyuncu isimlerinden geçersiz karakterleri temizle
        def clean_name(name):
            # Dosya adı için uygun olmayan karakterleri kaldır veya değiştir
            return ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name)
        
        white_name = clean_name(self.white_player)
        black_name = clean_name(self.black_player)
        
        filename = f"{date_str}_{white_name}_vs_{black_name}_{time_str}.json"
        
        filepath = os.path.join(self.saves_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(game_state, f)
        return filename

    def load_game(self, filename):
        """Kayıtlı oyunu yükle"""
        try:
            filepath = os.path.join(self.saves_dir, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.game = ChessBoard.from_dict(data['board'])
            self.white_player = data['white_player']
            self.black_player = data['black_player']
            
            # Yenen taşları yükle
            self.captured_white = [ChessPiece('white', symbol) for symbol in data['captured_white']]
            self.captured_black = [ChessPiece('black', symbol) for symbol in data['captured_black']]
            
            return True
        except Exception as e:
            print(f"Oyun yüklenirken hata: {e}")
            return False

    def draw_buttons(self):
        """Butonları çiz"""
        for button, text in [
            (self.save_button, "Kaydet"),
            (self.load_button, "Yükle"),
            (self.exit_button, "Çıkış")
        ]:
            # Mouse pozisyonuna göre buton rengini değiştir
            mouse_pos = pygame.mouse.get_pos()
            if button.collidepoint(mouse_pos):
                color = self.BUTTON_HOVER
            else:
                color = self.BUTTON_COLOR
            
            pygame.draw.rect(self.screen, color, button)
            text_surface = self.font.render(text, True, self.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)
        
        # Geri/İleri butonları
        for button, text in [
            (self.undo_button, "←"),
            (self.redo_button, "→")
        ]:
            mouse_pos = pygame.mouse.get_pos()
            color = self.BUTTON_HOVER if button.collidepoint(mouse_pos) else self.BUTTON_COLOR
            
            pygame.draw.rect(self.screen, color, button)
            text_surface = self.font.render(text, True, self.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)

    def handle_button_click(self, pos):
        """Buton tıklamalarını işle"""
        if self.exit_button.collidepoint(pos):
            if self.show_dialog("Oyunu kaydetmek ister misiniz?") == "Evet":
                filename = self.save_game()
                print(f"Oyun kaydedildi: {filename}")
            return False
        
        elif self.save_button.collidepoint(pos):
            filename = self.save_game()
            print(f"Oyun kaydedildi: {filename}")
            return True
        
        elif self.load_button.collidepoint(pos):
            save_file = self.show_load_game_menu()
            if save_file:
                if self.load_game(save_file):
                    print(f"Oyun yüklendi: {save_file}")
                    return True
        
        elif self.undo_button.collidepoint(pos):
            success, message = self.game.undo_move()
            if success:
                # Yenen taşları da güncelle
                self.update_captured_pieces()
            print(message)
            return True
        
        elif self.redo_button.collidepoint(pos):
            success, message = self.game.redo_move()
            if success:
                # Yenen taşları da güncelle
                self.update_captured_pieces()
            print(message)
            return True
        
        return None

    def show_dialog(self, message, options=["Evet", "Hayır"]):
        """Dialog penceresi göster"""
        dialog_width = 400
        dialog_height = 150
        dialog_x = (self.WINDOW_SIZE[0] - dialog_width) // 2
        dialog_y = (self.WINDOW_SIZE[1] - dialog_height) // 2
        
        # Dialog butonları
        button_width = 100
        button_height = 40
        button_spacing = 20
        total_buttons_width = len(options) * button_width + (len(options) - 1) * button_spacing
        first_button_x = dialog_x + (dialog_width - total_buttons_width) // 2
        
        buttons = []
        for i, text in enumerate(options):
            x = first_button_x + i * (button_width + button_spacing)
            y = dialog_y + dialog_height - button_height - 20
            buttons.append((pygame.Rect(x, y, button_width, button_height), text))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button, text in buttons:
                        if button.collidepoint(event.pos):
                            return text
            
            # Dialog arkaplanı
            pygame.draw.rect(self.screen, self.SIDEBAR_COLOR, 
                            (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(self.screen, self.TEXT_COLOR, 
                            (dialog_x, dialog_y, dialog_width, dialog_height), 2)
            
            # Mesaj
            text_surface = self.font.render(message, True, self.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(dialog_x + dialog_width//2, 
                                                    dialog_y + 50))
            self.screen.blit(text_surface, text_rect)
            
            # Butonlar
            for button, text in buttons:
                pygame.draw.rect(self.screen, self.BUTTON_COLOR, button)
                text_surface = self.font.render(text, True, self.TEXT_COLOR)
                text_rect = text_surface.get_rect(center=button.center)
                self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()

    def show_load_game_menu(self):
        """Kayıtlı oyunları listele ve seçim yap"""
        # Tüm .json dosyalarını al (sadece chess_save_ ile başlayanları değil)
        saves = sorted([f for f in os.listdir(self.saves_dir) if f.endswith('.json')], reverse=True)
        if not saves:
            return None
        
        menu_width = 600
        menu_height = 400
        menu_x = (self.WINDOW_SIZE[0] - menu_width) // 2
        menu_y = (self.WINDOW_SIZE[1] - menu_height) // 2
        
        # Scroll bar ayarları
        scroll_bar_width = 20
        content_width = menu_width - scroll_bar_width - 40  # 40 piksel padding
        
        button_height = 50
        visible_items = min(6, len(saves))
        scroll_position = 0
        
        # Scroll bar hesaplamaları
        total_height = len(saves) * button_height
        visible_height = visible_items * button_height
        scroll_ratio = visible_height / total_height if total_height > visible_height else 1
        scroll_bar_height = max(50, visible_height * scroll_ratio)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # macOS touchpad scroll işlemi için
                    if event.button in [4, 5]:  # 4: yukarı scroll, 5: aşağı scroll
                        direction = -1 if event.button == 4 else 1
                        scroll_position = max(0, min(scroll_position + direction, 
                                                  len(saves) - visible_items))
                        continue
                    
                    # Geri dön butonu
                    back_button = pygame.Rect(menu_x + 20, menu_y + menu_height - 60, 100, 40)
                    if back_button.collidepoint(mouse_pos):
                        return None
                    
                    # Scroll bar tıklama kontrolü
                    scroll_bar_rect = pygame.Rect(
                        menu_x + menu_width - scroll_bar_width - 10,
                        menu_y + 70,
                        scroll_bar_width,
                        visible_height
                    )
                    if scroll_bar_rect.collidepoint(mouse_pos):
                        # Scroll bar'a tıklandığında pozisyonu güncelle
                        relative_y = (mouse_pos[1] - (menu_y + 70)) / visible_height
                        scroll_position = int(relative_y * (len(saves) - visible_items))
                        scroll_position = max(0, min(scroll_position, len(saves) - visible_items))
                    
                    # Kayıtlı oyunlar
                    for i in range(visible_items):
                        idx = scroll_position + i
                        if idx >= len(saves):
                            break
                        
                        button = pygame.Rect(menu_x + 20, 
                                           menu_y + 70 + i * button_height, 
                                           content_width,
                                           button_height - 5)
                        if button.collidepoint(mouse_pos):
                            return saves[idx]
                
                # Mouse tekerleği için scroll işlemi
                elif event.type == pygame.MOUSEWHEEL:
                    scroll_position = max(0, min(scroll_position - event.y * 2,  # Scroll hızını artırmak için 2 ile çarptık
                                              len(saves) - visible_items))
            
            # Menü arkaplanı
            pygame.draw.rect(self.screen, self.SIDEBAR_COLOR, 
                            (menu_x, menu_y, menu_width, menu_height))
            pygame.draw.rect(self.screen, self.TEXT_COLOR, 
                            (menu_x, menu_y, menu_width, menu_height), 2)
            
            # Başlık
            title = self.font.render("Kayıtlı Oyunlar", True, self.TEXT_COLOR)
            title_rect = title.get_rect(center=(menu_x + menu_width//2, menu_y + 30))
            self.screen.blit(title, title_rect)
            
            # Scroll bar arkaplanı
            pygame.draw.rect(self.screen, self.BUTTON_COLOR,
                            (menu_x + menu_width - scroll_bar_width - 10,
                             menu_y + 70,
                             scroll_bar_width,
                             visible_height))
            
            # Scroll bar
            scroll_pos = menu_y + 70 + (visible_height - scroll_bar_height) * (scroll_position / (len(saves) - visible_items)) if len(saves) > visible_items else menu_y + 70
            pygame.draw.rect(self.screen, self.TEXT_COLOR,
                            (menu_x + menu_width - scroll_bar_width - 10,
                             scroll_pos,
                             scroll_bar_width,
                             scroll_bar_height))
            
            # Kayıtlı oyunları listele
            for i in range(visible_items):
                idx = scroll_position + i
                if idx >= len(saves):
                    break
                
                save_file = saves[idx]
                try:
                    filepath = os.path.join(self.saves_dir, save_file)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        date = data.get('date', 'Tarih bilinmiyor')
                        white = data.get('white_player', 'Beyaz')
                        black = data.get('black_player', 'Siyah')
                        text = f"{date} - {white} vs {black}"
                except:
                    text = save_file
                
                button = pygame.Rect(menu_x + 20, 
                                   menu_y + 70 + i * button_height, 
                                   content_width,
                                   button_height - 5)
                pygame.draw.rect(self.screen, self.BUTTON_COLOR, button)
                
                text_surface = self.font.render(text, True, self.TEXT_COLOR)
                text_rect = text_surface.get_rect(midleft=(button.left + 10, button.centery))
                self.screen.blit(text_surface, text_rect)
            
            # Geri dön butonu
            back_button = pygame.Rect(menu_x + 20, menu_y + menu_height - 60, 100, 40)
            pygame.draw.rect(self.screen, self.BUTTON_COLOR, back_button)
            back_text = self.font.render("Geri", True, self.TEXT_COLOR)
            back_rect = back_text.get_rect(center=back_button.center)
            self.screen.blit(back_text, back_rect)
            
            pygame.display.flip()

    def update_captured_pieces(self):
        """Yenen taşları hamle geçmişine göre güncelle"""
        self.captured_white = []
        self.captured_black = []
        
        for i in range(self.game.current_move + 1):
            _, _, captured_piece = self.game.move_history[i]
            if captured_piece:
                if captured_piece.color == 'white':
                    self.captured_white.append(captured_piece)
                else:
                    self.captured_black.append(captured_piece)

    def show_checkmate_dialog(self, winner):
        """Şah mat durumunda kazananı gösteren dialog"""
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.WINDOW_SIZE[0] - dialog_width) // 2
        dialog_y = (self.WINDOW_SIZE[1] - dialog_height) // 2
        
        winner_name = self.white_player if winner == 'white' else self.black_player
        message = f"ŞAH MAT! {winner_name} kazandı!"
        
        button_width = 150
        button_height = 40
        button = pygame.Rect(dialog_x + (dialog_width - button_width) // 2,
                            dialog_y + dialog_height - button_height - 20,
                            button_width, button_height)
        
        # Kazananı daha büyük fontla göster
        big_font = pygame.font.SysFont('Arial', 32, bold=True)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button.collidepoint(event.pos):
                        return
            
            # Dialog arkaplanı
            pygame.draw.rect(self.screen, self.SIDEBAR_COLOR, 
                            (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(self.screen, self.TEXT_COLOR, 
                            (dialog_x, dialog_y, dialog_width, dialog_height), 2)
            
            # Şah Mat mesajı
            text_surface = big_font.render("ŞAH MAT!", True, self.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(dialog_x + dialog_width//2, 
                                                    dialog_y + 50))
            self.screen.blit(text_surface, text_rect)
            
            # Kazanan mesajı
            winner_text = self.font.render(f"{winner_name} kazandı!", True, self.TEXT_COLOR)
            winner_rect = winner_text.get_rect(center=(dialog_x + dialog_width//2, 
                                                     dialog_y + 100))
            self.screen.blit(winner_text, winner_rect)
            
            # Buton
            pygame.draw.rect(self.screen, self.BUTTON_COLOR, button)
            button_text = self.font.render("Tamam", True, self.TEXT_COLOR)
            button_rect = button_text.get_rect(center=button.center)
            self.screen.blit(button_text, button_rect)
            
            pygame.display.flip()

    def run(self):
        # Önce oyuncu isimlerini al
        if not self.get_player_names():
            return

        running = True
        success = False  # success değişkenini başlangıçta tanımla
        while running:
            # Mevcut durumda şah mat kontrolü yap
            if self.game.current_turn == 'white':
                if self.game.is_checkmate('white'):
                    self.show_checkmate_dialog('black')  # Siyah kazandı
                    running = False
                    continue
            else:
                if self.game.is_checkmate('black'):
                    self.show_checkmate_dialog('white')  # Beyaz kazandı
                    running = False
                    continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Önce buton tıklamalarını kontrol et
                    button_result = self.handle_button_click(pos)
                    if button_result is not None:
                        if not button_result:
                            running = False
                        continue
                    
                    # Tahta tıklamalarını işle
                    board_pos = self.get_square_from_mouse(pos)
                    if board_pos[0] < 8 and board_pos[1] < 8:
                        success = False  # Her hamle denemesinde success'i sıfırla
                        if self.selected_piece is None:
                            piece = self.game.board[board_pos[0]][board_pos[1]]
                            if piece and piece.color == self.game.current_turn:
                                self.selected_piece = piece
                                self.selected_pos = board_pos
                                # Olası hamleleri hesapla
                                self.possible_moves = self.game.get_valid_moves(board_pos)
                        else:
                            # Hamle yap
                            if board_pos in self.possible_moves:  # Sadece geçerli hamlelere izin ver
                                target = self.game.board[board_pos[0]][board_pos[1]]
                                if target and target.color != self.selected_piece.color:
                                    if target.color == 'white':
                                        self.captured_white.append(target)
                                    else:
                                        self.captured_black.append(target)
                                
                                success, message = self.game.make_move(self.selected_pos, board_pos)
                                print(message)
                            
                            # Seçimi ve olası hamleleri temizle
                            self.selected_piece = None
                            self.selected_pos = None
                            self.possible_moves = []

                        # Hamle yapıldıktan sonra şah mat kontrolünü kaldır
                        # (Çünkü her döngü başında kontrol ediyoruz)

            # Ekranı güncelle
            self.draw_board()
            self.draw_pieces()
            self.draw_captured_pieces()
            self.draw_player_info()
            self.draw_buttons()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    gui = ChessGUI()
    gui.run() 