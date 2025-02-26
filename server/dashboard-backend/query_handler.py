from .controllers import base_device as base

def handle_query(request):
	print(request)

	return base.fetch_device(request, lambda x: x, )
