import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        # Initialize empty grid of None values
        height = self.crossword.height
        width = self.crossword.width
        grid = [[None for col in range(width)] 
                for row in range(height)]
        
        # Fill in letters for each word
        for variable, word in assignment.items():
            # Get starting position
            start_row = variable.i
            start_col = variable.j
            
            # Place each letter
            for letter_index in range(len(word)):
                letter = word[letter_index]
                
                # Calculate position based on direction
                if variable.direction == Variable.DOWN:
                    row = start_row + letter_index
                    col = start_col
                else:  # ACROSS
                    row = start_row
                    col = start_col + letter_index
                    
                grid[row][col] = letter
                
        return grid

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            # Create set of words that match this variable's length
            valid_words = set()
           
            # Check each word in the domain
            for word in self.domains[variable]:
                if len(word) == variable.length:
                    valid_words.add(word)
                    
            # Update domain to only contain valid words
            self.domains[variable] = valid_words

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Track if we removed any values
        revised = False
        
        # Get the overlap indices between variables x and y
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False
            
        x_index, y_index = overlap
        
        # Check each word in x's domain
        words_to_remove = set()
        for x_word in self.domains[x]:
            # Look for any word in y's domain that matches at overlap
            found_match = False
            for y_word in self.domains[y]:
                if x_word[x_index] == y_word[y_index]:
                    found_match = True
                    break
                    
            # If no match found, mark word for removal
            if not found_match:
                words_to_remove.add(x_word)
                revised = True
        
        # Remove incompatible words from x's domain
        self.domains[x] -= words_to_remove
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If no arcs provided, start with all variable pairs that overlap
        if arcs is None:
            arcs = []
            for var in self.crossword.variables:
                for neighbor in self.crossword.neighbors(var):
                    arcs.append((var, neighbor))
        
        # Keep track of arcs to process
        queue = arcs.copy()
        
        # Process arcs until queue is empty
        while queue:
            # Get next arc to process
            current_var, neighbor = queue.pop(0)
            
            # If we had to revise current_var's domain
            if self.revise(current_var, neighbor):
                # Check if we eliminated all possible values
                if not self.domains[current_var]:
                    return False
                    
                # Add arcs for all other neighbors of current_var
                # This ensures changes propagate through the graph
                for other_neighbor in self.crossword.neighbors(current_var) - {neighbor}:
                    queue.append((other_neighbor, current_var))
                    
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # 1. self.crossword.variables contains all variables that need values
        # 2. assignment is a dictionary where:
        #    - keys are Variable objects
        #    - values are the words assigned to those variables
        
        # Check if each variable from the crossword is present in our assignment
        for var in self.crossword.variables:
            if var not in assignment:
                return False
                
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check 1: No duplicate words
        used_words = []
        for variable in assignment:
            word = assignment[variable]
            # If we've seen this word before, puzzle is invalid
            if word in used_words:
                return False
            used_words.append(word)
        
        # Check 2: All words are correct length
        for variable in assignment:
            word = assignment[variable]
            required_length = variable.length
            if len(word) != required_length:
                return False
        
        # Check 3: Overlapping letters match
        for variable in assignment:
            # Look at each neighbor of current variable
            for neighbor in self.crossword.neighbors(variable):
                # Only check if neighbor has been assigned a word
                if neighbor in assignment:
                    # Get where these variables overlap
                    overlap = self.crossword.overlaps[variable, neighbor]
                    
                    # Skip if no overlap
                    if overlap is None:
                        continue
                        
                    # Get the position of overlapping letter in each word
                    my_letter_pos, neighbor_letter_pos = overlap
                    
                    # Get the actual words
                    my_word = assignment[variable]
                    neighbor_word = assignment[neighbor]
                    
                    # Check if letters match at overlap point
                    if my_word[my_letter_pos] != neighbor_word[neighbor_letter_pos]:
                        return False
        
        # If we passed all checks, assignment is valid
        return True

    def order_domain_values(self, var, assignment):
        """Order possible words for a variable from least to most constraining."""
        
        # If no valid words exist, return empty list
        if not self.domains[var]:
            return []
   
        def count_conflicts(word):
            """Count how many words this choice would eliminate from neighbors."""
            conflict_count = 0
            
            # Check each neighboring variable
            for neighbor in self.crossword.neighbors(var):
                # Skip neighbors that already have words assigned
                if neighbor in assignment:
                    continue
                    
                # Get where these variables overlap    
                overlap = self.crossword.overlaps[var, neighbor]
                my_letter_pos, neighbor_letter_pos = overlap
                
                # For each possible word the neighbor could use
                for neighbor_word in self.domains[neighbor]:
                    # If letters don't match at overlap, count a conflict
                    if word[my_letter_pos] != neighbor_word[neighbor_letter_pos]:
                        conflict_count += 1
            return conflict_count  
        # Sort words by how many conflicts they cause (least first)
        return sorted(self.domains[var], key=count_conflicts)

    def select_unassigned_variable(self, assignment):
        """Choose which empty variable to fill in next using smart heuristics."""
        
        # Get list of variables that don't have words yet
        empty_variables = []
        for var in self.crossword.variables:
            if var not in assignment:
                empty_variables.append(var)
        
        # If no empty variables left, return None        
        if not empty_variables:
            return None
            
        # First try picking variable with fewest word options left (MRV)
        def count_remaining_words(var):
            return len(self.domains[var])
            
        best_variables = sorted(empty_variables, key=count_remaining_words)
        fewest_words = len(self.domains[best_variables[0]])
        
        # Get all variables tied for fewest remaining words
        tied_variables = []
        for var in best_variables:
            if len(self.domains[var]) == fewest_words:
                tied_variables.append(var)
                
        # If only one variable has fewest words, use it        
        if len(tied_variables) == 1:
            return tied_variables[0]
            
        # Break ties by choosing variable with most neighbors
        def count_neighbors(var):
            return len(self.crossword.neighbors(var))
        return max(tied_variables, key=count_neighbors)

    def backtrack(self, assignment):
        """
        Try to complete the crossword using recursive backtracking search.
        """
        
        # If every variable has a word, we've solved it
        if self.assignment_complete(assignment):
            return assignment
        
        # Choose a variable to fill in    
        var = self.select_unassigned_variable(assignment)
        
        # Try each possible word for this variable
        for word in self.order_domain_values(var, assignment):
            # Tentatively assign this word
            assignment[var] = word
            
            # If assignment still valid, recursively try to fill rest
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                    
            # If we get here, word didn't work - remove it
            assignment.pop(var)
        
        # If no words worked, signal failure
        return None
    
def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
