#!/usr/bin/env python3
"""
Tres en raya (Tic-Tac-Toe) sin dependencias.

Uso:
    python tres_en_raya.py
"""

from __future__ import annotations
import math
import sys
from typing import List, Optional, Tuple

# Representación:
# El tablero es una lista de 9 celdas (índices 0..8) que contienen:
# 'X', 'O' o ' ' (espacio) para vacía.
# La disposición visual es:
#  0 | 1 | 2
# -----------
#  3 | 4 | 5
# -----------
#  6 | 7 | 8

BOARD_SIZE = 9
EMPTY = " "

WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def new_board() -> List[str]:
    """Crea un tablero vacío."""
    return [EMPTY] * BOARD_SIZE


def print_board(board: List[str]) -> None:
    """Imprime el tablero en formato humano-legible con índices guía."""
    def p(i: int) -> str:
        return board[i] if board[i] != EMPTY else str(i + 1)

    row_sep = "-" * 11
    print(f" {p(0)} | {p(1)} | {p(2)} ")
    print(row_sep)
    print(f" {p(3)} | {p(4)} | {p(5)} ")
    print(row_sep)
    print(f" {p(6)} | {p(7)} | {p(8)} ")


def check_winner(board: List[str]) -> Optional[str]:
    """
    Revisa si hay ganador.
    Devuelve 'X' o 'O' si hay ganador, 'D' si hay empate (board lleno sin ganador),
    o None si el juego continúa.
    """
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    if all(cell != EMPTY for cell in board):
        return "D"  # Empate (Draw)
    return None


def available_moves(board: List[str]) -> List[int]:
    """Retorna la lista de índices (0..8) libres en el tablero."""
    return [i for i, v in enumerate(board) if v == EMPTY]


def make_move(board: List[str], idx: int, player: str) -> None:
    """Coloca la ficha de `player` ('X' o 'O') en la posición `idx`."""
    board[idx] = player


def minimax(board: List[str], player: str, maximizing: bool) -> Tuple[int, Optional[int]]:
    """
    Minimax recursivo simple (sin poda alfa-beta).
    Devuelve una tupla (score, move_index).
    - score: +1 si gana 'X', -1 si gana 'O', 0 empate.
    - move_index: la mejor jugada para el jugador actual (índice 0..8) o None.
    Notas:
        - Definimos la utilidad desde la perspectiva absoluta:
            X ganador -> score = +1
            O ganador -> score = -1
            Empate -> score = 0
        - `maximizing` = True cuando el nodo actual intenta maximizar la puntuación.
    """
    winner = check_winner(board)
    if winner is not None:
        if winner == "X":
            return 1, None
        if winner == "O":
            return -1, None
        return 0, None  # empate

    best_score = -math.inf if maximizing else math.inf
    best_move: Optional[int] = None

    for move in available_moves(board):
        # probar jugada
        board[move] = player
        # siguiente jugador
        next_player = "O" if player == "X" else "X"
        score, _ = minimax(board, next_player, not maximizing)
        # revertir jugada
        board[move] = EMPTY

        # actualizar mejor jugada según si maximizamos o minimizamos
        if maximizing:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move

        # Si encontramos un resultado óptimo absoluto, podemos salir
        if maximizing and best_score == 1:
            break
        if (not maximizing) and best_score == -1:
            break

    return best_score, best_move


def best_move_for_cpu(board: List[str], cpu_piece: str) -> int:
    """
    Determina la mejor jugada para la CPU usando Minimax.
    Si both players optimal: X maximiza, O minimiza (por convención en minimax).
    Si cpu_piece == 'X' entonces maximiza; si 'O' entonces minimiza.
    """
    maximizing = True if cpu_piece == "X" else False
    _, move = minimax(board, cpu_piece, maximizing)
    # move debería no ser None salvo error lógico; si es None, tomar un movimiento disponible
    if move is None:
        moves = available_moves(board)
        if not moves:
            raise RuntimeError("No hay movimientos disponibles al pedir mejor jugada")
        return moves[0]
    return move


def human_turn(board: List[str], human_piece: str) -> None:
    """Solicita y valida la entrada del jugador humano; modifica el tablero."""
    while True:
        try:
            choice = input(f"Turno {human_piece}. Ingresa el número de casilla (1-9): ").strip()
            if choice.lower() in ("q", "quit", "salir"):
                print("Abandonando partida.")
                sys.exit(0)
            pos = int(choice) - 1
            if pos < 0 or pos >= BOARD_SIZE:
                print("Número inválido. Debe estar entre 1 y 9.")
                continue
            if board[pos] != EMPTY:
                print("Casilla ocupada. Elige otra.")
                continue
            make_move(board, pos, human_piece)
            return
        except ValueError:
            print("Entrada inválida. Introduce un número entre 1 y 9, o 'q' para salir.")


def run_two_player() -> None:
    """Bucle de juego para 2 jugadores locales."""
    board = new_board()
    current = "X"
    while True:
        print_board(board)
        human_turn(board, current)
        winner = check_winner(board)
        if winner is not None:
            print_board(board)
            if winner == "D":
                print("Empate.")
            else:
                print(f"Gana {winner}!")
            return
        # cambiar turno
        current = "O" if current == "X" else "X"


def run_vs_cpu() -> None:
    """Bucle de juego contra CPU. El usuario elige pieza y si inicia."""
    board = new_board()
    # elección del humano
    while True:
        choice = input("Jugar contra CPU. Elige tu ficha: X (empieza) u O: ").strip().upper()
        if choice in ("X", "O"):
            human_piece = choice
            cpu_piece = "O" if human_piece == "X" else "X"
            break
        print("Entrada inválida. Escribe 'X' o 'O'.")

    current = "X"  # X siempre mueve primero
    while True:
        print_board(board)
        if current == human_piece:
            human_turn(board, human_piece)
        else:
            print("Turno CPU...")
            move = best_move_for_cpu(board, cpu_piece)
            make_move(board, move, cpu_piece)
            print(f"CPU coloca {cpu_piece} en la casilla {move + 1}.")

        winner = check_winner(board)
        if winner is not None:
            print_board(board)
            if winner == "D":
                print("Empate.")
            else:
                print(f"Gana {winner}!")
            return

        # cambiar turno
        current = "O" if current == "X" else "X"


def main() -> None:
    """Menú principal y selección de modo de juego."""
    print("=== Tres en raya / Tic-Tac-Toe ===")
    print("Selecciona modo:")
    print("  1) 2 jugadores (local)")
    print("  2) Jugar contra CPU (IA óptima)")
    print("  q) Salir")

    while True:
        opt = input("Opción: ").strip().lower()
        if opt == "1":
            run_two_player()
            break
        if opt == "2":
            run_vs_cpu()
            break
        if opt in ("q", "quit", "salir"):
            print("Saliendo.")
            return
        print("Opción inválida. Escribe 1, 2 o q.")

    # luego de terminar, preguntar si desea jugar otra vez
    while True:
        again = input("¿Jugar otra partida? (s/n): ").strip().lower()
        if again and again[0] == "s":
            main()
            return
        if again and again[0] == "n":
            print("Gracias por jugar.")
            return
        print("Responde 's' o 'n'.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario. Adiós.")
        sys.exit(0)
