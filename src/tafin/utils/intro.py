def print_intro():
    """Display the welcome screen with ASCII art."""
    # ANSI color codes
    LIGHT_BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Clear screen effect with some spacing
    print("\n" * 2)

    # Welcome box with light blue border
    box_width = 50
    welcome_text = "Welcome to TAFIN"
    border_line = "+" + "-" * (box_width - 2) + "+"
    padding = (box_width - len(welcome_text) - 2) // 2
    extra_space = (box_width - len(welcome_text) - 2) % 2

    print(f"{LIGHT_BLUE}{border_line}{RESET}")
    print(
        f"{LIGHT_BLUE}|{' ' * padding}{BOLD}{welcome_text}{RESET}"
        f"{LIGHT_BLUE}{' ' * (padding + extra_space)}|{RESET}"
    )
    print(f"{LIGHT_BLUE}{border_line}{RESET}")
    print()

    tafin_lines = [
        (LIGHT_BLUE, "TTTTTT   AAAAA   FFFFFF  IIIII  N   N"),
        (CYAN,       "  TT    A     A  F         I    NN  N"),
        (MAGENTA,    "  TT    AAAAAAA  FFFF      I    N N N"),
        (YELLOW,     "  TT    A     A  F         I    N  NN"),
        (GREEN,      "  TT    A     A  F         I    N   N"),
    ]

    for color, line in tafin_lines:
        print(f"{BOLD}{color}{line}{RESET}")
    print()
    print("Your AI assistant for financial analysis.")
    print("Ask me any questions. Type 'exit' or 'quit' to end.")
    print()
