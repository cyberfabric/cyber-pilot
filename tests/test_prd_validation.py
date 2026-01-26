"""
Test PRD.md validation.

Tests PRD validation including actors, capabilities, and use cases.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.validation.artifacts.prd import validate_prd


class TestPRDStructure(unittest.TestCase):
    """Test PRD.md structure validation."""

    def test_minimal_valid_prd_passes(self):
        """Test minimal valid PRD.md passes."""
        text = """# PRD

## A. Vision

**Purpose**: Test application

First paragraph.

Second paragraph.

**Target Users**:
- Test users

**Key Problems Solved**:
- Testing

**Success Criteria**:
- Works

**Capabilities**:
- Do the thing

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: End user

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: Backend system

## C. Functional Requirements

#### User Management

**ID**: `fdd-app-fr-user-mgmt`

- The system MUST manage users.

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### Login Use Case

- **ID**: `fdd-app-usecase-login`
- **Actor**: `fdd-app-actor-user`
- **Preconditions**: User has account

1. User enters credentials
2. System validates credentials

- **Postconditions**: User is authenticated

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "PASS")

    def test_missing_section_b_fails(self):
        """Test missing Actors section fails."""
        text = """# PRD

## C. Functional Requirements

Content.

## D. Use Cases

Content.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        missing = [s["id"] for s in report["missing_sections"]]
        self.assertIn("B", missing)

    def test_missing_section_c_fails(self):
        """Test missing Capabilities section fails."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

First paragraph.

Second paragraph.

**Capabilities**:
- X

## B. Actors

- **ID**: `fdd-app-actor-user`

## D. Use Cases

Content.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        missing = [s["id"] for s in report["missing_sections"]]
        self.assertIn("C", missing)

    def test_missing_section_d_fails(self):
        """Test missing Use Cases section fails."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### CAP-001

- **ID**: `fdd-app-capability-test`
- **Purpose**: Test
- **Actors**: `fdd-app-actor-user`
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        missing = [s["id"] for s in report["missing_sections"]]
        self.assertIn("D", missing)

    def test_missing_section_a_fails(self):
        """Test missing Section A fails (D is optional)."""
        text = """# PRD

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### CAP-001

- **ID**: `fdd-app-capability-test`
- **Purpose**: Test
- **Actors**: `fdd-app-actor-user`
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        missing = [s["id"] for s in report["missing_sections"]]
        self.assertIn("A", missing)


class TestActorsValidation(unittest.TestCase):
    """Test actors section validation."""

    def test_actors_without_ids_fails(self):
        """Test actors section without IDs fails."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

## B. Actors

### Human Actors

#### BadActor

No ID field here!

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Test Cap

- **ID**: `fdd-app-capability-test`
- **Purpose**: Test
- **Actors**: `fdd-app-actor-system`

## D. Use Cases

- **ID**: `fdd-app-usecase-test`

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")

    def test_actors_with_proper_role_passes(self):
        """Test actors with Role field passes."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

First paragraph.

Second paragraph.

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### Administrator

- **ID**: `fdd-app-actor-admin`
- **Role**: Administrator

### System Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: Regular user

## C. Functional Requirements

#### Test Requirement

**ID**: `fdd-app-fr-test`

- The system MUST do the thing.

**Actors**: `fdd-app-actor-admin`

## D. Use Cases

#### Test Use Case

- **ID**: `fdd-app-usecase-test`
- **Actor**: `fdd-app-actor-admin`
- **Preconditions**: System is ready

1. Administrator performs action

- **Postconditions**: Action completed

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "PASS")


class TestCapabilitiesValidation(unittest.TestCase):
    """Test capabilities section validation."""

    def test_capability_without_id_fails(self):
        """Test capability without ID fails."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

## B. Actors

- **ID**: `fdd-app-actor-user`

## C. Capabilities

### FR-001: Test Requirement

**Purpose**: Some purpose

**Actors**: `fdd-app-actor-user`

No ID field!

## D. Use Cases

- **ID**: `fdd-app-usecase-test`
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")

    def test_capability_without_features_list_fails(self):
        """Test requirement without description fails."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

