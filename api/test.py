"""
Fichier de test pour diagnostiquer les problèmes Vercel
"""
def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': {'message': 'Test endpoint working', 'python_version': __import__('sys').version}
    }

