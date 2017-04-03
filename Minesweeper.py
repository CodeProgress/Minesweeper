import sys
import random
import itertools


class Game(object):
    def __init__(self, test_mode_parameters=None):
        self.test_mode_parameters = test_mode_parameters
        self.ascii_art = AsciiArt()
        if not self.test_mode_parameters:
            self.print_title_screen()
        self.max_side_length_of_grid = 30
        self.param_input_validator = ParameterInputValidator(self.max_side_length_of_grid)    # Dependency

        # variables initialized in separate method to enable reset for additional round
        self.size_of_square_grid = None
        self.num_mines = None
        self.board = None
        self.is_game_won = None
        self.max_len_of_turn_input_str = None
        self.turn_input_validator = None

        self.initialize_variables()

    def initialize_variables(self):
        if not self.test_mode_parameters:
            self.size_of_square_grid = self.get_size_of_grid_from_user()
            self.num_mines = self.get_num_mines_from_user()
        else:
            self.size_of_square_grid, self.num_mines = self.test_mode_parameters

        self.board = Board(self.size_of_square_grid, self.num_mines)    # Dependency
        self.is_game_won = False
        self.max_len_of_turn_input_str = self.get_max_len_turn_input_str()
        self.turn_input_validator \
            = TurnInputValidator(self.max_len_of_turn_input_str, self.board.is_cell_on_board)    # Dependency

    def play_game(self):
        self.print_instructions()
        while True:
            self.play_round()
            play_again = raw_input("\n==>Would you like to play again? y/n: ").strip()
            if play_again != "y":
                break
            self.reset_for_next_round()
        print "See you next time!"

    def play_round(self):
        while not self.is_game_over():
            print self.board
            move = self.get_row_col_from_user()
            self.update_board(move)

        self.board.uncover_all_cells()
        print self.board
        self.print_outcome()

    def reset_for_next_round(self):
        self.initialize_variables()

    def get_row_col_from_user(self):
        input_message = "==>Enter row number and column number to uncover: "
        error_message = "\nInvalid move.  {}" \
                        + "\nType row (space) col.  Ex: '4 5' (without quotes)" \
                        + "\nor press q to quit\n"

        return self.turn_input_validator.get_validated_row_col(input_message, error_message)

    def get_size_of_grid_from_user(self):
        print "First, let's set up the square NxN playing grid."
        print "What size would you like to choose for N?"

        input_message = "\n==>Enter an integer between 0 and {}: ".format(self.max_side_length_of_grid)
        error_message = "\nInvalid response.  {}" \
                        + "\nExample: '4' (without quotes)" \
                        + "\nThis would create a 4x4 grid" \
                        + "\n(Enter q to quit)"

        return self.param_input_validator.get_validated_size_of_grid(input_message, error_message)

    def get_num_mines_from_user(self):
        input_message = "\nHow many mines should be randomly placed within the grid?" \
                        + "\n==>Enter an integer between 0 and {}: ".format(self.size_of_square_grid**2)
        error_message = "\nInvalid response. {}" \
                        + "\n(Enter q to quit)"

        return self.param_input_validator.get_validated_num_mines(
            input_message, error_message, self.size_of_square_grid)

    def is_game_over(self):
        if self.board.are_all_safe_cells_flipped():
            self.is_game_won = True
            return True
        return self.board.mine_uncovered

    def get_max_len_turn_input_str(self):
        max_string_len_of_zero_based_row_index = len(str(self.size_of_square_grid - 1))
        max_string_len_of_zero_based_col_index = len(str(self.size_of_square_grid - 1))
        size_of_single_space_between_indices = 1
        return max_string_len_of_zero_based_row_index \
            + max_string_len_of_zero_based_col_index \
            + size_of_single_space_between_indices

    def update_board(self, move):
        row, col = move
        cell = self.board.get_cell(row, col)
        self.board.uncover_cell(cell)

    def print_outcome(self):
        output = ""
        if self.is_game_won:
            output += self.ascii_art.winner
        else:
            output += "Unfortunately that was a mine :/ \nBetter luck next time!"
        print output + "\nThanks for playing :)"

    def print_instructions(self):
        header = self.ascii_art.header

        instructions = "\nTo uncover a cell, enter a row number and a column number separated by a space." \
                       + "\n--For example, to select row 3 and column 4, Enter: 3 4" \
                       + "\n--Row numbers are displayed vertically along the left side." \
                       + "\n--Column numbers are displayed horizontally along the top." \
                       + "\n(Enter q at any time to quit)\n"
        print header + instructions

    def print_title_screen(self):
        print self.ascii_art.minesweeper_title
        print "Welcome to Minesweeper!"


