import logging
import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    accessToken = ''
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        accessToken = req_body.get('accessToken')

    if accessToken:
        return func.HttpResponse(
            json.dumps({"data": f"Access Token received as {accessToken}"}),
            status_code=200,
            mimetype="application/json"
        )
    else:
        return func.HttpResponse(
            json.dumps({"data": f"No token found"}),
            status_code=400,
            mimetype="application/json",
        )
