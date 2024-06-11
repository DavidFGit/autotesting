import gitlab

def create_commit(file_path, commit_message, file_content):
    # Configurar la conexión con GitLab
    gl = gitlab.Gitlab('http://gitlab.itauchile.cl/', private_token='HLJ7CwKKgRkqBk1KDZ9n')

    # Obtener el proyecto
    project = gl.projects.get('arq-devops-team/david-tests/poc-autotesting-gerais-local')

    # Obtener el archivo existente o crear uno nuevo
    try:
        file = project.files.get(file_path, ref='main')
        file.content = file_content
    except gitlab.exceptions.GitlabGetError:
        file = project.files.create({'file_path': file_path, 'branch': 'main', 'content': file_content, 'commit_message': 'Create file'})

    # Realizar el commit
    commit_data = {
        'branch': 'main',
        'commit_message': commit_message,
        'actions': [
            {
                'action': 'update',
                'file_path': file_path,
                'content': file_content
            }
        ]
    }
    commit = project.commits.create(commit_data)

    print(f"Commit realizado: {commit.id}")