class Board(object):
    def __init__(self, side_length_of_square_grid, num_mines):
        self.side_length_of_square_grid = side_length_of_square_grid
        self.num_mines = num_mines
        self.num_safe_cells = self.side_length_of_square_grid**2 - self.num_mines
        self.num_safe_cells_uncovered = 0
        self.mine_uncovered = False

        self.transformations_to_get_neighboring_cells = \
            [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),            (0, 1),
             (1, -1),  (1, 0), (1, 1)]

        self.mine_locations = self.create_random_mine_locations()
        self.board = self.empty_board()
        self.populate_board_with_all_cells()

    def empty_board(self):
        num_rows = self.side_length_of_square_grid
        num_cols = self.side_length_of_square_grid
        return [[None] * num_cols for _ in range(num_rows)]

    def populate_board_with_all_cells(self):
        num_rows = self.side_length_of_square_grid
        num_cols = self.side_length_of_square_grid
        for row in range(num_rows):
            for col in range(num_cols):
                if (row, col) in self.mine_locations:
                    cell = Mine(row, col)    # Dependency
                else:
                    cell = SafeCell(row, col)    # Dependency
                    self.assign_surrounding_cells_to_cell(cell)
                self.board[row][col] = cell
        self.assign_num_surrounding_mines_to_all_safe_cells()

    def create_random_mine_locations(self):
        possible_mine_locations = itertools.product(
            xrange(self.side_length_of_square_grid),
            xrange(self.side_length_of_square_grid))
        return set(random.sample(list(possible_mine_locations), self.num_mines))

    def is_cell_on_board(self, row, col):
        return (0 <= row < self.side_length_of_square_grid) \
            and (0 <= col < self.side_length_of_square_grid)

    def are_all_safe_cells_flipped(self):
        return self.num_safe_cells_uncovered == self.num_safe_cells

    def assign_surrounding_cells_to_cell(self, cell):
        surrounding_cell_locations = []
        for transformation in self.transformations_to_get_neighboring_cells:
            possible_surr_cell_location = (cell.row + transformation[0], cell.col + transformation[1])
            if self.is_cell_on_board(*possible_surr_cell_location):
                surrounding_cell_locations.append(possible_surr_cell_location)
        cell.surrounding_cell_locations = surrounding_cell_locations

    def assign_num_surrounding_mines_to_all_safe_cells(self):
        for row in self.board:
            for cell in row:
                if type(cell) is SafeCell:
                    self.assign_num_surrounding_mines(cell)

    def assign_num_surrounding_mines(self, cell):
        count = 0
        for surrounding_cell in cell.surrounding_cell_locations:
            if type(self.get_cell(*surrounding_cell)) is Mine:
                count += 1
        cell.num_mines_in_surrounding_cells = count

    def get_cell(self, row, col):
        return self.board[row][col]

    def uncover_all_cells(self):
        for row in range(self.side_length_of_square_grid):
            for col in range(self.side_length_of_square_grid):
                cell = self.get_cell(row, col)
                cell.uncover()

    def uncover_cell(self, cell):
        # if cell is already uncovered, don't do anything
        if not cell.is_covered:
            return

        cell.uncover()

        # Base case 1: cell is a Mine
        if type(cell) is Mine:
            self.mine_uncovered = True
            return

        self.num_safe_cells_uncovered += 1

        # Base case 2: cell has a mine surrounding it
        if not cell.has_zero_surrounding_mines():
            return

        # Recursive step
        for surrounding_cell_location in cell.surrounding_cell_locations:
            row, col = surrounding_cell_location
            surrounding_cell = self.get_cell(row, col)
            self.uncover_cell(surrounding_cell)

    def __str__(self):
        output = "\n    " + ' '.join([str(col).rjust(2) for col in range(self.side_length_of_square_grid)]) + "\n"
        output += "    " + "-- " * self.side_length_of_square_grid + "\n"
        for i, row in enumerate(self.board):
            output += str(i).rjust(2) + " | " + '  '.join([str(x) for x in row]) + "\n"
        return output