First paragraph.

Second paragraph.

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### FR-001

**ID**: `fdd-app-fr-test`

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`

**Actor**: `fdd-app-actor-user`

**Preconditions**: Ok

**Flow**:
1. Step

**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        req_errors = [e for e in report["issues"] if "functional requirement must include a description" in str(e.get("message", "")).lower()]
        self.assertGreater(len(req_errors), 0)

    def test_capability_without_actors_fails(self):
        """Test capability without Actors reference fails."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### CAP-001

**ID**: `fdd-app-capability-test`

**Purpose**: Test purpose

- Feature 1

No actors listed!
 
## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`

**Actor**: `fdd-app-actor-user`

**Preconditions**: Ok

**Flow**:
1. Step

**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        req_errors = [e for e in report["issues"] if "missing **actors** line" in str(e.get("message", "")).lower()]
        self.assertGreater(len(req_errors), 0)

    def test_capability_with_unknown_actor_fails(self):
        """Test capability referencing unknown actor fails."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### FR-001

**ID**: `fdd-app-fr-test`

- The system MUST do something.

**Actors**: `fdd-app-actor-unknown`

## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`

**Actor**: `fdd-app-actor-user`

**Preconditions**: Ok

**Flow**:
1. Step

**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        unknown_actor_errors = [e for e in report["issues"] if "unknown actor" in str(e.get("message", "")).lower()]
        self.assertGreater(len(unknown_actor_errors), 0)


class TestUseCasesValidation(unittest.TestCase):
    """Test use cases section validation."""

    def test_use_cases_without_ids_fails(self):
        """Test use cases without IDs fails."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Test Requirement

**ID**: `fdd-app-fr-test`

- The system MUST do the thing.

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### Bad Use Case

- **Actor**: `fdd-app-actor-user`
- **Preconditions**: None

1. Do something

- **Postconditions**: Done

No ID field here!
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        # Check for missing ID validation issue
        uc_errors = [e for e in report["issues"]
                    if "use case" in str(e).lower() and "**id**" in str(e).lower()]
        self.assertGreater(len(uc_errors), 0)

    def test_use_cases_with_proper_ids_passes(self):
        """Test use cases with proper IDs passes."""
        text = """# PRD

## A. Feature Context

**Purpose**: Test

First paragraph.

Second paragraph.

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Functional Requirements

#### Test Requirement

**ID**: `fdd-app-fr-test`

- The system MUST do the thing.

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### Login

- **ID**: `fdd-app-usecase-login`
- **Actor**: `fdd-app-actor-user`
- **Preconditions**: User has account

1. User enters credentials
2. System validates

- **Postconditions**: User is logged in

#### Logout

- **ID**: `fdd-app-usecase-logout`
- **Actor**: `fdd-app-actor-user`
- **Preconditions**: User is logged in

1. User clicks logout

- **Postconditions**: User is logged out

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "PASS")


class TestPlaceholders(unittest.TestCase):
    """Test placeholder detection."""

    def test_placeholders_detected(self):
        """Test that placeholders cause validation failure."""
        text = """# PRD

## B. Actors

- **ID**: `fdd-app-actor-user`
  **Role**: TODO: Define role

## C. Capabilities

### CAP-001

**ID**: `fdd-app-capability-test`

**Purpose**: TBD

**Actors**: `fdd-app-actor-user`

## D. Use Cases

- **ID**: `fdd-app-usecase-test`
  **Purpose**: FIXME: Add purpose
