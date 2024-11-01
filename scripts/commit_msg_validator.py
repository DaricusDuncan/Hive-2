import re
import sys

def validate_commit_message(commit_msg_file):
    with open(commit_msg_file, 'r') as f:
        commit_msg = f.read().strip()

    # Conventional Commits pattern
    pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|ci|revert)(\([a-z-]+\))?: .{1,72}$'
    
    # Check first line (subject)
    subject = commit_msg.split('\n')[0]
    
    if not re.match(pattern, subject):
        print('Error: Commit message does not follow the conventional commits format.')
        print('Format: <type>(<scope>): <description>')
        print('Example: feat(auth): add refresh token functionality')
        print('\nValid types: feat, fix, docs, style, refactor, perf, test, chore, ci, revert')
        print('Valid scopes: auth, api, db, security, test, config, docs')
        sys.exit(1)

    # Check max line length
    for line in commit_msg.split('\n'):
        if len(line) > 72:
            print('Error: Commit message lines should not exceed 72 characters')
            sys.exit(1)

    # Check if body is separated by blank line if present
    lines = commit_msg.split('\n')
    if len(lines) > 1 and lines[1] != '':
        print('Error: Commit message body should be separated from subject by a blank line')
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Error: Commit message file path is required')
        sys.exit(1)
    
    validate_commit_message(sys.argv[1])