class Cell(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_covered = True
        self.num_mines_in_surrounding_cells = 0
        self.surrounding_cell_locations = []

    def get_name_representation(self):
        raise NotImplementedError

    def uncover(self):
        self.is_covered = False

    def __str__(self):
        if self.is_covered:
            return 'X'
        return self.get_name_representation()


class SafeCell(Cell):
    def get_name_representation(self):
        if self.has_zero_surrounding_mines():
            return '.'
        return str(self.num_mines_in_surrounding_cells)

    def has_zero_surrounding_mines(self):
        return self.num_mines_in_surrounding_cells == 0


class Mine(Cell):
    def get_name_representation(self):
        return 'M'


class AsciiArt(object):
    def __init__(self):
        self.winner = "   _____                            _       _" \
                      + "\n  / ____|                          | |     | |" \
                      + "\n | |     ___  _ __   __ _ _ __ __ _| |_ ___| |" \
                      + "\n | |    / _ \| '_ \ / _` | '__/ _` | __/ __| |" \
                      + "\n | |___| (_) | | | | (_| | | | (_| | |_\__ \_|" \
                      + "\n  \_____\___/|_| |_|\__, |_|  \__,_|\__|___(_)" \
                      + "\n  __     __          __/ |                _" \
                      + "\n  \ \   / /         |___/                | |" \
                      + "\n   \ \_/ /__  _   _  __      _____  _ __ | |" \
                      + "\n    \   / _ \| | | | \ \ /\ / / _ \| '_ \| |" \
                      + "\n     | | (_) | |_| |  \ V  V / (_) | | | |_|" \
                      + "\n     |_|\___/ \__,_|   \_/\_/ \___/|_| |_(_) \n"

        self.header = "                       _                _                 " \
                      + "\n  /\  /\_____      __ | |_ ___    _ __ | | __ _ _   _   _ " \
                      + "\n / /_/ / _ \ \ /\ / / | __/ _ \  | '_ \| |/ _` | | | | (_)" \
                      + "\n/ __  / (_) \ V  V /  | || (_) | | |_) | | (_| | |_| |  _ " \
                      + "\n\/ /_/ \___/ \_/\_/    \__\___/  | .__/|_|\__,_|\__, | (_)" \
                      + "\n                                 |_|            |___/     "

        self.minesweeper_title = "\n    __  ____" \
                                 + "\n   /  |/  (_)___  ___" \
                                 + "\n  / /|_/ / / __ \/ _ \\" \
                                 + "\n / /  / / / / / /  __/ " \
                                 + "\n/_/  /_/_/_/ /_/\___/" \
                                 + "\n   ______      _____  ___  ____  ___  _____" \
                                 + "\n  / ___/ | /| / / _ \/ _ \/ __ \/ _ \/ ___/" \
                                 + "\n (__  )| |/ |/ /  __/  __/ /_/ /  __/ /    " \
                                 + "\n/____/ |__/|__/\___/\___/ .___/\___/_/" \
                                 + "\n                       /_/             "


class WrongNumberOfArguments(TypeError):
    """Custom Exception for UserInputValidator"""
    pass


class GameTerminated(KeyboardInterrupt):
    """Custom Exception for UserInputValidator"""
    pass


class UserInputValidator(object):
    def __init__(self):
        self.termination_str = "q"

    @staticmethod
    def get_data_from_user(input_message, error_message, validation_function, extra_vf_args=()):
        while True:
            try:
                user_input = raw_input(input_message).strip()
                return validation_function(user_input, *extra_vf_args)
            except GameTerminated:
                sys.exit()
            except (ValueError, TypeError), e:
                print error_message.format(e)

    @staticmethod
    def validate_num_arguments(args_list, expected_num_arguments):
        if len(args_list) != expected_num_arguments:
            raise WrongNumberOfArguments("Number of args must equal {}".format(expected_num_arguments))

    def convert_arguments_to_ints(self, args_list):
        for i in range(len(args_list)):
            args_list[i] = self.convert_to_int(args_list[i])

    @staticmethod
    def convert_to_int(arg):
        try:
            return int(arg)
        except ValueError:
            raise ValueError("Input must be an int")

    def is_game_terminated(self, user_input):
        if user_input == self.termination_str:
            raise GameTerminated("Game Terminated")

    @staticmethod
    def validate_argument_inclusive_range(argument, min_value, max_value):
        if argument < min_value or argument > max_value:
            raise ValueError("{} is not within the inclusive range: {} to {}".format(argument, min_value, max_value))


class TurnInputValidator(UserInputValidator):
    def __init__(self, max_input_length, is_row_col_on_board_function):
        super(TurnInputValidator, self).__init__()
        self.max_input_length = max_input_length
        self.is_row_col_on_board_function = is_row_col_on_board_function
        self.expected_num_arguments = 2

    def _validate_row_col(self, user_input):
        self.is_game_terminated(user_input)
        self._validate_input_length(user_input)

        output_list = user_input.split(' ')
        self.validate_num_arguments(output_list, self.expected_num_arguments)
        self.convert_arguments_to_ints(output_list)

        row, col = output_list
        self._validate_cell_is_on_board(row, col)

        return row, col

    def get_validated_row_col(self, input_message, error_message):
        return self.get_data_from_user(input_message, error_message, self._validate_row_col)

    def _validate_input_length(self, user_input):
        if len(user_input) > self.max_input_length:
            raise ValueError("Input is too many characters")

    def _validate_cell_is_on_board(self, row, col):
        if not self.is_row_col_on_board_function(row, col):
            raise ValueError("Square row:{} col:{} is not on the board".format(row, col))


class ParameterInputValidator(UserInputValidator):
    def __init__(self, max_side_length):
        super(ParameterInputValidator, self).__init__()
        self.min_side_length = 0
        self.max_side_length = max_side_length
        self.min_num_mines = 0

    def _validate_size_of_grid(self, user_input):
        self.is_game_terminated(user_input)
        side_length_of_sq_grid = self.convert_to_int(user_input)
        self.validate_argument_inclusive_range(side_length_of_sq_grid, self.min_side_length, self.max_side_length)
        return side_length_of_sq_grid

    def get_validated_size_of_grid(self, input_message, error_message):
        return self.get_data_from_user(input_message, error_message, self._validate_size_of_grid)

    def _validate_num_mines(self, user_input, side_length_of_sq_grid):
        self.is_game_terminated(user_input)
        number_of_mines = self.convert_to_int(user_input)
        self.validate_argument_inclusive_range(number_of_mines, self.min_num_mines, side_length_of_sq_grid ** 2)
        return number_of_mines

    def get_validated_num_mines(self, input_message, error_message, side_length_of_sq_grid):
        return self.get_data_from_user(input_message, error_message, self._validate_num_mines, [side_length_of_sq_grid])


if __name__ == "__main__":
    g = Game()
    g.play_game()
