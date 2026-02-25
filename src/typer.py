"""
Minimal stub implementation of the `typer` module.

This exists only so that Gradio's CLI import works in environments
where the real `typer` package is not available. We do NOT actually
use the Gradio CLI in this project, so it's safe for these functions
to be no-ops.

If you later install the real `typer` package into your environment,
it will be shadowed by this local module. In that case, you can
delete this file and rely on the real library instead.
"""

from typing import Any, Callable, Optional, TypeVar


T = TypeVar("T", bound=Callable[..., Any])


class Typer:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def command(self, *args: Any, **kwargs: Any) -> Callable[[T], T]:
        def decorator(fn: T) -> T:
            return fn

        return decorator

    def callback(self, *args: Any, **kwargs: Any) -> Callable[[T], T]:
        def decorator(fn: T) -> T:
            return fn

        return decorator

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        # In the real Typer, this would run the CLI app.
        # We never invoke it in this project.
        return None


def Option(
    default: Any = ...,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Stub for typer.Option."""
    return default


def Argument(
    default: Any = ...,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Stub for typer.Argument."""
    return default


def echo(message: Optional[str] = None) -> None:
    """Stub for typer.echo."""
    if message:
        print(message)


__all__ = ["Typer", "Option", "Argument", "echo"]

