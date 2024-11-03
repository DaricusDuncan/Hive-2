import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app import create_app
from core.database import db
from models.user import User
from models.role import Role
from services.github import GitHubService
from urllib.parse import urlparse

def setup_test_user():
    """Create a test user with necessary roles"""
    app = create_app()
    with app.app_context():
        try:
            # Verify GitHub token
            if not os.environ.get('GITHUB_TOKEN'):
                print("Error: GITHUB_TOKEN environment variable is not set")
                return

            # Create user role if it doesn't exist
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                user_role = Role(name='user', description='Regular user role')
                db.session.add(user_role)
                db.session.commit()
                print("User role created successfully")

            # Create test user if it doesn't exist
            test_user = User.query.filter_by(username='test_github_user').first()
            if not test_user:
                test_user = User(
                    username='test_github_user',
                    email='test_github@example.com'
                )
                test_user.set_password('Test123!')
                test_user.roles.append(user_role)
                db.session.add(test_user)
                db.session.commit()
                print("Test user created successfully")
            else:
                print("Test user already exists")

            # Test GitHub repository analysis
            github_service = GitHubService()
            repo_url = "https://github.com/DaricusDuncan/Hive-2"
            
            try:
                # Parse repository URL
                parsed_url = urlparse(repo_url)
                path_parts = [p for p in parsed_url.path.split('/') if p]
                
                if len(path_parts) < 2:
                    print("Invalid repository URL format")
                    return
                
                owner, repo_name = path_parts[0], path_parts[1]
                print(f"\nAnalyzing repository: {owner}/{repo_name}")
                
                # Test repository access
                try:
                    repo = github_service.client.get_repo(f"{owner}/{repo_name}")
                    print(f"Successfully accessed repository: {repo.full_name}")
                except Exception as e:
                    print(f"Error accessing repository: {str(e)}")
                    return
                
                # Analyze repository issues
                issues = github_service.prioritize_issues(owner, repo_name)
                
                if issues:
                    print("\nRepository Analysis Results:")
                    print(f"Analyzed {len(issues)} issues")
                    for i, issue in enumerate(issues[:3], 1):  # Show top 3 issues
                        print(f"\nTop Issue #{i}:")
                        print(f"Number: #{issue['issue_number']}")
                        print(f"Title: {issue['title']}")
                        print(f"Complexity: {issue['complexity']}/10")
                        print(f"Score: {issue['score']}")
                        print(f"Implementation Time: {issue['implementation_time']} hours")
                        print(f"Security Impact: {issue['security_impact']}/10")
                        print(f"Performance Impact: {issue['performance_impact']}/10")
                else:
                    print("No open issues found in the repository")
                    
            except Exception as e:
                print(f"Error analyzing repository: {str(e)}")

        except Exception as e:
            print(f"Error in setup: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    setup_test_user()
