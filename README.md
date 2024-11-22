# Crossword Generator

## Overview
This project is a Crossword Generator, which builds and solves crossword puzzles using a constraint satisfaction problem (CSP) approach. It incorporates algorithms for node consistency, arc consistency, and backtracking to find optimal solutions.

## Features
- **Dynamic Puzzle Loading**: Load crossword structures and word banks from text files.
- **Constraint Satisfaction**: Ensures words fit the puzzle layout and adhere to overlap rules.
- **Custom Output**: Print or save completed puzzles as images.
- **Testing**: Includes a comprehensive suite of unit tests for key functionalities.

## File Structure

### Code
- `crossword.py`: Contains classes for representing crossword structures (`Crossword`) and variables (`Variable`). Defines overlaps, neighbors, and puzzle parsing.
- `generate.py`: Implements the `CrosswordCreator` class for solving the crossword using CSP techniques.
- `test_generate.py`: Unit tests for `CrosswordCreator` and related functionality.

### Data
- `structure0.txt`, `structure1.txt`, `structure2.txt`: Text files defining different crossword layouts where `_` represents open cells and `#` represents blocked cells.
- `words0.txt`, `words1.txt`, `words2.txt`: Word banks to be used as vocabulary for the puzzles.

## How to Use

### Requirements
- Python 3.x
- `Pillow` library for saving crossword puzzles as images

Install Pillow using pip:
```bash
pip install pillow
```

### Running the Generator
Use the following command to generate a crossword:
```bash
python generate.py <structure_file> <words_file> [output_file]
```
- `<structure_file>`: Path to the crossword structure file (e.g., `data/structure1.txt`).
- `<words_file>`: Path to the words file (e.g., `data/words1.txt`).
- `[output_file]` (optional): Path to save the crossword as an image.

### Example
```bash
python generate.py data/structure1.txt data/words1.txt output.png
```

### Unit Testing
Run unit tests with:
```bash
python -m unittest test_generate.py
```

## Key Components

### `crossword.py`
- **Variable Class**: Represents a word's placement, including its direction, starting point, and length.
- **Crossword Class**: Manages the puzzle's structure, vocabulary, variables, and overlaps.

### `generate.py`
- **Node Consistency**: Removes invalid words based on unary constraints (e.g., word length).
- **Arc Consistency**: Eliminates words that cause conflicts with neighboring variables.
- **Backtracking**: Recursively assigns words to variables until a solution is found.

### `test_generate.py`
Includes tests for:
- Node consistency
- Arc consistency
- Overlap handling
- Backtracking solution

## Data Format

### Structure Files
Each line represents a row in the crossword. Use `_` for open cells and `#` for blocked cells.

Example:
```
#___#
#_##_
#_##_
#_##_
#____
```

### Word Files
A list of words, one per line, to be used in the crossword.

Example:
```
one
two
three
four
five
```

## Future Enhancements
- Add support for diagonally placed words.
- Improve heuristics for faster backtracking.
- Implement a web-based interface for puzzle generation.

## License
This project is licensed under the MIT License.
