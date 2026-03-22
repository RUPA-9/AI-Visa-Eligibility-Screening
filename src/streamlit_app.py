"""
Bootstrap wrapper for Streamlit that safely loads the main `app.py` UI.

This loader will read `app.py`, strip surrounding Markdown/``` fences if they
exist (some files were saved with code fences), then execute the resulting
Python source. This preserves the original `app.py` file while allowing
`streamlit run streamlit_app.py` to work even when `app.py` contains fences.
"""
import pathlib
import runpy
import sys

ROOT = pathlib.Path(__file__).parent
APP_PATH = ROOT / "app.py"

def load_and_exec_app(path: pathlib.Path):
    text = path.read_text(encoding='utf-8')

    # If file appears to be wrapped in Markdown code fences, strip them.
    # Handles leading ```python or ``` and a trailing ```
    if text.lstrip().startswith('```'):
        # find first line break after opening fence
        parts = text.splitlines()
        # drop the first line (``` or ```python)
        parts = parts[1:]
        # if last line is a closing fence, drop it
        if parts and parts[-1].strip().endswith('```'):
            parts = parts[:-1]
        text = "\n".join(parts)

    # Execute the cleaned source in a fresh globals dict
    globals_dict = {
        "__name__": "__main__",
        "__file__": str(path),
    }
    try:
        exec(compile(text, str(path), 'exec'), globals_dict)
    except Exception:
        # Provide a helpful error message in the Streamlit logs
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    if not APP_PATH.exists():
        print(f"Could not find {APP_PATH}. Please ensure app.py exists in the same folder.")
        sys.exit(1)

    load_and_exec_app(APP_PATH)
