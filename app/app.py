import uvicorn
from absl import app, logging, flags
from fastapi import FastAPI
from routes import v1

FLAGS = flags.FLAGS
flags.DEFINE_integer('port', 8080, 'Port to bind uvicorn to.')
flags.DEFINE_boolean('debug', False, 'FastAPI(debug= <this flag>).')


def main(argv):
    print("*** FLAGS")
    print(FLAGS)

    fastapi_app = FastAPI(
        openapi_url='/openapi/spec.json',
        docs_url='/swagger',
        redoc_url='/redoc',
        debug=FLAGS.debug
    )

    @fastapi_app.on_event("startup")
    def startup() -> None:
        pass

    @fastapi_app.on_event("shutdown")
    def shutdown() -> None:
        pass

    fastapi_app.include_router(v1.RouterResolver().router, prefix='/api/v1')
    uvicorn.run(fastapi_app, host="0.0.0.0", port=FLAGS.port)


if __name__ == '__main__':
    logging.set_verbosity(logging.DEBUG)
    app.run(main)
