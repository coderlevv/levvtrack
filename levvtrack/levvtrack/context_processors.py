from levvtrack.version import VERSION

def app_version(request):
    return {"APP_VERSION": VERSION}