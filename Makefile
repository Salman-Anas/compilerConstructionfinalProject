# CS471L Mini Compiler Project Makefile
# Variables
PYTHON = python3
MAIN = src/main.py
TEST_DIR = test
OUTPUT_DIR = output
GROUP_NUM = 1 # Change this to your actual group number
ROLL_NUM = 2023-CS-06
ZIP_NAME = CS471L_Project_Group$(GROUP_NUM)_$(ROLL_NUM).zip

# Default target: Run the compiler on a sample test file
run:
	@echo "Running compiler on basic test file..."
	mkdir -p $(OUTPUT_DIR)
	$(PYTHON) $(MAIN) $(TEST_DIR)/basic1.pas > $(OUTPUT_DIR)/basic1_output.txt
	@echo "Output saved to $(OUTPUT_DIR)/basic1_output.txt"
	cat $(OUTPUT_DIR)/basic1_output.txt

# Run all test files
test-all:
	@echo "Testing all sample programs..."
	mkdir -p $(OUTPUT_DIR)
	$(PYTHON) $(MAIN) $(TEST_DIR)/basic1.pas > $(OUTPUT_DIR)/basic1_output.txt
	$(PYTHON) $(MAIN) $(TEST_DIR)/math2.pas > $(OUTPUT_DIR)/math2_output.txt
	$(PYTHON) $(MAIN) $(TEST_DIR)/errorTest.pas > $(OUTPUT_DIR)/error_output.txt
	$(PYTHON) $(MAIN) $(TEST_DIR)/complex_math.pas > $(OUTPUT_DIR)/complex_math_output.txt
	$(PYTHON) $(MAIN) $(TEST_DIR)/stress_recovery.pas > $(OUTPUT_DIR)/stress_recovery_output.txt
	$(PYTHON) $(MAIN) $(TEST_DIR)/lexical_edge.pas > $(OUTPUT_DIR)/lexical_edge_output.txt
	@echo "All outputs saved to $(OUTPUT_DIR)/"

# Package the project for submission
zip:
	@echo "Packaging project into $(ZIP_NAME)..."
	zip -r $(ZIP_NAME) src/ docs/ test/ output/ Makefile README.md
	@echo "Submission package ready!"

# Clean up generated files
clean:
	rm -f $(OUTPUT_DIR)/*.txt
	rm -f *.zip
	s