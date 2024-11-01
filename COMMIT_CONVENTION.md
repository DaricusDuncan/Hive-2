# Commit Message Convention

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

## Format
Each commit message consists of:
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools
- `ci`: Changes to CI configuration files and scripts
- `revert`: Reverts a previous commit

### Scope
The scope provides additional contextual information and should be one of:
- `auth`: Authentication related changes
- `api`: API endpoints and resources
- `db`: Database related changes
- `security`: Security related changes
- `test`: Test related changes
- `config`: Configuration changes
- `docs`: Documentation changes

### Description
- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No dot (.) at the end

### Examples
```
feat(auth): add refresh token blacklisting
fix(api): resolve rate limiting issue in user endpoints
docs(readme): update API documentation with new endpoints
test(auth): add integration tests for login flow
refactor(db): optimize user query performance
style(api): format code according to PEP 8
chore(deps): update dependencies to latest versions
```

### Breaking Changes
When a commit includes a breaking change, it must be indicated in the footer with a `BREAKING CHANGE:` prefix:
```
feat(api): change user authentication endpoint

BREAKING CHANGE: The authentication endpoint now requires an additional 'client_id' parameter
```

## Git Hooks Setup
To ensure commit message compliance, consider setting up Git hooks that validate commit messages against this convention.

## Benefits
- Automatically generating CHANGELOGs
- Determining semantic version bumps
- Communicating the nature of changes to teammates and stakeholders
- Making it easier for people to contribute to the project
