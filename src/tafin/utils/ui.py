import sys
import threading
import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Iterable, List, Optional


class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


class Spinner:
    """Simple terminal spinner running in a background thread."""

    FRAMES = ["|", "/", "-", "\\"]

    def __init__(self, message: str = "", color: str = Colors.CYAN):
        self.message = message
        self.color = color
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _animate(self):
        index = 0
        while self._running:
            frame = self.FRAMES[index % len(self.FRAMES)]
            sys.stdout.write(f"\r{self.color}{frame} {self.message}{Colors.ENDC}")
            sys.stdout.flush()
            time.sleep(0.08)
            index += 1

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self, final_message: str = "", symbol: str = "[OK]", symbol_color: str = Colors.GREEN):
        if not self._running:
            return
        self._running = False
        if self._thread:
            self._thread.join()
        sys.stdout.write("\r" + " " * (len(self.message) + 4) + "\r")
        if final_message:
            print(f"{symbol_color}{symbol}{Colors.ENDC} {final_message}")
        sys.stdout.flush()

    def update_message(self, message: str):
        self.message = message


def show_progress(message: str, success_message: str = ""):
    """Decorator that shows a spinner while the wrapped function executes."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            spinner = Spinner(message)
            spinner.start()
            try:
                result = func(*args, **kwargs)
                spinner.stop(success_message or message.replace("...", " done"), symbol="[OK]", symbol_color=Colors.GREEN)
                return result
            except Exception as exc:
                spinner.stop(f"Failed: {exc}", symbol="[!!]", symbol_color=Colors.RED)
                raise

        return wrapper

    return decorator


class UI:
    """Utility helpers for consistent console output."""

    def __init__(self):
        self.current_spinner: Optional[Spinner] = None

    @contextmanager
    def progress(self, message: str, success_message: str = ""):
        spinner = Spinner(message)
        self.current_spinner = spinner
        spinner.start()
        try:
            yield spinner
            spinner.stop(success_message or message.replace("...", " done"), symbol="[OK]", symbol_color=Colors.GREEN)
        except Exception as exc:
            spinner.stop(f"Failed: {exc}", symbol="[!!]", symbol_color=Colors.RED)
            raise
        finally:
            self.current_spinner = None

    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}=== {text} ==={Colors.ENDC}")

    def print_task_list(self, tasks: Iterable):
        tasks_list: List = list(tasks)
        if not tasks_list:
            return
        self.print_header("Planned Tasks")
        for task in tasks_list:
            desc = task.get("description", task) if isinstance(task, dict) else str(task)
            status = task.get("done", False) if isinstance(task, dict) else False
            checkbox = "[x]" if status else "[ ]"
            print(f"{Colors.DIM}{checkbox}{Colors.ENDC} {desc}")

    def print_task_start(self, task_desc: str):
        print(f"\n{Colors.CYAN}{Colors.BOLD}[task]{Colors.ENDC} {task_desc}")

    def print_task_done(self, task_desc: str):
        print(f"{Colors.GREEN}[done]{Colors.ENDC} {Colors.DIM}{task_desc}{Colors.ENDC}")

    def print_tool_run(self, tool: str, result: str = ""):
        preview = f" ({result[:50]}...)" if result else ""
        print(f"{Colors.YELLOW}[tool]{Colors.ENDC} {tool}{preview}")

    def print_answer(self, answer: str):
        width = 80
        border = "+" + "-" * (width - 2) + "+"
        print(f"\n{Colors.BLUE}{border}{Colors.ENDC}")
        title = "ANSWER"
        padding = (width - len(title) - 2) // 2
        print(f"{Colors.BLUE}|{' ' * padding}{Colors.BOLD}{title}{Colors.ENDC}{Colors.BLUE}{' ' * (width - len(title) - padding - 2)}|{Colors.ENDC}")
        print(f"{Colors.BLUE}{border}{Colors.ENDC}")

        for line in answer.splitlines() or [""]:
            for wrapped in self._wrap_line(line, width - 4):
                print(f"{Colors.BLUE}| {Colors.ENDC}{wrapped.ljust(width - 4)}{Colors.BLUE} |{Colors.ENDC}")

        print(f"{Colors.BLUE}{border}{Colors.ENDC}\n")

    def print_info(self, message: str):
        print(f"{Colors.DIM}{message}{Colors.ENDC}")

    def print_error(self, message: str):
        print(f"{Colors.RED}[error]{Colors.ENDC} {message}")

    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}[warn]{Colors.ENDC} {message}")

    @staticmethod
    def _wrap_line(text: str, max_width: int) -> List[str]:
        if not text:
            return [""]
        words = text.split()
        lines: List[str] = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= max_width:
                current = f"{current} {word}".strip()
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