"""
        report = validate_prd(text)
        
        self.assertEqual(report["status"], "FAIL")
        self.assertGreater(len(report["placeholder_hits"]), 0)


class TestPRDAdditionalCoverage(unittest.TestCase):
    def test_unknown_top_level_section_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Cap

- **ID**: `fdd-app-capability-test`
- Feature 1
- **Actors**: `fdd-app-actor-user`

## Z. Extra

Extra
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(e.get("message") == "Unknown top-level sections" for e in report.get("errors", [])))

    def test_section_order_with_optional_sections_invalid(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

## E. Additional Context

Extra

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Cap

- **ID**: `fdd-app-capability-test`
- Feature 1
- **Actors**: `fdd-app-actor-user`
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(e.get("message") == "Section order invalid" for e in report.get("errors", [])))

    def test_actor_block_missing_metadata_and_capabilities_flagged(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

## B. Actors

### Human Actors

#### Empty Actor

#### Actor With Capabilities

- **ID**: `fdd-app-actor-user`
- **Role**: User
- **Capabilities**: must not be here

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Cap

- **ID**: `fdd-app-capability-test`
- Feature 1
- **Actors**: `fdd-app-actor-user`
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Actor block missing metadata" for i in report.get("issues", [])))
        self.assertTrue(any(i.get("message") == "Actor block must not list capabilities" for i in report.get("issues", [])))

    def test_section_a_missing_list_items_and_short_text_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

**Target Users**:
Users

**Key Problems Solved**:
Problems

**Success Criteria**:
Criteria

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Cap

- **ID**: `fdd-app-capability-test`
- Feature 1
- **Actors**: `fdd-app-actor-user`
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("must contain at least one list item" in str(i.get("message", "")) for i in report.get("issues", [])))

    def test_section_a_requires_two_paragraphs(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application
**Target Users**: Users
**Key Problems Solved**: Problems
**Success Criteria**: Criteria

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Cap

- **ID**: `fdd-app-capability-test`
- Feature 1
- **Actors**: `fdd-app-actor-user`
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Section A must contain at least 2 paragraphs" for i in report.get("issues", [])))

    def test_actor_id_not_first_metadata_line_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

## B. Actors

### Human Actors

#### User

- **Role**: User
- **ID**: `fdd-app-actor-user`

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Cap

- **ID**: `fdd-app-capability-test`
- Feature 1
- **Actors**: `fdd-app-actor-user`
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Actor ID must be first non-empty line after heading" for i in report.get("issues", [])))

    def test_duplicate_actor_ids_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

## B. Actors

### Human Actors

#### User A

- **ID**: `fdd-app-actor-user`
- **Role**: User

#### User B

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Cap

- **ID**: `fdd-app-capability-test`
- Feature 1
- **Actors**: `fdd-app-actor-user`
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Duplicate actor IDs" for i in report.get("issues", [])))

    def test_capability_block_missing_metadata_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Capabilities

#### Cap

## D. Use Cases

#### UC

- **ID**: `fdd-app-usecase-test`
- **Actor**: `fdd-app-actor-user`
- **Preconditions**: Ok

1. Step

- **Postconditions**: Ok
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Functional requirement block missing metadata" for i in report.get("issues", [])))

    def test_prd_more_branches_in_one_doc(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

## B. Actors

#### User

- **ID**: `fdd-app-actor-user`

## C. Capabilities

#### Cap

- **Purpose**: not first
- **ID**: `not-a-cap-id`
- **Actors**: `fdd-app-actor-user`

#### Cap2

## D. Use Cases

#### UC1

#### UC2

- **ID**: `fdd-app-usecase-test`
1. Step
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        issues = report.get("issues", [])

        self.assertTrue(any(i.get("message") == "Section B must be grouped by Human Actors and System Actors" for i in issues))
        self.assertTrue(any(i.get("message") == "Missing **Role** line" for i in issues))
        self.assertTrue(any(i.get("message") == "Functional requirement ID must be first non-empty line after heading" for i in issues))
        self.assertTrue(any(i.get("message") == "Invalid functional requirement ID format" for i in issues))
        self.assertTrue(any(i.get("message") == "Use case block missing metadata" for i in issues))
        self.assertTrue(any(i.get("message") == "Missing **Actor** line" for i in issues))
        self.assertTrue(any(i.get("message") == "Missing **Preconditions**" for i in issues))
        self.assertTrue(any(i.get("message") == "Missing **Postconditions**" for i in issues))

    def test_section_a_capabilities_inline_value_passes(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

First paragraph.

Second paragraph.

**Target Users**: Users

**Key Problems Solved**: Problems

**Success Criteria**: Criteria

**Capabilities**: Something

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Functional Requirements

#### Req

**ID**: `fdd-app-fr-req`

- The system MUST do something.

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`
**Actor**: `fdd-app-actor-user`
**Preconditions**: Ok
**Flow**:
1. Step
**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "PASS")

    def test_section_c_missing_actors_line_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

First paragraph.

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Functional Requirements

#### Req

**ID**: `fdd-app-fr-req`

- The system MUST do something.

## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`
**Actor**: `fdd-app-actor-user`
**Preconditions**: Ok
**Flow**:
1. Step
**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Functional requirement missing **Actors** line" for i in report.get("issues", [])))

    def test_section_c_duplicate_functional_requirement_ids_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

First paragraph.

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Functional Requirements

#### Req1

**ID**: `fdd-app-fr-dup`

- Desc

**Actors**: `fdd-app-actor-user`

#### Req2

**ID**: `fdd-app-fr-dup`

- Desc

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`
**Actor**: `fdd-app-actor-user`
**Preconditions**: Ok
**Flow**:
1. Step
**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Duplicate functional requirement IDs" for i in report.get("issues", [])))

    def test_section_d_missing_id_line_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

First paragraph.

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Functional Requirements

#### Req

**ID**: `fdd-app-fr-req`

- Desc

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### UC-001: X

**Actor**: `fdd-app-actor-user`
**Preconditions**: Ok
**Flow**:
1. Step
**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Missing **ID** line" for i in report.get("issues", [])))

    def test_section_d_unknown_fr_reference_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

First paragraph.

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Functional Requirements

#### Req

**ID**: `fdd-app-fr-req`

- Desc

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`
**Actor**: `fdd-app-actor-user`
**Preconditions**: Ok
**Flow**:
1. Ref `fdd-app-fr-missing`
**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Use case references unknown functional requirement ID" for i in report.get("issues", [])))

    def test_section_e_invalid_nfr_id_format_fails(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

First paragraph.

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Functional Requirements

#### Req

**ID**: `fdd-app-fr-req`

- Desc

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`
**Actor**: `fdd-app-actor-user`
**Preconditions**: Ok
**Flow**:
1. Step
**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `not-a-nfr-id`

- Authentication MUST be required.
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Invalid NFR ID format" for i in report.get("issues", [])))

    def test_section_f_invalid_and_duplicate_context_ids_fail(self) -> None:
        text = """# PRD

