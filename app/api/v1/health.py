from . import blueprint

@blueprint.route('/health', methods=['GET'])
def health():
    return {'status':'ok', 'version':'v1'}
