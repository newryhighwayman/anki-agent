# Python Standards

The following guidelines are **MANDATORY** for all Python code.

- 88 chars per line.

- NEVER use comments unless you are in a config file or if it is absolutely necessary to clarify complex logic.


## Imports

- NEVER use inline imports!


## Module-level variables

- Module-level variables and constants must come directly after imports (and any type definitions they depend on).

- NEVER define module-level variables halfway through a file, after function definitions.


## Functions

- Keep functions short and focused. A function should ideally do one and only one thing.


## Docstrings

- Use numpy-style docstrings.

- All code references must be wrapped in backticks (e.g. `variable_1`).

- All public functions and methods must have a docstring with at least `Parameters` and `Returns` sections.
  **Example**
    ```python
    def my_func(var1: int, var2: list[str]) -> float:
        """Short description of what function does.

        Parameters
        ----------
        var1 : int
            Short description of `var1`.

        var2: list of str
            Short description of `var2`.

        Returns
        -------
        float
            Short description of what is returned.
        """
    ```

- Private functions and methods do not require a `Parameters` or `Returns` section.


## Type hints

- All function signatures must use type hints.

- DO NOT use type hints on variable declarations.


## Line continuation

- NEVER use the `\` character for line continuation.

- ALWAYS rely on Python’s implicit line continuation inside parentheses, brackets, or braces.

**Example**
```python
❌ Bad
message = "This card was generated automatically by the agent " \
          "and includes pronunciation, audio, and an example sentence."

✅ Good
message = (
    "This card was generated automatically by the agent "
    "and includes pronunciation, audio, and an example sentence."
)
```

## Unit tests

- Unit tests should test **behaviour**, not implementation!