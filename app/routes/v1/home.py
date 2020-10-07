from starlette.responses import RedirectResponse

from .router_resolver import RouterResolver

router = RouterResolver().router


@router.get('/',
            responses={400: {'description': 'Bad Request'}},
            status_code=200)
async def home():
    return RedirectResponse(url="/swagger")
