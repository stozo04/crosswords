import unittest
from generate import CrosswordCreator
from crossword import Crossword, Variable


class TestCrossword(unittest.TestCase):

    def setUp(self):
        structure = "data/structure1.txt"
        words = "data/words1.txt"
        self.crossword = Crossword(structure, words)
        self.creator = CrosswordCreator(self.crossword)

    def test_enforce_node_consistency(self):
        self.creator.enforce_node_consistency()
        for var in self.creator.domains:
            for word in self.creator.domains[var]:
                self.assertEqual(len(word), var.length)

    def test_revise(self):
        var1 = Variable(0, 0, Variable.ACROSS, 3)
        var2 = Variable(0, 0, Variable.DOWN, 3)
        
        # Simple case: only one valid combination
        self.creator.domains[var1] = {"DOG", "CAT"}
        self.creator.domains[var2] = {"DAY"}  # Only word starting with D
        
        self.crossword.overlaps = {
            (var1, var2): (0, 0),
            (var2, var1): (0, 0)
        }
        
        revised = self.creator.revise(var1, var2)
        self.assertTrue(revised)
        self.assertEqual(self.creator.domains[var1], {"DOG"})  # Only word starting with D

    def test_revise_complex(self):
        var1 = Variable(0, 0, Variable.ACROSS, 4)
        var2 = Variable(0, 1, Variable.DOWN, 3)

        # Adding words that won't match the constraint
        self.creator.domains[var1] = {"BARK", "DARK", "PARK", "MARK", "BIRD", "BURN"}
        self.creator.domains[var2] = {"ART", "ARK", "ARM"}

        self.crossword.overlaps = {
            (var1, var2): (1, 0),
            (var2, var1): (0, 1)
        }

        print(f"Before revision:")
        print(f"var1 domain: {self.creator.domains[var1]}")
        print(f"var2 domain: {self.creator.domains[var2]}")
        print(f"Overlap: {self.crossword.overlaps[var1, var2]}")

        revised = self.creator.revise(var1, var2)
        
        print(f"\nAfter revision:")
        print(f"var1 domain: {self.creator.domains[var1]}")
        print(f"Revised: {revised}")

        self.assertTrue(revised)
        self.assertEqual(self.creator.domains[var1], {"BARK", "DARK", "PARK", "MARK"})

    def test_assignment_complete(self):
        assignment = {var: "TEST" for var in self.crossword.variables}
        self.assertTrue(self.creator.assignment_complete(assignment))

        incomplete = {var: "TEST" for var in list(self.crossword.variables)[:-1]}
        self.assertFalse(self.creator.assignment_complete(incomplete))

    def test_multiple_overlaps(self):
        var1 = Variable(0, 0, Variable.ACROSS, 4)
        var2 = Variable(0, 1, Variable.DOWN, 3)
        
        # Reset and set domains
        self.creator.domains = {}
        
        # Words where second letter is 'A' to match with var2
        self.creator.domains[var1] = {"DARK", "BARK"}
        self.creator.domains[var2] = {"ART", "ARK"}
        
        # Reset and set overlaps
        self.crossword.overlaps = {}
        self.crossword.overlaps = {
            (var1, var2): (1, 0),
            (var2, var1): (0, 1)
        }
        
        print("\nInitial state:")
        print(f"var1 domain: {self.creator.domains[var1]}")
        print(f"var2 domain: {self.creator.domains[var2]}")
        print(f"Overlap position: {self.crossword.overlaps[var1, var2]}")
        
        revised = self.creator.revise(var1, var2)
        
        print("\nAfter revision:")
        print(f"var1 domain: {self.creator.domains[var1]}")
        print(f"Revised: {revised}")
        
        revised = self.creator.revise(var1, var2)
        self.assertFalse(revised)  # No revision needed
        self.assertEqual(self.creator.domains[var1], {"DARK", "BARK"})

    def test_complex_overlap_filtering(self):
        var1 = Variable(0, 0, Variable.ACROSS, 4)
        var2 = Variable(0, 1, Variable.DOWN, 3)
        
        self.creator.domains = {}
        self.creator.domains[var1] = {"TEAM", "MILK", "DARK"}  # Only TEAM should remain
        self.creator.domains[var2] = {"EAT"}
        
        self.crossword.overlaps = {
            (var1, var2): (1, 0),
            (var2, var1): (0, 1)
        }
        
        revised = self.creator.revise(var1, var2)
        print(f"After revision - var1 domain: {self.creator.domains[var1]}")
        
        self.assertTrue(revised)
        self.assertEqual(self.creator.domains[var1], {"TEAM"})

    def test_empty_domains(self):
        var1 = Variable(0, 0, Variable.ACROSS, 4)
        var2 = Variable(0, 1, Variable.DOWN, 3)
        
        self.creator.domains = {}
        self.creator.domains[var1] = set()  # Empty domain
        self.creator.domains[var2] = {"EAT"}
        
        self.crossword.overlaps = {(var1, var2): (1, 0), (var2, var1): (0, 1)}
        revised = self.creator.revise(var1, var2)
        self.assertFalse(revised)  # Nothing to revise in empty domain

    def test_no_overlap(self):
        var1 = Variable(0, 0, Variable.ACROSS, 4)
        var2 = Variable(0, 1, Variable.DOWN, 3)
        
        self.creator.domains = {}
        self.creator.domains[var1] = {"TEAM"}
        self.creator.domains[var2] = {"EAT"}
        self.crossword.overlaps = {(var1, var2): None}
        
        revised = self.creator.revise(var1, var2)
        self.assertFalse(revised)  # No overlap means no revision needed


    def test_ac3_basic(self):
        # Create a simple crossword structure
        self.crossword.variables = set()
        var1 = Variable(0, 0, Variable.ACROSS, 4)
        var2 = Variable(0, 1, Variable.DOWN, 3)
        self.crossword.variables.add(var1)
        self.crossword.variables.add(var2)
        
        # Set domains and overlaps
        self.creator.domains = {
            var1: {"TEAM", "BEAM"},
            var2: {"EAT", "EEL"}
        }
        
        self.crossword.overlaps = {
            (var1, var2): (1, 0),
            (var2, var1): (0, 1)
        }
        
        success = self.creator.ac3()
        self.assertTrue(success)
        self.assertEqual(self.creator.domains[var1], {"TEAM", "BEAM"})
        self.assertEqual(self.creator.domains[var2], {"EAT", "EEL"})

    def test_ac3_empty_domain(self):
        # Similar setup for empty domain test
        self.crossword.variables = set()
        var1 = Variable(0, 0, Variable.ACROSS, 4)
        var2 = Variable(0, 1, Variable.DOWN, 3)
        self.crossword.variables.add(var1)
        self.crossword.variables.add(var2)
        
        self.creator.domains = {
            var1: {"MILK"},
            var2: {"EAT"}
        }
        
        self.crossword.overlaps = {
            (var1, var2): (1, 0),
            (var2, var1): (0, 1)
        }
        
        success = self.creator.ac3()
        self.assertFalse(success)

    def test_backtrack_simple(self):
        self.crossword.variables = set()
        var1 = Variable(0, 0, Variable.ACROSS, 3)
        var2 = Variable(0, 0, Variable.DOWN, 3)
        self.crossword.variables.update([var1, var2])
        
        self.creator.domains = {
            var1: {"CAT", "DOG"},
            var2: {"CAR", "CUP"}
        }
        
        self.crossword.overlaps = {
            (var1, var2): (0, 0),
            (var2, var1): (0, 0)
        }
        
        result = self.creator.backtrack({})
        self.assertIsNotNone(result)
        self.assertIn(result[var1], {"CAT"})  # Only CAT works with CAR/CUP
        self.assertIn(result[var2], {"CAR", "CUP"})  # Either is valid with CAT

    def test_backtrack_impossible(self):
        self.crossword.variables = set()
        var1 = Variable(0, 0, Variable.ACROSS, 3)
        var2 = Variable(0, 0, Variable.DOWN, 3)
        self.crossword.variables.update([var1, var2])
        
        self.creator.domains = {
            var1: {"DOG"},
            var2: {"CAT"}
        }
        
        self.crossword.overlaps = {
            (var1, var2): (0, 0),
            (var2, var1): (0, 0)
        }
        
        result = self.creator.backtrack({})
        self.assertIsNone(result)

    def test_backtrack_complex(self):
        self.crossword.variables = set()
        
        across = Variable(1, 0, Variable.ACROSS, 3)  
        down = Variable(0, 1, Variable.DOWN, 3)      
        
        self.crossword.variables.update([across, down])
        
        self.crossword.overlaps = {
            (across, down): (1, 0),
            (down, across): (0, 1)
        }
        
        # Fix: Use words that match at overlap point (A-A)
        self.creator.domains = {
            across: {"RAT"}, 
            down: {"ART"}  # Now first letter 'A' matches with second letter of "RAT"
        }
        
        print(f"\nTest setup:")
        print(f"Across word options: {self.creator.domains[across]}")
        print(f"Down word options: {self.creator.domains[down]}")
        print(f"Overlap: letter {self.crossword.overlaps[across, down][0]} of across")
        print(f"matches letter {self.crossword.overlaps[across, down][1]} of down")
        
        result = self.creator.backtrack({})
        print(f"Result: {result}")
        
        self.assertIsNotNone(result)
        self.assertEqual(result[across], "RAT")
        self.assertEqual(result[down], "ART")

    def test_backtrack_multiple_solutions(self):
        self.crossword.variables = set()
        
        across = Variable(1, 0, Variable.ACROSS, 3)  
        down = Variable(0, 1, Variable.DOWN, 3)      
        
        self.crossword.variables.update([across, down])
        self.crossword.overlaps = {
            (across, down): (1, 0),
            (down, across): (0, 1)
        }
        
        self.creator.domains = {
            across: {"RAT", "CAT", "BAT"}, 
            down: {"ART", "ACT", "APT"}
        }
        
        result = self.creator.backtrack({})
        self.assertIsNotNone(result)
        
        across_word = result[across]
        down_word = result[down]
        
        self.assertIn(across_word, {"RAT", "CAT", "BAT"})
        self.assertIn(down_word, {"ART", "ACT", "APT"})
        self.assertEqual(across_word[1], down_word[0])

    def test_backtrack_no_solution(self):
        self.crossword.variables = set()
        
        across = Variable(1, 0, Variable.ACROSS, 3)  
        down = Variable(0, 1, Variable.DOWN, 3)      
        
        self.crossword.variables.update([across, down])
        self.crossword.overlaps = {
            (across, down): (1, 0),
            (down, across): (0, 1)
        }
        
        self.creator.domains = {
            across: {"CAT", "BAT"}, 
            down: {"XYZ"}  # No overlap match possible
        }
        
        result = self.creator.backtrack({})
        self.assertIsNone(result)  # Should return None when no solution exists

if __name__ == "__main__":
    unittest.main()
