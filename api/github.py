from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, current_user
from services.github import GitHubService
from core.rbac import role_required
from core.security import limiter
from urllib.parse import urlparse

github_ns = Namespace('github', description='GitHub API operations')

# Existing models...
repository_model = github_ns.model('Repository', {
    'name': fields.String(required=True, description='Repository name'),
    'description': fields.String(description='Repository description'),
    'private': fields.Boolean(default=False, description='Private repository flag')
})

repo_details_model = github_ns.model('RepositoryDetails', {
    'name': fields.String(),
    'description': fields.String(),
    'url': fields.String(),
    'stars': fields.Integer(),
    'forks': fields.Integer(),
    'language': fields.String(),
    'issues_count': fields.Integer(),
    'created_at': fields.DateTime(),
    'updated_at': fields.DateTime()
})

user_info_model = github_ns.model('GitHubUser', {
    'login': fields.String(),
    'name': fields.String(),
    'email': fields.String(),
    'public_repos': fields.Integer(),
    'followers': fields.Integer(),
    'following': fields.Integer()
})

issue_analysis_model = github_ns.model('IssueAnalysis', {
    'issue_number': fields.Integer(),
    'title': fields.String(),
    'complexity': fields.Float(),
    'security_impact': fields.Float(),
    'performance_impact': fields.Float(),
    'ux_impact': fields.Float(),
    'implementation_time': fields.Integer(),
    'state': fields.String(),
    'created_at': fields.DateTime(),
    'updated_at': fields.DateTime()
})

issue_dependency_model = github_ns.model('IssueDependency', {
    'issue_number': fields.Integer(),
    'title': fields.String(),
    'state': fields.String(),
    'created_at': fields.DateTime()
})

issue_dependencies_model = github_ns.model('IssueDependencies', {
    'issue_number': fields.Integer(),
    'dependencies': fields.List(fields.Nested(issue_dependency_model)),
    'dependency_count': fields.Integer()
})

prioritized_issue_model = github_ns.model('PrioritizedIssue', {
    'issue_number': fields.Integer(),
    'title': fields.String(),
    'complexity': fields.Float(),
    'security_impact': fields.Float(),
    'performance_impact': fields.Float(),
    'ux_impact': fields.Float(),
    'implementation_time': fields.Integer(),
    'score': fields.Float(),
    'state': fields.String(),
    'created_at': fields.DateTime(),
    'updated_at': fields.DateTime(),
    'dependencies': fields.List(fields.Nested(issue_dependency_model))
})

# New model for repository URL analysis request
repo_url_analysis_request = github_ns.model('RepoUrlAnalysisRequest', {
    'repository_url': fields.String(required=True, description='GitHub repository URL')
})

# Existing endpoints...
@github_ns.route('/user')
class GitHubUserInfo(Resource):
    @jwt_required()
    @github_ns.marshal_with(user_info_model)
    @github_ns.doc(security='Bearer')
    @limiter.limit("100/hour")
    def get(self):
        """Get GitHub user information for authenticated user"""
        github = GitHubService()
        return github.get_user_info()

@github_ns.route('/repositories')
class GitHubRepositories(Resource):
    @jwt_required()
    @github_ns.doc(security='Bearer')
    @limiter.limit("100/hour")
    def get(self):
        """List repositories for authenticated user"""
        github = GitHubService()
        return github.list_repositories()

@github_ns.route('/repositories/<string:username>')
class UserRepositories(Resource):
    @jwt_required()
    @github_ns.doc(security='Bearer')
    @limiter.limit("100/hour")
    def get(self, username):
        """List repositories for a specific user"""
        github = GitHubService()
        return github.list_repositories(username)

@github_ns.route('/repositories/create')
class CreateRepository(Resource):
    @jwt_required()
    @role_required('admin', 'moderator')
    @github_ns.expect(repository_model)
    @github_ns.doc(security='Bearer')
    @limiter.limit("10/hour")
    def post(self):
        """Create a new repository (Admin/Moderator only)"""
        data = github_ns.payload
        github = GitHubService()
        return github.create_repository(
            name=data['name'],
            description=data.get('description'),
            private=data.get('private', False)
        )

@github_ns.route('/repository/<string:owner>/<string:repo_name>')
class RepositoryDetails(Resource):
    @jwt_required()
    @github_ns.marshal_with(repo_details_model)
    @github_ns.doc(security='Bearer')
    @limiter.limit("100/hour")
    def get(self, owner, repo_name):
        """Get detailed information about a specific repository"""
        github = GitHubService()
        repo = github.get_repository(owner, repo_name)
        if not repo:
            github_ns.abort(404, f"Repository {owner}/{repo_name} not found")
        return repo

@github_ns.route('/repository/<string:owner>/<string:repo_name>/issue/<int:issue_number>/analysis')
class IssueAnalysis(Resource):
    @jwt_required()
    @github_ns.marshal_with(issue_analysis_model)
    @github_ns.doc(security='Bearer')
    @limiter.limit("50/hour")
    def get(self, owner, repo_name, issue_number):
        """Analyze a specific issue"""
        github = GitHubService()
        analysis = github.analyze_issue(owner, repo_name, issue_number)
        if not analysis:
            github_ns.abort(404, f"Issue {issue_number} not found or analysis failed")
        return analysis

@github_ns.route('/repository/<string:owner>/<string:repo_name>/issue/<int:issue_number>/dependencies')
class IssueDependencies(Resource):
    @jwt_required()
    @github_ns.marshal_with(issue_dependencies_model)
    @github_ns.doc(security='Bearer')
    @limiter.limit("50/hour")
    def get(self, owner, repo_name, issue_number):
        """Get dependencies for a specific issue"""
        github = GitHubService()
        dependencies = github.analyze_issue_dependencies(owner, repo_name, issue_number)
        if not dependencies:
            github_ns.abort(404, f"Issue {issue_number} not found or analysis failed")
        return dependencies

@github_ns.route('/repository/<string:owner>/<string:repo_name>/issues/prioritized')
class PrioritizedIssues(Resource):
    @jwt_required()
    @github_ns.marshal_list_with(prioritized_issue_model)
    @github_ns.doc(security='Bearer')
    @limiter.limit("20/hour")
    def get(self, owner, repo_name):
        """Get prioritized list of issues for a repository"""
        github = GitHubService()
        issues = github.prioritize_issues(owner, repo_name)
        if issues is None:
            github_ns.abort(404, f"Repository {owner}/{repo_name} not found or analysis failed")
        return issues

# New endpoint for repository URL analysis
@github_ns.route('/analyze')
class RepositoryURLAnalysis(Resource):
    @jwt_required()
    @github_ns.expect(repo_url_analysis_request)
    @github_ns.marshal_list_with(prioritized_issue_model)
    @github_ns.doc(security='Bearer')
    @limiter.limit("10/hour")
    def post(self):
        """Analyze issues from a GitHub repository URL"""
        data = github_ns.payload
        repo_url = data.get('repository_url')
        
        # Parse repository URL
        try:
            parsed_url = urlparse(repo_url)
            path_parts = [p for p in parsed_url.path.split('/') if p]
            
            if len(path_parts) < 2:
                github_ns.abort(400, "Invalid repository URL format")
            
            owner, repo_name = path_parts[0], path_parts[1]
            
            # Initialize GitHub service and analyze repository issues
            github = GitHubService()
            issues = github.prioritize_issues(owner, repo_name)
            
            if issues is None:
                github_ns.abort(404, f"Repository {owner}/{repo_name} not found or analysis failed")
            
            return issues
            
        except Exception as e:
            github_ns.abort(400, f"Error analyzing repository: {str(e)}")
