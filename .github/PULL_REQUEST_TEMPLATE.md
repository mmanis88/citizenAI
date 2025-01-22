---
name: Pull Request
about: Describe your changes
title: ""
labels: ""
assignees: ""
---

**Description**
A clear and concise description of what the pull request does.

**Related Issue**
Link to any related issues or pull requests. (e.g., `Fixes #123`)

## Comments

[These are some optional comments that we might want to share with the reviewers and will make their job a little easier. This section is mandatory when the risk level is not low]

- This pull request affects also the global state management mechanism regarding session. This means that all views that interact with it might be affected too
- Please check thoroughly my work regarding tests suites because this is the first time I wrote some tests with Testing Library so I have some doubts about the end-result

## Changes

[This is a list with all the changes implemented in this pull request]

- Updated the login mechanism client-side
- Added extra logic in the session management in global store
- Added validation rule for the email and the password fields
- Added UI tests to test various scenarios

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Checklist**

- [ ] I have read the [contributing guidelines](CONTRIBUTING.md).
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] I have added tests that prove my fix is effective
- [ ] New and existing tests pass locally with my changes

**Screenshots (if applicable)**
Add screenshots or screen recordings to help explain your changes.

**Additional Notes**
Any additional notes or information that may be helpful for the reviewers.

**Implementation Details (if applicable)**

- Outline any major decisions or design considerations.
- Describe any changes to the codebase structure or dependencies.

**Deployment Instructions (if applicable)**

- Any specific instructions or considerations for deploying this change.