## A. Feature Context

**Purpose**: Test application

First paragraph.

Second paragraph.

**Target Users**:
- Users

**Key Problems Solved**:
- Problem

**Success Criteria**:
- Criteria

**Capabilities**:
- X

## B. Actors

### Human Actors

#### User

- **ID**: `fdd-app-actor-user`
- **Role**: User

### System Actors

#### System

- **ID**: `fdd-app-actor-system`
- **Role**: System

## C. Functional Requirements

#### Req

**ID**: `fdd-app-fr-req`

- Desc

**Actors**: `fdd-app-actor-user`

## D. Use Cases

#### UC-001: X

**ID**: `fdd-app-usecase-x`
**Actor**: `fdd-app-actor-user`
**Preconditions**: Ok
**Flow**:
1. Step
**Postconditions**: Ok

## E. Non-functional requirements

#### Security

**ID**: `fdd-app-nfr-security`

- Authentication MUST be required.

## F. Additional context

**ID**: `fdd-app-prd-context`

**ID**: `fdd-app-prd-context-note`

**ID**: `fdd-app-prd-context-note`
"""
        report = validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Invalid PRD context ID format" for i in report.get("issues", [])))
        self.assertTrue(any(i.get("message") == "Duplicate PRD context IDs" for i in report.get("issues", [])))


if __name__ == "__main__":
    unittest.main()
