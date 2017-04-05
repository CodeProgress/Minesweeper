import unittest
import Minesweeper


class Tests(unittest.TestCase):
    def setUp(self):
        self.size_of_board = 12
        self.num_mines = 20
        self.Game = Minesweeper.Game((self.size_of_board, self.num_mines))

    def tearDown(self):
        self.Game = None

    def reset_board_with_new_mine_locations(self, new_mine_locations):
        board_obj = self.Game.board

        board_obj.mine_locations = new_mine_locations
        board_obj.board = board_obj.empty_board()
        board_obj.populate_board_with_all_cells()

    def expected_error_for_bad_turn_input(self, expected_error, bad_inputs):
        for bad_input in bad_inputs:
            self.assertRaises(expected_error,
                              lambda: self.Game.turn_input_validator._validate_row_col(bad_input))

    @staticmethod
    def get_board_str(board):
        output = ""
        for row in board:
            output += ' '.join([str(x) for x in row]) + "\n"
        return output

    def initialize_non_random_game(self, size, num_mines, mine_locations):
        assert num_mines == len(mine_locations)
        self.Game = Minesweeper.Game((size, num_mines))
        self.reset_board_with_new_mine_locations(mine_locations)

    def test_board_size(self):
        expected = self.size_of_board
        num_rows = len(self.Game.board.board)
        num_cols = len(self.Game.board.board[0])
        self.assertEqual(expected, num_rows)
        self.assertEqual(expected, num_cols)

    def test_parameter_input_validator(self):
        validator = self.Game.param_input_validator

        size_too_small = -1
        size_too_big = 31
        self.assertRaises(ValueError,
                          lambda: validator._validate_size_of_grid(size_too_small))
        self.assertRaises(ValueError,
                          lambda: validator._validate_size_of_grid(size_too_big))

        size_of_board = 20
        too_many_mines = 401
        too_few_mines = -1
        self.assertRaises(ValueError,
                          lambda: validator._validate_num_mines(too_many_mines, size_of_board))
        self.assertRaises(ValueError,
                          lambda: validator._validate_num_mines(too_few_mines, size_of_board))

        valid_size = 20
        valid_num_mines = 400
        self.assertEqual(valid_size, validator._validate_size_of_grid(valid_size))
        self.assertEqual(valid_num_mines, validator._validate_num_mines(valid_num_mines, valid_size))

    def test_turn_input_validator(self):
        too_few_args = "10"
        too_many_args = "1 2 3"
        too_many_characters = "1 2 3 4 5 6"
        off_board_negative = "-1 0"
        off_board_positive = "20 50"
        non_ints = "a b"
        valid_input = "10 11"

        self.expected_error_for_bad_turn_input(Minesweeper.WrongNumberOfArguments, [too_few_args, too_many_args])

        self.expected_error_for_bad_turn_input(ValueError,
                                               [off_board_negative, off_board_positive, non_ints, too_many_characters])

        self.assertEqual((10, 11), self.Game.turn_input_validator._validate_row_col(valid_input))

    def test_is_cell_on_board(self):
        self.assertTrue(self.Game.board.is_cell_on_board(0, 0))
        self.assertTrue(self.Game.board.is_cell_on_board(self.size_of_board-1, self.size_of_board-1))

        self.assertFalse(self.Game.board.is_cell_on_board(5, -1))
        self.assertFalse(self.Game.board.is_cell_on_board(-1, 5))
        self.assertFalse(self.Game.board.is_cell_on_board(-1, -5))
        self.assertFalse(self.Game.board.is_cell_on_board(self.size_of_board, 5))
        self.assertFalse(self.Game.board.is_cell_on_board(5, self.size_of_board))
        self.assertFalse(self.Game.board.is_cell_on_board(self.size_of_board, self.size_of_board))

    def test_initial_board_layout(self):
        # regression test
        mine_locations = {(7, 3), (6, 9), (9, 1), (10, 17), (3, 0), (11, 2), (19, 4), (18, 4), (8, 7),
                          (0, 0), (14, 0), (5, 1), (15, 19), (12, 9), (15, 12), (9, 0), (6, 7), (15, 11),
                          (12, 13), (7, 19), (12, 4), (15, 18), (1, 10), (10, 0), (15, 17), (1, 1),
                          (10, 9), (6, 4), (5, 4), (6, 18), (8, 2), (19, 6), (16, 4), (17, 10), (1, 13),
                          (12, 7), (19, 17), (16, 12), (3, 5), (10, 13), (1, 12), (5, 16), (8, 12),
                          (3, 18), (10, 14), (4, 3), (1, 7), (11, 15), (3, 4), (8, 4)}

        self.initialize_non_random_game(20, 50, mine_locations)

        self.assertFalse(self.Game.is_game_over())
        self.assertFalse(self.Game.is_game_won)

        self.Game.board.uncover_all_cells()

        expected_board = "M 2 1 . . . 1 1 1 1 1 2 2 2 1 . . . . .\n" + \
                         "2 M 1 . . . 1 M 1 1 M 2 M M 1 . . . . .\n" + \
                         "2 2 1 1 2 2 2 1 1 1 1 2 2 2 1 . . 1 1 1\n" + \
                         "M 1 1 2 M M 1 . . . . . . . . . . 1 M 1\n" + \
                         "2 2 2 M 4 3 1 . . . . . . . . 1 1 2 1 1\n" + \
                         "1 M 2 3 M 2 1 1 2 1 1 . . . . 1 M 2 1 1\n" + \
                         "1 1 2 3 M 2 1 M 2 M 1 . . . . 1 1 2 M 2\n" + \
                         ". 1 2 M 3 2 2 2 3 1 1 1 1 1 . . . 1 2 M\n" + \
                         "2 3 M 3 M 1 1 M 1 . . 1 M 1 . . . . 1 1\n" + \
                         "M M 2 2 1 1 1 1 2 1 1 1 2 3 2 1 1 1 1 .\n" + \
                         "M 4 2 1 . . . . 1 M 1 . 1 M M 2 2 M 1 .\n" + \
                         "1 2 M 2 1 1 1 1 3 2 2 . 2 3 4 M 2 1 1 .\n" + \
                         ". 1 1 2 M 1 1 M 2 M 1 . 1 M 2 1 1 . . .\n" + \
                         "1 1 . 1 1 1 1 1 2 1 1 . 1 1 1 . . . . .\n" + \
                         "M 1 . . . . . . . . 1 2 2 1 . . 1 2 3 2\n" + \
                         "1 1 . 1 1 1 . . . . 1 M M 2 . . 1 M M M\n" + \
                         ". . . 1 M 1 . . . 1 2 4 M 2 . . 1 2 3 2\n" + \
                         ". . . 2 2 2 . . . 1 M 2 1 1 . . . . . .\n" + \
                         ". . . 2 M 3 1 1 . 1 1 1 . . . . 1 1 1 .\n" + \
                         ". . . 2 M 3 M 1 . . . . . . . . 1 M 1 .\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

    def test_uncovering_mine(self):
        mine_locations = {(0, 0), (1, 1), (2, 2)}
        self.initialize_non_random_game(6, 3, mine_locations)

        self.Game.update_board((0, 0))

        self.assertTrue(self.Game.is_game_over())
        self.assertFalse(self.Game.is_game_won)

        expected_board = "M X X X X X\n" + \
                         "X X X X X X\n" + \
                         "X X X X X X\n" + \
                         "X X X X X X\n" + \
                         "X X X X X X\n" + \
                         "X X X X X X\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

        self.Game.board.uncover_all_cells()

        expected_board = "M 2 1 . . .\n" + \
                         "2 M 2 1 . .\n" + \
                         "1 2 M 1 . .\n" + \
                         ". 1 1 1 . .\n" + \
                         ". . . . . .\n" + \
                         ". . . . . .\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

    def test_uncovering_empty_cell(self):
        mine_locations = {(0, 0), (1, 1), (2, 2)}
        self.initialize_non_random_game(6, 3, mine_locations)

        self.Game.update_board((4, 4))

        self.assertFalse(self.Game.is_game_over())
        self.assertFalse(self.Game.is_game_won)

        expected_board = "X X 1 . . .\n" + \
                         "X X 2 1 . .\n" + \
                         "1 2 X 1 . .\n" + \
                         ". 1 1 1 . .\n" + \
                         ". . . . . .\n" + \
                         ". . . . . .\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

    def test_uncovering_all_safecells(self):
        mine_locations = {(0, 0), (1, 1), (2, 2)}
        self.initialize_non_random_game(6, 3, mine_locations)

        self.Game.update_board((4, 4))
        self.Game.update_board((1, 0))

        self.assertFalse(self.Game.is_game_over())
        self.assertFalse(self.Game.is_game_won)

        expected_board = "X X 1 . . .\n" + \
                         "2 X 2 1 . .\n" + \
                         "1 2 X 1 . .\n" + \
                         ". 1 1 1 . .\n" + \
                         ". . . . . .\n" + \
                         ". . . . . .\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

        self.Game.update_board((0, 1))

        self.assertTrue(self.Game.is_game_over())
        self.assertTrue(self.Game.is_game_won)

        expected_board = "X 2 1 . . .\n" + \
                         "2 X 2 1 . .\n" + \
                         "1 2 X 1 . .\n" + \
                         ". 1 1 1 . .\n" + \
                         ". . . . . .\n" + \
                         ". . . . . .\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

        self.Game.board.uncover_all_cells()
        expected_board = "M 2 1 . . .\n" + \
                         "2 M 2 1 . .\n" + \
                         "1 2 M 1 . .\n" + \
                         ". 1 1 1 . .\n" + \
                         ". . . . . .\n" + \
                         ". . . . . .\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

    def test_zero_dimensional_game(self):
        mine_locations = {}
        self.initialize_non_random_game(0, 0, mine_locations)
        self.assertTrue(self.Game.is_game_over())
        self.assertTrue(self.Game.is_game_won)

    def test_size_one_with_one_mine(self):
        mine_locations = {(0, 0)}
        self.initialize_non_random_game(1, 1, mine_locations)
        self.assertTrue(self.Game.is_game_over())
        self.assertTrue(self.Game.is_game_won)

        expected_board = "X\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

    def test_size_one_with_zero_mines(self):
        mine_locations = {}
        self.initialize_non_random_game(1, 0, mine_locations)
        self.assertFalse(self.Game.is_game_over())
        self.assertFalse(self.Game.is_game_won)

        expected_board = "X\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))

        self.Game.update_board((0, 0))

        self.assertTrue(self.Game.is_game_over())
        self.assertTrue(self.Game.is_game_won)

        expected_board = ".\n"
        self.assertEqual(expected_board, self.get_board_str(self.Game.board.board))
