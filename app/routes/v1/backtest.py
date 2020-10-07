import pandas as pd
from contracts.v1.request import TargetDataFrame
from fastapi import HTTPException, Request
from fastquant import backtest
import traceback

from .router_resolver import RouterResolver

router = RouterResolver().router

def convert(val):
    constructors = [int, float, str]
    for c in constructors:
        try:
            return c(val)
        except ValueError:
            pass

@router.get('/backtest/{strategy}',
            responses={400: {'description': 'Bad Request'}},
            status_code=200)
async def do_backtest(strategy, payload: TargetDataFrame, request: Request):
    try:
        df = pd.DataFrame.from_dict(payload.columns)
        df = df.set_index(pd.DatetimeIndex(df.index))
    except Exception as error:
        raise HTTPException(
            status_code=400, detail=f'Dataframe serialization error: {error}')

    query_dict = {param: convert(val) for param, val in request.query_params._dict.items()}
    try:
        results = backtest(strategy=strategy, data=df.dropna(), plot=False, **query_dict)
    except Exception as error:
        raise HTTPException(status_code=500,
                             detail="".join(
                                 traceback.format_exception(
                                     etype=type(error), value=error, tb=error.__traceback__
                                 )))

    if query_dict.get('return_history', False):
        results, history = results

        return {"results": results.to_dict(),
                'history': {'orders': history['orders'].fillna('').to_dict(),
                            'periodic': history['periodic'].fillna('').to_dict()
                            }
                }
    else:
        return {"results": results.to_dict()
                }
