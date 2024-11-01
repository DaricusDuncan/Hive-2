import sys
sys.path.append('.')
from scripts.git_push import push_changes

def main():
    if push_changes():
        print("Success: Changes pushed to remote repository")
        return 0
    print("Error: Failed to push changes to remote repository")
    return 1

if __name__ == "__main__":
    sys.exit(main())
