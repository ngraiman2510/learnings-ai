WINNING_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
]


def print_board(board):
    print()
    for row in range(3):
        start = row * 3
        print(f" {board[start]} | {board[start + 1]} | {board[start + 2]} ")
        if row < 2:
            print("---+---+---")
    print()


def get_winner(board):
    for a, b, c in WINNING_LINES:
        if board[a] == board[b] == board[c] and board[a] in ("X", "O"):
            return board[a]
    return None


def ask_move(board, player):
    while True:
        choice = input(f"Player {player}, choose a square (1-9): ")
        if not choice.isdigit() or not 1 <= int(choice) <= 9:
            print("Please enter a number from 1 to 9.")
            continue
        index = int(choice) - 1
        if board[index] in ("X", "O"):
            print("That square is taken. Try another.")
            continue
        return index


def play():
    board = [str(n) for n in range(1, 10)]  # shows 1-9 as square numbers
    player = "X"

    for _ in range(9):
        print_board(board)
        board[ask_move(board, player)] = player

        if get_winner(board):
            print_board(board)
            print(f"Player {player} wins!")
            return

        player = "O" if player == "X" else "X"

    print_board(board)
    print("It's a draw!")


if __name__ == "__main__":
    play()
    while input("Play again? (y/n): ").lower() == "y":
        play()
    print("Thanks for playing!")