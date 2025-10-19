"""
Chores Module - API Test Script
Tests all backend functionality via HTTP requests to the FastAPI server.

Requirements:
    pip install httpx

Usage:
    1. Start your FastAPI server: uvicorn backend.main:app --reload
    2. Run this script: python test_chores_api.py
"""

import httpx
from datetime import datetime, timedelta


class TestColors:
    """ANSI color codes for pretty output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{TestColors.HEADER}{TestColors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{TestColors.ENDC}\n")


def print_success(text):
    print(f"{TestColors.OKGREEN}✓ {text}{TestColors.ENDC}")


def print_error(text):
    print(f"{TestColors.FAIL}✗ {text}{TestColors.ENDC}")


def print_info(text):
    print(f"{TestColors.OKCYAN}ℹ {text}{TestColors.ENDC}")


def print_warning(text):
    print(f"{TestColors.WARNING}⚠ {text}{TestColors.ENDC}")


def print_response(response, show_body=True):
    """Print HTTP response details"""
    status_color = TestColors.OKGREEN if response.status_code < 400 else TestColors.FAIL
    print(f"{status_color}  Status: {response.status_code}{TestColors.ENDC}")
    if show_body and response.text:
        try:
            print(f"  Response: {response.json()}")
        except:
            print(f"  Response: {response.text[:200]}")


class ChoresAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0, follow_redirects=True)
        self.age_groups = []
        self.members = []
        self.chores = []
        
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def test_health_check(self):
        """Test that the API is running"""
        print_header("HEALTH CHECK")
        try:
            response = self.client.get("/")
            print_success(f"API is running at {self.base_url}")
            print_response(response, show_body=False)
            return True
        except httpx.ConnectError:
            print_error(f"Cannot connect to API at {self.base_url}")
            print_warning("Make sure your FastAPI server is running:")
            print_warning("  uvicorn backend.main:app --reload")
            return False
    
    def test_age_groups(self):
        """Test Age Group CRUD operations"""        
        # Clean up existing test data first
        response = self.client.get("/api/chores/age-groups")
        if response.status_code == 200:
            existing_groups = response.json()
            for group in existing_groups:
                if group['name'] in ['Young Child', 'Teen', 'Older Teen', 'Adult']:
                    self.client.delete(f"/api/chores/age-groups/{group['id']}")
                    
        print_header("TEST 1: Age Group Operations")
        
        # Create age groups
        age_groups_data = [
            {"name": "Young Child", "min_age": 5, "max_age": 10, "default_weekly_cap": 25},
            {"name": "Teen", "min_age": 11, "max_age": 15, "default_weekly_cap": 27},
            {"name": "Older Teen", "min_age": 16, "max_age": 17, "default_weekly_cap": 30},
            {"name": "Adult", "min_age": 18, "max_age": 100, "default_weekly_cap": 30},
        ]
        
        print_info("Creating age groups...")
        for data in age_groups_data:
            response = self.client.post("/api/chores/age-groups", json=data)
            print_response(response)
            
            if response.status_code == 201:
                age_group = response.json()
                self.age_groups.append(age_group)
                print_success(f"Created: {age_group['name']} ({age_group['min_age']}-{age_group['max_age']} years, {age_group['default_weekly_cap']} pts/week)")
            else:print_error(f"Failed to create age group: {data['name']}")
        
        # Get all age groups
        print_info("\nRetrieving all age groups...")
        response = self.client.get("/api/chores/age-groups")
        print_response(response)
        
        if response.status_code == 200:
            groups = response.json()
            print_success(f"Retrieved {len(groups)} age groups")
        
        # Get single age group
        if self.age_groups:
            print_info("\nRetrieving single age group by ID...")
            response = self.client.get(f"/api/chores/age-groups/{self.age_groups[0]['id']}")
            print_response(response)
            
            if response.status_code == 200:
                print_success("Successfully retrieved age group")
        
        return len(self.age_groups) > 0
    
    def test_family_members(self):
        """Test Family Member CRUD and point tracking"""
        print_header("TEST 2: Family Member Operations")
        
        if not self.age_groups:
            print_error("No age groups available. Run age group tests first.")
            return False
        
        # Create family members
        members_data = [
            {"name": "Seren", "age": 8, "age_group_id": self.age_groups[0]['id']},
            {"name": "Torin", "age": 9, "age_group_id": self.age_groups[0]['id']},
            {"name": "Evlin", "age": 13, "age_group_id": self.age_groups[1]['id']},
            {"name": "Aedan", "age": 16, "age_group_id": self.age_groups[2]['id'], "weekly_points_cap_override": 29},
        ]
        
        print_info("Creating family members...")
        for data in members_data:
            response = self.client.post("/api/chores/members", json=data)
            print_response(response)
            
            if response.status_code == 201:
                member = response.json()
                self.members.append(member)
                cap = member.get('weekly_points_cap') or self.age_groups[0]['weekly_points_cap']
                print_success(f"Created: {member['name']} (Age {member['age']}, Cap: {cap} pts/week)")
            else:
                print_error(f"Failed to create member: {data['name']}")
        
        # Get all members
        print_info("\nRetrieving all family members...")
        response = self.client.get("/api/chores/members")
        print_response(response)
        
        if response.status_code == 200:
            members = response.json()
            print_success(f"Retrieved {len(members)} family members")
        
        # Test Aedan's custom cap
        if len(self.members) >= 4:
            aedan = self.members[3]
            print_info(f"\nVerifying Aedan's custom weekly cap...")
            response = self.client.get(f"/api/chores/members/{aedan['id']}")
            
            if response.status_code == 200:
                member_data = response.json()
                cap = member_data.get('weekly_points_cap_override', member_data.get('weekly_points_cap'))
                if cap == 29:
                    print_success(f"Aedan's custom cap verified: {cap} points")
                else:
                    print_warning(f"Aedan's cap is {cap}, expected 29")
        
        return len(self.members) > 0
    
    def test_chore_creation(self):
        """Test Chore CRUD operations"""
        print_header("TEST 3: Chore Creation & Management")
        
        if not self.members:
            print_error("No family members available. Run member tests first.")
            return False
        
        # Create various chores
        chores_data = [
            {
                "title": "Take out trash",
                "points": 1,
                "category": "cleaning",
                "priority": "medium",
                "assigned_to_id": self.members[0]['id'],
                "created_by_id": self.members[3]['id'] if len(self.members) >= 4 else self.members[0]['id'],
            },
            {
                "title": "Vacuum living room",
                "points": 2,
                "category": "cleaning",
                "priority": "high",
                "assigned_to_id": self.members[1]['id'] if len(self.members) >= 2 else self.members[0]['id'],
                "created_by_id": self.members[3]['id'] if len(self.members) >= 4 else self.members[0]['id'],
                "recurrence_pattern": "weekly",
            },
            {
                "title": "Wash dishes",
                "points": 2,
                "category": "cooking",
                "priority": "high",
                "assigned_to_id": self.members[2]['id'] if len(self.members) >= 3 else self.members[0]['id'],
                "created_by_id": self.members[3]['id'] if len(self.members) >= 4 else self.members[0]['id'],
                "recurrence_pattern": "daily",
            },
            {
                "title": "Mow lawn",
                "points": 3,
                "category": "yard",
                "priority": "low",
                "assigned_to_id": self.members[3]['id'] if len(self.members) >= 4 else self.members[0]['id'],
                "created_by_id": self.members[3]['id'] if len(self.members) >= 4 else self.members[0]['id'],
                "due_date": (datetime.now() + timedelta(days=7)).date().isoformat(),
            },
        ]
        
        print_info("Creating chores...")
        for data in chores_data:
            response = self.client.post("/api/chores", json=data)
            print_response(response)
            
            if response.status_code == 201:
                chore = response.json()
                self.chores.append(chore)
                recurrence = f" ({chore.get('recurrence_pattern', 'NONE')})" if chore.get('recurrence_pattern') else ""
                print_success(f"Created: {chore['title']} - {chore['points']} pts{recurrence}")
            else:
                print_error(f"Failed to create chore: {data['title']}")
        
        # Test filtering
        print_info("\nTesting chore filters...")
        
        # Filter by status
        response = self.client.get("/api/chores?status=PENDING")
        if response.status_code == 200:
            pending = response.json()
            print_info(f"  Pending chores: {len(pending)}")
        
        # Filter by category
        response = self.client.get("/api/chores?category=CLEANING")
        if response.status_code == 200:
            cleaning = response.json()
            print_info(f"  Cleaning chores: {len(cleaning)}")
        
        # Filter by assigned member
        if self.members:
            response = self.client.get(f"/api/chores?assigned_to_id={self.members[0]['id']}")
            if response.status_code == 200:
                member_chores = response.json()
                print_info(f"  {self.members[0]['name']}'s chores: {len(member_chores)}")
        
        return len(self.chores) > 0
    
    def test_chore_completion(self):
        """Test chore completion and weekly cap enforcement"""
        print_header("TEST 4: Chore Completion & Weekly Caps")
        
        if not self.chores or not self.members:
            print_error("Need chores and members for completion tests")
            return False
        
        # Test normal completion
        print_info("Testing normal chore completion...")
        member = self.members[0]
        chore = self.chores[0]
        
        # Get member's current points
        response = self.client.get(f"/api/chores/members/{member['id']}")
        if response.status_code == 200:
            before_data = response.json()
            before_points = before_data.get('weekly_points', 0)
        
        # Complete the chore
        completion_data = {
            "chore_id": chore['id'],
            "completed_by_id": member['id']
        }
        response = self.client.post("/api/chores/completions", json=completion_data)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"{member['name']} completed '{chore['title']}' (+{chore['points']} pts)")
            print_info(f"  Message: {result.get('message', 'Success')}")
            
            # Check updated points
            response = self.client.get(f"/api/chores/members/{member['id']}")
            if response.status_code == 200:
                after_data = response.json()
                after_points = after_data.get('weekly_points', 0)
                print_info(f"  Points: {before_points} → {after_points}")
                print_success(f"  Total points: {after_data.get('total_points', 0)}")
                print_success(f"  Monthly points: {after_data.get('monthly_points', 0)}")
        
        # Test weekly cap enforcement
        print_info("\nTesting weekly cap enforcement...")
        test_member = self.members[0]
                
        # Create a high-point chore to test cap
        high_point_chore_data = {
            "title": "Test chore for cap enforcement",
            "points": 20,
            "category": "CLEANING",
            "priority": "LOW",
            "assigned_to_id": test_member['id'],
            "created_by_id": self.members[3]['id'] if len(self.members) >= 4 else test_member['id'],
        }
        
        response = self.client.post("/api/chores", json=high_point_chore_data)
        if response.status_code == 201:
            test_chore = response.json()
            
            # Try to complete it
            completion_data = {
                "chore_id": test_chore['id'],
                "completed_by_id": test_member['id']
            }
            response = self.client.post("/api/chores/completions", json=completion_data)
            print_response(response)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print_success("  Chore completed successfully")
                else:
                    print_warning(f"  Cap enforcement working: {result.get('message')}")
            elif response.status_code == 400:
                print_success("  ✓ Cap enforcement prevented completion (HTTP 400)")
        
        return True
    
    def test_dashboard(self):
        """Test dashboard endpoint"""
        print_header("TEST 5: Dashboard Data")
        
        print_info("Retrieving dashboard data...")
        response = self.client.get("/api/chores/dashboard")
        print_response(response)
        
        if response.status_code == 200:
            dashboard = response.json()
            print_success("Dashboard data retrieved successfully")
            print_info(f"  Total members: {len(dashboard.get('members', []))}")
            print_info(f"  Total chores: {dashboard.get('total_chores', 0)}")
            print_info(f"  Pending chores: {dashboard.get('pending_chores', 0)}")
            print_info(f"  Completed today: {dashboard.get('completed_today', 0)}")
            return True
        
        return False
    
    def test_completion_history(self):
        """Test completion history endpoint"""
        print_header("TEST 6: Completion History")
        
        print_info("Retrieving completion history...")
        response = self.client.get("/api/chores/completions")
        print_response(response)
        
        if response.status_code == 200:
            completions = response.json()
            print_success(f"Retrieved {len(completions)} completion records")
            
            for completion in completions[:5]:  # Show first 5
                print_info(f"  ✓ {completion.get('family_member', {}).get('name', 'Unknown')} completed '{completion.get('chore_title', 'Unknown')}'")
                print_info(f"      Points: {completion.get('points_earned', 0)}, At: {completion.get('completed_at', 'Unknown')}")
            
            return True
        
        return False


def run_all_tests():
    """Run complete test suite"""
    print_header("CHORES MODULE - API TEST SUITE")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = ChoresAPITester()
    
    try:
        # Health check first
        if not tester.test_health_check():
            return
        
        # Run tests in sequence
        tests = [
            ("Age Groups", tester.test_age_groups),
            ("Family Members", tester.test_family_members),
            ("Chore Creation", tester.test_chore_creation),
            ("Chore Completion", tester.test_chore_completion),
            ("Dashboard", tester.test_dashboard),
            ("Completion History", tester.test_completion_history),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
                    print_warning(f"{test_name} test had issues")
            except Exception as e:
                failed += 1
                print_error(f"{test_name} test failed with error: {e}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print_header("TEST SUMMARY")
        print_success(f"Passed: {passed}/{len(tests)} tests ✓")
        if failed > 0:
            print_warning(f"Failed: {failed}/{len(tests)} tests")
        
        print_info("\nNext steps:")
        print_info("  1. Review any failed tests above")
        print_info("  2. Check your database for created records")
        print_info("  3. Test additional edge cases manually")
        print_info("  4. Begin frontend development")
        
    except KeyboardInterrupt:
        print_warning("\nTests interrupted by user")
    finally:
        tester.close()
        print_info(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_all_tests()