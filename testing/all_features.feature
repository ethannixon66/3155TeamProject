Feature: User Login
  Scenario: User clicks login button
    Given the user is on the login page
    And the username box is filled in
    And the password box is filled in
    And the username is valid
    And the password is valid
    Then the user will be logged in and brought to the home page

Feature: Edit Task
  Scenario: User wants to change task details
    Given the user is viewing a task
    When the user clicks the edit button
    Then the user can see an editable text field with the current task inside
  Scenario: User has submitted an edit
    When the user hits the submit button for an edit
    Then the edit is pushed to the database
    And the user can view the updated task

Feature: View Task
  Scenario: User wants to view task details
    Given the user is on the board's Homepage.
    When the user clicks on a task
    Then the user can see the task details

Feature: Add Task
  Scenario: User wants to add a new task to the board.
    Given the User is on the boards Homepage.
    When the user clicks on the add task button
    And user names the task
    And the task name is unique
    And user clicks the submit 
    Then a new task is added to the board.
