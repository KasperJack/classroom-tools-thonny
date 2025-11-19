#!/usr/bin/env python3
"""
TOML-based Function Test Runner
Tests Python functions using simple TOML test definitions
"""

import sys
import os
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # pip install tomli
    except ImportError:
        print("ERROR: Need tomllib (Python 3.11+) or tomli (pip install tomli)")
        sys.exit(1)


class Colors:
    """ANSI color codes for pretty output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    @staticmethod
    def disable():
        """Disable colors (for Windows or piped output)"""
        Colors.GREEN = Colors.RED = Colors.YELLOW = ''
        Colors.BLUE = Colors.CYAN = Colors.BOLD = Colors.RESET = ''


class TestRunner:
    def __init__(self, code_file, test_file):
        self.code_file = code_file
        self.test_file = test_file
        self.namespace = {}
        self.passed = 0
        self.failed = 0
        
    def load_code(self):
        """Load and execute the user's code"""
        try:
            with open(self.code_file, 'r', encoding='utf-8') as f:
                code = f.read()
            exec(code, self.namespace)
            return True
        except FileNotFoundError:
            print(f"{Colors.RED}✗ Error:{Colors.RESET} Code file not found: {self.code_file}")
            return False
        except SyntaxError as e:
            print(f"{Colors.RED}✗ Syntax Error:{Colors.RESET} {e}")
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ Error loading code:{Colors.RESET} {e}")
            return False
    
    def load_tests(self):
        """Load test definitions from TOML file"""
        try:
            with open(self.test_file, 'rb') as f:
                return tomllib.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}✗ Error:{Colors.RESET} Test file not found: {self.test_file}")
            return None
        except Exception as e:
            print(f"{Colors.RED}✗ Error parsing TOML:{Colors.RESET} {e}")
            return None
    
    def format_value(self, value):
        """Format a value for display"""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            return '[' + ', '.join(self.format_value(v) for v in value) + ']'
        elif isinstance(value, dict):
            items = [f'{k}: {self.format_value(v)}' for k, v in value.items()]
            return '{' + ', '.join(items) + '}'
        else:
            return str(value)
    
    def format_args(self, args):
        """Format function arguments for display"""
        return ', '.join(self.format_value(arg) for arg in args)
    
    def run_function_test(self, test_num, test):
        """Run a single function test"""
        function_name = test.get('function')
        args = test.get('args', [])
        expected = test.get('returns')
        description = test.get('description', '')
        
        # Check if function exists
        if function_name not in self.namespace:
            self.failed += 1
            print(f"\n{Colors.RED}✗ Test {test_num} FAILED{Colors.RESET}")
            if description:
                print(f"  {Colors.CYAN}{description}{Colors.RESET}")
            print(f"  {Colors.YELLOW}Function '{function_name}' not found{Colors.RESET}")
            return
        
        func = self.namespace[function_name]
        
        # Run the function
        try:
            result = func(*args)
            
            # Check result
            if result == expected:
                self.passed += 1
                print(f"\n{Colors.GREEN}✓ Test {test_num} PASSED{Colors.RESET}")
                if description:
                    print(f"  {Colors.CYAN}{description}{Colors.RESET}")
                print(f"  {Colors.BOLD}Call:{Colors.RESET} {function_name}({self.format_args(args)})")
                print(f"  {Colors.BOLD}Returned:{Colors.RESET} {self.format_value(result)}")
            else:
                self.failed += 1
                print(f"\n{Colors.RED}✗ Test {test_num} FAILED{Colors.RESET}")
                if description:
                    print(f"  {Colors.CYAN}{description}{Colors.RESET}")
                print(f"  {Colors.BOLD}Call:{Colors.RESET} {function_name}({self.format_args(args)})")
                print(f"  {Colors.BOLD}Expected:{Colors.RESET} {self.format_value(expected)}")
                print(f"  {Colors.BOLD}Got:{Colors.RESET} {self.format_value(result)}")
        
        except Exception as e:
            self.failed += 1
            print(f"\n{Colors.RED}✗ Test {test_num} FAILED{Colors.RESET}")
            if description:
                print(f"  {Colors.CYAN}{description}{Colors.RESET}")
            print(f"  {Colors.BOLD}Call:{Colors.RESET} {function_name}({self.format_args(args)})")
            print(f"  {Colors.YELLOW}Error:{Colors.RESET} {e}")
    
    def run_all_tests(self):
        """Run all tests and display results"""
        # Print header
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Running Tests{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"Code file: {Colors.CYAN}{self.code_file}{Colors.RESET}")
        print(f"Test file: {Colors.CYAN}{self.test_file}{Colors.RESET}")
        
        # Load code
        print(f"\n{Colors.BOLD}Loading code...{Colors.RESET}")
        if not self.load_code():
            return False
        print(f"{Colors.GREEN}✓ Code loaded successfully{Colors.RESET}")
        
        # Load tests
        print(f"\n{Colors.BOLD}Loading tests...{Colors.RESET}")
        tests = self.load_tests()
        if not tests:
            return False
        
        test_list = tests.get('test', [])
        if not test_list:
            print(f"{Colors.YELLOW}⚠ Warning:{Colors.RESET} No tests found in {self.test_file}")
            return False
        
        print(f"{Colors.GREEN}✓ Found {len(test_list)} test(s){Colors.RESET}")
        
        # Run tests
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Results{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        
        for i, test in enumerate(test_list, 1):
            self.run_function_test(i, test)
        
        # Print summary
        total = self.passed + self.failed
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"Total tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Great job!{Colors.RESET}")
        else:
            percentage = (self.passed / total * 100) if total > 0 else 0
            print(f"\nScore: {percentage:.1f}%")
        
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
        
        return self.failed == 0


def main():
    """Main entry point"""
    if len(sys.argv) != 3:
        print(f"{Colors.BOLD}Usage:{Colors.RESET} python test_runner.py <code_file.py> <tests.toml>")
        print(f"\nExample:")
        print(f"  python test_runner.py solution.py tests.toml")
        sys.exit(1)
    
    code_file = sys.argv[1]
    test_file = sys.argv[2]
    
    # Disable colors on Windows if not supported
    if os.name == 'nt' and not os.environ.get('ANSICON'):
        Colors.disable()
    
    runner = TestRunner(code_file, test_file)
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
